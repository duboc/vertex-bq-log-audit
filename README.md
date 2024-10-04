# Vertex AI Gemini Prompt Audit Logger

## Overview

This project provides a utility to log and audit prompts and responses from Google's Vertex AI Gemini model to BigQuery. It's designed to help track and analyze interactions with the AI model, providing valuable insights into usage patterns, response quality, and potential safety concerns.

## Why This Was Made

1. **Audit Trail**: Maintaining a comprehensive log of all interactions with the AI model is crucial for accountability and transparency.

2. **Performance Monitoring**: By tracking token usage and response metrics, we can optimize our use of the Gemini model and manage costs effectively.

3. **Safety Analysis**: The detailed logging of safety ratings allows for ongoing monitoring of content safety and helps identify potential issues.

4. **Insight Generation**: Storing structured data in BigQuery enables advanced analytics and reporting on AI model usage and performance.

5. **Compliance**: For organizations with strict data governance requirements, this logging system provides a robust audit mechanism.

6. **Continuous Improvement**: By analyzing past interactions, we can refine our prompts and improve the quality of AI-generated content over time.

## Features

- Logs prompts and responses from Vertex AI Gemini model to BigQuery
- Captures detailed metadata including:
  - Timestamp
  - Token counts
  - Safety ratings
  - Citations (if any)
  - Grounding metadata (for web search queries and chunks)
- Automatically creates the BigQuery table if it doesn't exist
- Handles structured nested data in BigQuery

## Prerequisites

- Google Cloud Project with Vertex AI and BigQuery enabled
- Python 3.7+
- Required Python packages: `google-cloud-bigquery`, `google-cloud-aiplatform`

## Setup

1. Set up Google Cloud credentials
2. Install required packages: `pip install google-cloud-bigquery google-cloud-aiplatform`
3. Update the `project`, `location`, `dataset_id`, and `table_id` variables in the script

## Usage

Run the script to log a sample interaction with the Gemini model:

```
python utils_vertex_bq_log.py
```

Customize the `prompt` variable to log different interactions.

## Future Enhancements

- Add error handling and retries for robustness
- Implement batch logging for improved performance
- Create a configuration file for easy customization
- Add unit tests for reliability

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Apachd 2.0](LICENSE)