import re
import time
from dateutil import parser
import pytz

def login(page, username, password):

    # Fill the UserName box
    page.get_by_role("textbox", name="Username").type(username, delay=100);

    # Fill the Password box
    page.get_by_role("textbox", name="Password").type(password, delay=100); time.sleep(0.25)

    # Submit search
    page.get_by_role("button", name="Login").press("Enter")

    # Wait for page to load
    page.wait_for_load_state("networkidle")

    
def extract_course_links(page):
    """
    Returns a list of dicts for course links whose text starts with 3 digits and a dash.
    Each dict includes tag, text, and href from the JS filter.
    """
    with open(r"BlackboardProject\clickable_filter.js", "r", encoding="utf-8") as f:
        js_code = f.read()

    clickable_elements = page.eval_on_selector_all("*", js_code)

    course_links = [
        el for el in clickable_elements
        if el["tag"] == "A" and re.match(r"^\d{3}-", el["text"])
    ]

    if not course_links:
        print("No course links found.")
        exit()

    return course_links


def extract_id_from_link(link):
    """
    Given a full course URL string, extract the course_id value from the URL.
    """
    match = re.search(r"id=([^&]+)", link)
    return match.group(1) if match else None


def scrape_announcement_text(page, announcements_url):

    # Go to the announcements page
    page.goto(announcements_url, wait_until="networkidle")

    # Optional: wait in case of dynamic content
    page.wait_for_load_state('load')

    # Get all visible text content on the page
    text = page.inner_text("body")
    cleaned_text = "\n".join(line for line in text.splitlines() if line.strip())

    return cleaned_text


def parse_date_posted_to_timestamp(date_posted_str):
    # Parse without timezone using dateutil
    dt = parser.parse(date_posted_str, ignoretz=True)

    # Manually set the timezone to Arabian Standard Time (UTC+3)
    tz = pytz.timezone('Asia/Riyadh')
    dt_local = tz.localize(dt)

    # Convert to UTC and return timestamp
    dt_utc = dt_local.astimezone(pytz.UTC)
    return dt_utc.timestamp()


def clean_announcement(raw_text, course_id_param: str = None, course_url_param: str = None):
    lines = raw_text.splitlines()

    # Find "Institution" and start parsing from 3 lines after it
    try:
        inst_index = lines.index("Institution")
        lines = lines[inst_index + 3:]
    except ValueError:
        print("Could not find 'Institution' marker in text.")
        return []

    announcements = []
    current = {}
    buffer = []

    for line in lines:
        line = line.strip()
        if not current:
            current["title"] = line
            buffer = []
        elif line.startswith("Posted to:"):
            # Remove lines like "Posted by: ..."
            body_lines = [l for l in buffer if not l.startswith("Posted by:")]

            # First, prepare the full body content string outside the f-string
            full_body_content_string = '\n'.join(body_lines).strip()

            date_posted_str = None
            remaining_body_content = full_body_content_string

            # Check if there's content and extract the first line as date
            if full_body_content_string:
                temp_lines = full_body_content_string.splitlines()
                if temp_lines:
                    date_str_prefix = "Posted on: "
                    date_posted_str = temp_lines[0][len(date_str_prefix):].strip()
                    remaining_body_content = '\n'.join(temp_lines[1:]).strip()

            timestamp = parse_date_posted_to_timestamp(date_posted_str)
            combined_content = f"{current['title']}\n\n{remaining_body_content}"
            posted_to_value = line.replace("Posted to: ", "").strip()

            #Construct the dictionary
            final_announcement_data = {
                "id": str(f"{''.join(filter(str.isdigit, course_id_param))}{int(timestamp)}"),
                "course_id": course_id_param,  
                "timestamp": timestamp,
                "content": posted_to_value + " " + combined_content,
                "date_posted": date_posted_str,
                "posted_to": posted_to_value,
                "course_url": course_url_param, 
            }

            announcements.append(final_announcement_data)

            current = {}
        else:
            buffer.append(line)

    return announcements


# from qdrant_client import QdrantClient

# qdrant_client = QdrantClient(
#     url="https://7bc6eb6c-b639-4f2d-872b-a8221387ac60.europe-west3-0.gcp.cloud.qdrant.io:6333", 
#     api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.sPatmPoSjAcCEWYD0cxc40dUhEWUGytq5SH13WY1mzw",
# )

# print(qdrant_client.get_collections())