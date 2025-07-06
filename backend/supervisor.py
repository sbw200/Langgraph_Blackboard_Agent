import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union

import yaml
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import convert_to_messages
from langchain_mistralai import ChatMistralAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from pydantic import Field
from qdrant_client import QdrantClient
from qdrant_client.models import (FieldCondition, Filter, MatchAny, MatchValue,Range)
from sentence_transformers import SentenceTransformer
from langgraph.checkpoint.memory import MemorySaver
from langgraph_supervisor import create_supervisor
from langchain_tavily import TavilySearch


from scrape_bb import scrape_upload_new_announcements


load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise ValueError("Environment variables not set.")
qdrant_key = os.getenv("QDRANT_KEY")
qdrant_url = os.getenv("QDRANT_url")

model = SentenceTransformer("all-MiniLM-L6-v2")

with open(r"C:\Users\SAADB\Desktop\Code\BlackboardProject\backend\prompts.yaml", "r") as f:
    prompts = yaml.safe_load(f)

ANNOUNCEMENT_PROMPT = prompts["announcement_agent_prompt"]
CALENDAR_PROMPT = prompts["calendar_agent_prompt"]
SEARCH_PROMPT = prompts["web_search_agent_prompt"]
SUPERVISOR_PROMPT = prompts["supervisor_prompt"]

LANGSMITH_TRACING=True
os.environ["LANGCHAIN_TRACING_V2"] = "true"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY=os.getenv("LANGSMITH_API_KEY")
project_name="BBChat"
os.environ["LANGCHAIN_PROJECT"] = project_name
MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY")

client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_key,
)

manager_llm = ChatMistralAI(
    mistral_api_key=MISTRAL_API_KEY, model="mistral-medium-latest", temperature=1
)
worker_llm = ChatMistralAI(
    mistral_api_key=MISTRAL_API_KEY, model="mistral-medium-latest", temperature=1
)

web_search = TavilySearch(api_key=TAVILY_API_KEY)

def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")


