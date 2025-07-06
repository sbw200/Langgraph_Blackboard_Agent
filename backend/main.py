import os
import uuid
import uvicorn
import nest_asyncio
from pyngrok import ngrok
from fastapi import FastAPI, Request
from pydantic import BaseModel
from supervisor import get_graph 
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.tracers import LangChainTracer

from fastapi import FastAPI
from pydantic import BaseModel

tracer = LangChainTracer()

app = FastAPI()

chat_histories = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specific frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supervisor = get_graph()

class ChatRequest(BaseModel):
    message: str
    thread_id: str = None  

@app.get("/")
def home():
    return {"message": "LangGraph chatbot is live!"}

@app.post("/chat")
async def chat(req: ChatRequest):
    thread_id = req.thread_id or str(uuid.uuid4())

    user_message = {"role": "user", "content": req.message}

    full_history = []
    for chunk in supervisor.stream(
        {"messages": [user_message]},  # only latest message
        config={
            "configurable": {"thread_id": thread_id},
            "callbacks": [tracer],
        },
    ):
        full_history.append(chunk)

    final_message = full_history[-1]["supervisor"]["messages"] if full_history else []
    assistant_responses = [m.content for m in final_message if m.type == "ai"]
    assistant_response = assistant_responses[-1] if assistant_responses else "No response."

    return {
        "thread_id": thread_id,
        "response": assistant_response,
        "history": final_message,  
        "error": False, 
    }


# uvicorn main:app --reload --port 8000
# @app.post("/chat")
# async def chat(req: ChatRequest):
#     print("✅ /chat endpoint hit with message:", req.message)
#     thread_id = req.thread_id or str(uuid.uuid4())
#     # Stream full history
#     full_history = []
#     for chunk in supervisor.stream(
#         {
#             "messages": [{"role": "user", "content": req.message}]
#         },
#         config={"configurable": {"thread_id": thread_id}}
#     ):
#         full_history.append(chunk)
#     # You can change this to only return the final message if you want
#     final_message = full_history[-1]["supervisor"]["messages"] if full_history else []
#     return {"thread_id": thread_id, "messages": final_message}

# if __name__ == "__main__":
#     nest_asyncio.apply()  # For notebooks or environments like Jupyter
#     public_url = ngrok.connect(8000)
#     print("🚀 Public FastAPI endpoint:", public_url.public_url)
#     uvicorn.run(app, port=8000)
