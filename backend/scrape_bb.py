import time
from qdrant_client import QdrantClient
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import json
from bb_funcs import *
from qdrant_funcs import create_collection, prepare_data_for_qdrant, upsert_data_to_qdrant

link = "https://blackboard.kfupm.edu.sa/"

# Load .env variables (BB Username and Password)
load_dotenv()
username = os.getenv("NAME")
password = os.getenv("PASSWORD")
qdrant_key = os.getenv("QDRANT_KEY")
qdrant_url = os.getenv("QDRANT_url")
collection = 'announcements'

def scrape_upload_new_announcements(username, password, qdrant_key, model):

    # Part 1: Scrape Data and Save to file -------
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(link)

        try:
            login(page,username,password)
        except:
            print("An error occurred during login.")
            browser.close()

        course_links = extract_course_links(page)

        course_ids = [extract_id_from_link(course["href"]) for course in course_links if extract_id_from_link(course["href"])]

        announcement_urls = [
        f"https://blackboard.kfupm.edu.sa/webapps/blackboard/execute/announcement"
        f"?method=search&context=course_entry&course_id={course_id}"
        f"&handle=announcements_entry&mode=view"
        for course_id in course_ids
        ]

        all_announcements = []

        # Add announcements to the json file
        for course_id, url in zip(course_ids, announcement_urls):
            try:
                raw_text = scrape_announcement_text(page, url) # Assuming 'page' is defined
                cleaned_data = clean_announcement(raw_text,course_id_param=course_id, course_url_param=url)
                all_announcements.extend(cleaned_data)

                # To save after *each* course, keep it here. 
                with open("announcements.json", "w", encoding="utf-8") as f_json:
                    json.dump(all_announcements, f_json, ensure_ascii=False, indent=2)

            except Exception as e:
                print(f"Failed to Process URL {url}: {e}") 
                continue 

        time.sleep(1)
        browser.close()

    # Part 2: Upload Data to Qdrant -------

    # URL is for the 'Blackboard' cluster
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_key
    )

    # Makes the collection if it doesn't exist
    create_collection(client)

    #Prepare data points for qdrant
    points_to_insert = prepare_data_for_qdrant(client, "announcements.json", model)

    # Upload NEW data points to qdrant
    upsert_data_to_qdrant(client, points_to_insert)

#scrape_upload_new_announcements(username, password, qdrant_key, model=model)
# playwright codegen https://blackboard.kfupm.edu.sa/


