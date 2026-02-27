import json
import os
import sys
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv

load_dotenv()

ES_URL = os.environ.get("ELASTICSEARCH_URL")
ES_API_KEY = os.environ.get("ELASTICSEARCH_API_KEY")

if not ES_URL or not ES_API_KEY:
    print("Error: ELASTICSEARCH_URL and ELASTICSEARCH_API_KEY must be set in .env")
    sys.exit(1)

client = Elasticsearch(
    ES_URL,
    api_key=ES_API_KEY
)

LOGS_INDEX = "server-logs-mock"
TICKETS_INDEX = "incident-tickets-mock"

def create_indices():
    # Define mapping for logs
    if not client.indices.exists(index=LOGS_INDEX):
        print(f"Creating index {LOGS_INDEX}...")
        client.indices.create(
            index=LOGS_INDEX,
            mappings={
                "properties": {
                    "@timestamp": {"type": "date"},
                    "service": {"type": "keyword"},
                    "message": {"type": "text"},
                    "level": {"type": "keyword"},
                    "status_code": {"type": "integer"},
                    "latency_ms": {"type": "integer"}
                }
            }
        )
    else:
        print(f"Index {LOGS_INDEX} already exists")

    # Define mapping for tickets (with text fields optimized for later semantic search if desired via Agent Builder)
    if not client.indices.exists(index=TICKETS_INDEX):
         print(f"Creating index {TICKETS_INDEX}...")
         client.indices.create(
            index=TICKETS_INDEX,
            mappings={
                "properties": {
                    "ticket_id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "root_cause": {"type": "text"},
                    "resolution": {"type": "text"},
                    "tags": {"type": "keyword"}
                }
            }
        )
    else:
         print(f"Index {TICKETS_INDEX} already exists")


def ingest_data():
    # Ingest logs
    try:
        with open("mock_logs.json", "r") as f:
            logs = json.load(f)
            
        actions = [
            {
                "_index": LOGS_INDEX,
                "_source": log
            }
            for log in logs
        ]
        
        helpers.bulk(client, actions)
        print(f"Successfully ingested {len(logs)} logs to {LOGS_INDEX}")
    except FileNotFoundError:
        print("mock_logs.json not found. Run generate_logs.py first.")

    # Ingest tickets
    try:
        with open("mock_tickets.json", "r") as f:
            tickets = json.load(f)
            
        actions = [
            {
                "_index": TICKETS_INDEX,
                "_source": ticket
            }
            for ticket in tickets
        ]
        
        helpers.bulk(client, actions)
        print(f"Successfully ingested {len(tickets)} tickets to {TICKETS_INDEX}")
    except FileNotFoundError:
         print("mock_tickets.json not found. Run generate_tickets.py first.")


if __name__ == "__main__":
    print("Testing connection to Elasticsearch...")
    try:
        info = client.info()
        print(f"Connected to cluster: {info['cluster_name']}")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)
        
    create_indices()
    ingest_data()
    print("Done!")
