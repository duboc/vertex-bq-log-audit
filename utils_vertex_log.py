import vertexai
from vertexai.generative_models import GenerativeModel
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()

# Set up logging
logging.basicConfig(filename='gemini_api_log.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_dict(title, data):
    logging.info(f"{title}:\n{json.dumps(data, indent=2, default=str)}")

vertexai.init(
    project=os.getenv("VERTEX_PROJECT_ID"),
    location=os.getenv("VERTEX_LOCATION")
)

model = GenerativeModel("gemini-1.5-flash-002")
prompt = "Write a story about a magic backpack."

# Log input
logging.info(f"Input Prompt: {prompt}")

response = model.generate_content(prompt)

# Function to extract safety ratings
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

# Log output
logging.info("Generated Content:")
logging.info(response.text)

# Log metadata
log_dict("Metadata", {
    "Prompt Token Count": response.usage_metadata.prompt_token_count,
    "Candidates Token Count": response.usage_metadata.candidates_token_count,
    "Total Token Count": response.usage_metadata.total_token_count
})

for i, candidate in enumerate(response.candidates):
    candidate_data = {
        "Index": candidate.index,
        "Finish Reason": candidate.finish_reason,
        "Finish Message": candidate.finish_message,
        "Safety Ratings": extract_safety_ratings(candidate.safety_ratings)
    }

    if candidate.citation_metadata:
        candidate_data["Citations"] = [
            {
                "Start Index": citation.start_index,
                "End Index": citation.end_index,
                "URI": citation.uri,
                "Title": citation.title,
                "License": citation.license,
                "Publication Date": f"{citation.publication_date.year}-{citation.publication_date.month}-{citation.publication_date.day}" if citation.publication_date else None
            } for citation in candidate.citation_metadata.citations
        ]

    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
        grounding_data = {}
        if candidate.grounding_metadata.web_search_queries:
            grounding_data["Web Search Queries"] = candidate.grounding_metadata.web_search_queries
        if candidate.grounding_metadata.grounding_chunks:
            grounding_data["Grounding Chunks"] = [
                {
                    "URI": chunk.web.uri if hasattr(chunk, 'web') else chunk.retrieved_context.uri,
                    "Title": chunk.web.title if hasattr(chunk, 'web') else chunk.retrieved_context.title
                } for chunk in candidate.grounding_metadata.grounding_chunks
            ]
        candidate_data["Grounding Metadata"] = grounding_data

    log_dict(f"Candidate {i + 1}", candidate_data)

# Print to console that logging is complete
print("Logging complete. Check gemini_api_log.log for details.")