research_agent = create_react_agent(
    model=worker_llm,
    tools=[web_search],
    prompt=(
        "You are a research agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with research-related tasks, DO NOT do any math\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="research_agent",
)


_model_cache = {}

def embed_query(
    texts: Union[str, List[str]],
    model: Optional[SentenceTransformer] = None,
    model_name: str = "all-MiniLM-L6-v2",
    normalize: bool = True,
) -> Union[List[float], List[List[float]]]:
    global _model_cache

    if model is None:
        if model_name not in _model_cache:
            _model_cache[model_name] = SentenceTransformer(model_name)
        model = _model_cache[model_name]

    if isinstance(texts, str):
        return model.encode(texts, normalize_embeddings=normalize).tolist()
    return model.encode(texts, normalize_embeddings=normalize).tolist()


def get_announcements_by_courses(
    client: QdrantClient,
    course_ids: Optional[List[str]] = None,
    query_text: Optional[str] = None,
    mode: str = "hybrid",  # "recent_only", "semantic_only", or "hybrid"
    time_window_days: Optional[int] = None,
    now: Optional[datetime] = None,
    limit: int = 10000,
    k_per_course: Optional[int] = 5,
    username: Optional[str] = None,
    password: Optional[str] = None,
    qdrant_key: Optional[str] = None,
) -> List[dict]:

    if username and password and qdrant_key:
        scrape_upload_new_announcements(username, password, qdrant_key, model)

    now = now or datetime.utcnow()
    timestamp_now = now.timestamp()
    earliest_timestamp = None
    if time_window_days is not None:
        earliest_timestamp = timestamp_now - (time_window_days * 86400)

    def scroll_recent():
        results = []
        for course_id in course_ids:
            must_conditions = [
                FieldCondition(key="course_id", match=MatchValue(value=course_id))
            ]
            if earliest_timestamp:
                must_conditions.append(
                    FieldCondition(
                        key="timestamp",
                        range=Range(gte=earliest_timestamp, lte=timestamp_now),
                    )
                )
            response, _ = client.scroll(
                collection_name="announcements",
                scroll_filter=Filter(must=must_conditions),
                limit=k_per_course,
                with_payload=True,
                with_vectors=False,
            )
            course_announcements = [pt.payload for pt in response]
            course_announcements.sort(key=lambda a: a.get("timestamp", 0), reverse=True)
            results.extend(course_announcements)
        return results

    def search_semantic():
        if not query_text:
            return []
        query_vector = embed_query(query_text, model)
        must_conditions = []
        if course_ids:
            must_conditions.append(
                FieldCondition(key="course_id", match=MatchAny(any=course_ids))
            )
        if earliest_timestamp:
            must_conditions.append(
                FieldCondition(
                    key="timestamp",
                    range=Range(gte=earliest_timestamp, lte=timestamp_now),
                )
            )

        search_results = client.search(
            collection_name="announcements",
            query_vector=query_vector,
            limit=limit,
            query_filter=Filter(must=must_conditions) if must_conditions else None,
            with_payload=True,
            with_vectors=False,
        )
        announcements = [r.payload for r in search_results]
        announcements.sort(key=lambda a: a.get("timestamp", 0), reverse=True)
        return announcements

    if mode == "recent_only":
        return scroll_recent()
    elif mode == "semantic_only":
        return search_semantic()
    elif mode == "hybrid":
        semantic_hits = search_semantic()
        if semantic_hits:
            return semantic_hits
        return scroll_recent()
    else:
        raise ValueError(f"Unknown mode: {mode}")

@tool(description="Get the most recent announcement for a specific course by course_id.")
def search_announcements(
    course_ids: Optional[List[str]] = None,
    time_window_days: int = 20,
    k_per_course: int = 5,
    query_text: Optional[str] = None,
    mode: str = "recent_only",
) -> Tuple[str, str]:
    """Search and summarize course announcements (quizzes, deadlines, etc.).

    Modes:
    - 'recent_only': Fetch most recent announcements.
    - 'semantic_only': Return announcements semantically matching `query_text`.
    - 'hybrid': Try semantic first, fallback to recent if empty.
    """

    if course_ids == None:
        if mode == "recent_only":
            course_ids = []

    announcements = get_announcements_by_courses(
        client=client,
        course_ids=course_ids,
        time_window_days=time_window_days,
        k_per_course=k_per_course,
        query_text=query_text,
        mode=mode,
        now=datetime.now(timezone.utc),
    )

    if not announcements:
        return (
            "📭 No recent announcements found.",
            "📭 No recent announcements found.",
        )

    summaries = []
    for ann in announcements:
        course = ann.get("posted_to", "Unknown Course")
        content = ann.get("content", "").strip().replace("\n", " ")
        date = ann.get("date_posted", "Unknown Date")
        summary = f"🔔 **{course}** ({date}):\n{content[:300]}{'...' if len(content) > 300 else ''}"
        summaries.append(summary)

    formatted = "\n\n".join(summaries)
    return (formatted, json.dumps(announcements, ensure_ascii=False, indent=2))


announcement_agent = create_react_agent(
    model=worker_llm,
    tools=[search_announcements],
    prompt=(ANNOUNCEMENT_PROMPT),
    name="announcement_agent",
)

checkpointer = MemorySaver()

supervisor = create_supervisor(
    model=worker_llm,
    agents=[research_agent, announcement_agent],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "- a research agent. Assign web search tasks to this agent\n"
        "- an announcement agent. Ask ONLY this agent for course related queries like assignments/quizzes/exams/info."
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself except answering basic questions."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile(checkpointer=checkpointer)


def get_graph():
    return supervisor


# for chunk in supervisor.stream(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "When was the final for course id '_105953_1'? Check the past 3 months",
#             }
#         ]
#     },
#     config={
#         "configurable": {
#             "thread_id": str(uuid.uuid4())  # or reuse a fixed one for session persistence
#         }
#     }
# ):
#     pretty_print_messages(chunk, last_message=True)

# final_message_history = chunk["supervisor"]["messages"]
