"""
Save to Airtable Tool
======================
Sends articles to an Airtable table via the Airtable REST API.

Each article becomes one row in your Airtable table. The tool maps
our article fields to Airtable column names.

SETUP:
    1. Create a personal access token at https://airtable.com/create/tokens
       - Scope: data.records:write
       - Access: your specific base
    2. Add to .env:
           AIRTABLE_API_KEY=pat-xxxxx
           AIRTABLE_BASE_ID=appxxxxx
           AIRTABLE_TABLE_NAME=AI News

AIRTABLE API BASICS:
    - Endpoint: POST https://api.airtable.com/v0/{base_id}/{table_name}
    - Auth: Bearer token in header
    - Body: {"records": [{"fields": {"Title": "...", ...}}]}
    - Limit: 10 records per request (we batch automatically)
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from lib.orchestrator.base_tool import BaseTool

# Airtable API limits to 10 records per POST request
AIRTABLE_BATCH_SIZE = 10


class SaveToAirtableTool(BaseTool):
    """Saves a list of articles to an Airtable table."""

    def execute(self, **kwargs) -> dict:
        """
        Send articles to Airtable.

        Args:
            articles (list): List of article dicts from FilterRecentTool.
            api_key (str): Airtable personal access token.
            base_id (str): Airtable base ID (starts with "app").
            table_name (str): Name of the table in your base.

        Returns:
            Standard tool result dict. On success, 'data' contains:
                - saved_count: how many articles were saved
                - batch_results: response from each API call
        """
        import requests

        try:
            articles = kwargs.get('articles', [])
            api_key = kwargs.get('api_key', '')
            base_id = kwargs.get('base_id', '')
            table_name = kwargs.get('table_name', '')

            # ── Validate credentials ──
            if not api_key:
                return {
                    'success': False,
                    'data': None,
                    'error': (
                        "No Airtable API key. "
                        "Add AIRTABLE_API_KEY to your .env file. "
                        "Get one at: https://airtable.com/create/tokens"
                    ),
                    'tool_name': self.get_name(),
                    'metadata': {'reason': 'missing_api_key'}
                }

            if not base_id:
                return {
                    'success': False,
                    'data': None,
                    'error': (
                        "No Airtable base ID. "
                        "Add AIRTABLE_BASE_ID to your .env file. "
                        "Find it in your Airtable URL: airtable.com/appXXXXX/..."
                    ),
                    'tool_name': self.get_name(),
                    'metadata': {'reason': 'missing_base_id'}
                }

            if not articles:
                return {
                    'success': True,
                    'data': {'saved_count': 0, 'batch_results': []},
                    'error': None,
                    'tool_name': self.get_name(),
                    'metadata': {'reason': 'no_articles_to_save'}
                }

            # ── Build the API request ──
            url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # ── Send articles in batches of 10 (Airtable's limit) ──
            saved_count = 0
            batch_results = []
            errors = []

            for i in range(0, len(articles), AIRTABLE_BATCH_SIZE):
                batch = articles[i:i + AIRTABLE_BATCH_SIZE]

                # Map our article fields to Airtable column names
                records = []
                for article in batch:
                    records.append({
                        "fields": {
                            "Title": article.get('title', ''),
                            "URL": article.get('url', ''),
                            "Published": article.get('published', ''),
                            "Description": article.get('description', ''),
                            "Source": article.get('source', ''),
                            "Fetched At": datetime.utcnow().isoformat(),
                        }
                    })

                # POST to Airtable
                response = requests.post(
                    url,
                    headers=headers,
                    json={"records": records},
                    timeout=30,
                )

                if response.status_code == 200:
                    result = response.json()
                    created = len(result.get('records', []))
                    saved_count += created
                    batch_results.append({
                        'batch': i // AIRTABLE_BATCH_SIZE + 1,
                        'sent': len(batch),
                        'created': created,
                        'status': response.status_code,
                    })
                else:
                    # Airtable returned an error
                    error_body = response.text[:500]
                    errors.append(
                        f"Batch {i // AIRTABLE_BATCH_SIZE + 1} failed "
                        f"(HTTP {response.status_code}): {error_body}"
                    )
                    batch_results.append({
                        'batch': i // AIRTABLE_BATCH_SIZE + 1,
                        'sent': len(batch),
                        'created': 0,
                        'status': response.status_code,
                        'error': error_body,
                    })

            # ── Return results ──
            if errors:
                return {
                    'success': False,
                    'data': {
                        'saved_count': saved_count,
                        'batch_results': batch_results,
                    },
                    'error': "; ".join(errors),
                    'tool_name': self.get_name(),
                    'metadata': {
                        'total_articles': len(articles),
                        'saved_count': saved_count,
                        'error_count': len(errors),
                    }
                }

            return {
                'success': True,
                'data': {
                    'saved_count': saved_count,
                    'batch_results': batch_results,
                },
                'error': None,
                'tool_name': self.get_name(),
                'metadata': {
                    'total_articles': len(articles),
                    'saved_count': saved_count,
                    'batches_sent': len(batch_results),
                }
            }

        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e),
                'tool_name': self.get_name(),
                'metadata': {'exception_type': type(e).__name__}
            }
