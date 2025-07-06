import json
from qdrant_client import models
from collections import defaultdict
from datetime import datetime
from typing import List, Optional
from qdrant_client import QdrantClient
#from scrape_bb import scrape_upload_new_announcements

def create_collection(client):
    "Create the announcements collection if it does not exist"
    if not client.collection_exists('announcements'):
        client.create_collection(
        collection_name="announcements",
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        on_disk_payload=True,  
        )
        client.create_payload_index(
            collection_name="announcements",
            field_name="course_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
        collection_name="announcements",
        field_name="timestamp",
        field_schema=models.PayloadSchemaType.FLOAT,
        )


def point_exists(client, collection_name, point_id):
    result = client.retrieve(
        collection_name=collection_name,
        ids=[point_id]
    )
    return len(result) > 0


def fetch_existing_ids(client, course_id):
    '''Return all announcement IDs for a given course ID.'''
    ids = set()
    scroll = client.scroll(
        collection_name="announcements",
        scroll_filter=models.Filter(
            must=[models.FieldCondition(key="course_id", match=models.MatchValue(value=course_id))]
        ),
        limit=10000
    )
    for point in scroll[0]:
        ids.add(point.id)
    return ids


def prepare_data_for_qdrant(client, filepath, model):
    "Prepares qdrant data points from a json file"

    with open(filepath, "r", encoding="utf-8") as f:
        announcements = json.load(f)

    points_to_insert = []

    # Group all announcementby course_id (optional but efficient)
    grouped = defaultdict(list)
    for ann in announcements:
        grouped[ann["course_id"]].append(ann)

    for course_id, items in grouped.items():
        existing_ids = fetch_existing_ids(client, course_id)

        for item in items:
            timestamp = item["timestamp"]
            point_id = int(item["id"])

            if point_id in existing_ids:
                continue  # Skip duplicates

            vector = model.encode(item["content"]).tolist()

            point = models.PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "course_id": course_id,
                    "timestamp": timestamp,
                    "content": item["content"],
                    "posted_to": item["posted_to"],
                    "course_url": item["course_url"],
                    "date_posted": item["date_posted"]
                }
            )
            points_to_insert.append(point)
    
    return points_to_insert


def upsert_data_to_qdrant(client, points_to_insert):
    "Upsert a json file with points to qdrant"
    if points_to_insert:
        client.upsert(
            collection_name="announcements",
            points=points_to_insert
        )
        print(f"Inserted {len(points_to_insert)} new announcements.")
    else:
        print("No new announcements to insert.")








