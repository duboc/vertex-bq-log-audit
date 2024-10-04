import os
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import bigquery
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Vertex AI
vertexai.init(
    project=os.getenv("VERTEX_PROJECT_ID"),
    location=os.getenv("VERTEX_LOCATION")
)

# Initialize BigQuery client
client = bigquery.Client(project=os.getenv("VERTEX_PROJECT_ID"))

# Set up BigQuery dataset and table
dataset_id = os.getenv("BQ_DATASET_ID", "gemini_audit")
table_id = os.getenv("BQ_TABLE_ID", "prompt_audit")
table_ref = client.dataset(dataset_id).table(table_id)

# Define schema for BigQuery table
schema = [
    bigquery.SchemaField("timestamp", "TIMESTAMP"),
    bigquery.SchemaField("prompt", "STRING"),
    bigquery.SchemaField("response", "STRING"),
    bigquery.SchemaField("prompt_token_count", "INTEGER"),
    bigquery.SchemaField("candidates_token_count", "INTEGER"),
    bigquery.SchemaField("total_token_count", "INTEGER"),
    bigquery.SchemaField("candidates", "RECORD", mode="REPEATED", fields=[
        bigquery.SchemaField("index", "INTEGER"),
        bigquery.SchemaField("finish_reason", "STRING"),
        bigquery.SchemaField("finish_message", "STRING"),
        bigquery.SchemaField("safety_ratings", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("category", "STRING"),
            bigquery.SchemaField("probability", "STRING"),
            bigquery.SchemaField("probability_score", "FLOAT"),
            bigquery.SchemaField("severity", "STRING"),
            bigquery.SchemaField("severity_score", "FLOAT"),
            bigquery.SchemaField("blocked", "BOOLEAN")
        ]),
        bigquery.SchemaField("citations", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("start_index", "INTEGER"),
            bigquery.SchemaField("end_index", "INTEGER"),
            bigquery.SchemaField("uri", "STRING"),
            bigquery.SchemaField("title", "STRING"),
            bigquery.SchemaField("license", "STRING"),
            bigquery.SchemaField("publication_date", "DATE")
        ]),
        bigquery.SchemaField("grounding_metadata", "RECORD", fields=[
            bigquery.SchemaField("web_search_queries", "STRING", mode="REPEATED"),
            bigquery.SchemaField("grounding_chunks", "RECORD", mode="REPEATED", fields=[
                bigquery.SchemaField("uri", "STRING"),
                bigquery.SchemaField("title", "STRING")
            ])
        ])
    ])
]

# Create the table if it doesn't exist
try:
    client.get_table(table_ref)
except Exception:
    table = bigquery.Table(table_ref, schema=schema)
    table = client.create_table(table)

model = GenerativeModel(os.getenv("VERTEX_MODEL_ID", "gemini-1.5-flash-002"))
prompt = "Write a story about a magic backpack."

response = model.generate_content(prompt)

def extract_safety_ratings(safety_ratings):
    return [
        {
            "category": rating.category,
            "probability": rating.probability,
            "probability_score": rating.probability_score,
            "severity": rating.severity,
            "severity_score": rating.severity_score,
            "blocked": rating.blocked
        } for rating in safety_ratings
    ]

row = {
    "timestamp": datetime.now(),
    "prompt": prompt,
    "response": response.text,
    "prompt_token_count": response.usage_metadata.prompt_token_count,
    "candidates_token_count": response.usage_metadata.candidates_token_count,
    "total_token_count": response.usage_metadata.total_token_count,
    "candidates": []
}

for candidate in response.candidates:
    candidate_data = {
        "index": candidate.index,
        "finish_reason": candidate.finish_reason,
        "finish_message": candidate.finish_message,
        "safety_ratings": extract_safety_ratings(candidate.safety_ratings),
        "citations": [],
        "grounding_metadata": {"web_search_queries": [], "grounding_chunks": []}
    }

    if candidate.citation_metadata:
        candidate_data["citations"] = [
            {
                "start_index": citation.start_index,
                "end_index": citation.end_index,
                "uri": citation.uri,
                "title": citation.title,
                "license": citation.license,
                "publication_date": citation.publication_date.date() if citation.publication_date else None
            } for citation in candidate.citation_metadata.citations
        ]

    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
        if candidate.grounding_metadata.web_search_queries:
            candidate_data["grounding_metadata"]["web_search_queries"] = candidate.grounding_metadata.web_search_queries
        if candidate.grounding_metadata.grounding_chunks:
            candidate_data["grounding_metadata"]["grounding_chunks"] = [
                {
                    "uri": chunk.web.uri if hasattr(chunk, 'web') else chunk.retrieved_context.uri,
                    "title": chunk.web.title if hasattr(chunk, 'web') else chunk.retrieved_context.title
                } for chunk in candidate.grounding_metadata.grounding_chunks
            ]

    row["candidates"].append(candidate_data)

# Insert the row into BigQuery
errors = client.insert_rows_json(table_ref, [row])
if errors:
    print(f"Encountered errors while inserting row: {errors}")
else:
    print("Row inserted successfully.")