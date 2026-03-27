"""
Export 3 pages of Canva design DAHD6ICQCWU and upload each to DO Spaces.
"""
import os
import sys
import time
import requests
import boto3
from botocore.client import Config
from dotenv import load_dotenv

# Load creds from the correct .env
load_dotenv('/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env')

DESIGN_ID = "DAHD6ICQCWU"
CANVA_API_BASE = "https://api.canva.com/rest/v1"
POLL_INTERVAL = 3
MAX_POLLS = 40

ACCESS_TOKEN = os.environ.get('CANVA_ACCESS_TOKEN', '').strip("'\"")
DO_KEY = os.environ.get('DO_SPACES_KEY')
DO_SECRET = os.environ.get('DO_SPACES_SECRET')
DO_BUCKET = os.environ.get('DO_SPACES_BUCKET', 'purpleocaz-assets')
DO_ENDPOINT = os.environ.get('DO_SPACES_ENDPOINT', 'https://lon1.digitaloceanspaces.com')

print(f"[init] Token starts with: {ACCESS_TOKEN[:20]}...")
print(f"[init] DO_SPACES_KEY: {DO_KEY}")
print(f"[init] DO_BUCKET: {DO_BUCKET}")

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json',
}

def export_page(page_number: int) -> str:
    """Export a single page of the design. Returns the download URL."""
    print(f"\n[export] Starting export for page {page_number}...")
    payload = {
        "design_id": DESIGN_ID,
        "format": {
            "type": "png",
            "export_quality": "pro",
            "pages": [page_number],
            "width": 3000
        }
    }
    resp = requests.post(f"{CANVA_API_BASE}/exports", json=payload, headers=headers)
    print(f"[export] POST /exports status: {resp.status_code}")
    if resp.status_code not in (200, 201):
        print(f"[export] ERROR: {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    job_id = data['job']['id']
    print(f"[export] Job ID: {job_id}")

    # Poll until done
    for i in range(MAX_POLLS):
        time.sleep(POLL_INTERVAL)
        poll_resp = requests.get(f"{CANVA_API_BASE}/exports/{job_id}", headers=headers)
        poll_data = poll_resp.json()
        status = poll_data['job']['status']
        print(f"[export] Poll {i+1}: status={status}")

        if status == 'success':
            urls = poll_data['job'].get('urls', [])
            if not urls:
                raise RuntimeError("Export succeeded but no URLs returned")
            download_url = urls[0]  # plain string per canva-client.ts
            print(f"[export] Page {page_number} download URL: {download_url[:80]}...")
            return download_url

        if status == 'failed':
            error = poll_data['job'].get('error', {})
            raise RuntimeError(f"Export failed: {error}")

    raise RuntimeError(f"Export timed out after {MAX_POLLS} polls")


def upload_to_spaces(download_url: str, page_number: int, timestamp: int) -> str:
    """Download from Canva URL and upload to DO Spaces. Returns CDN URL."""
    key = f"thumbnails/tattoo/business_card/listing_page{page_number}_{timestamp}.png"
    cdn_url = f"https://{DO_BUCKET}.lon1.digitaloceanspaces.com/{key}"

    print(f"\n[spaces] Downloading page {page_number} from Canva...")
    dl_resp = requests.get(download_url, timeout=120)
    dl_resp.raise_for_status()
    image_bytes = dl_resp.content
    print(f"[spaces] Downloaded {len(image_bytes):,} bytes")

    print(f"[spaces] Uploading to DO Spaces: {key}")
    s3 = boto3.client(
        's3',
        region_name='lon1',
        endpoint_url=DO_ENDPOINT,
        aws_access_key_id=DO_KEY,
        aws_secret_access_key=DO_SECRET,
        config=Config(signature_version='s3v4')
    )
    s3.put_object(
        Bucket=DO_BUCKET,
        Key=key,
        Body=image_bytes,
        ContentType='image/png',
        ACL='public-read'
    )
    print(f"[spaces] Upload complete: {cdn_url}")
    return cdn_url


def verify_url(cdn_url: str) -> bool:
    """Verify the CDN URL returns HTTP 200."""
    resp = requests.head(cdn_url, timeout=30)
    print(f"[verify] {cdn_url} → HTTP {resp.status_code}")
    return resp.status_code == 200


if __name__ == '__main__':
    timestamp = int(time.time() * 1000)
    results = []

    for page in [1, 2, 3]:
        try:
            download_url = export_page(page)
            cdn_url = upload_to_spaces(download_url, page, timestamp)
            ok = verify_url(cdn_url)
            results.append({'page': page, 'url': cdn_url, 'ok': ok})
        except Exception as e:
            print(f"[ERROR] Page {page} failed: {e}")
            results.append({'page': page, 'url': None, 'error': str(e)})

    print("\n" + "="*60)
    print("RESULTS:")
    for r in results:
        if r.get('url'):
            status = "OK" if r['ok'] else "FAIL"
            print(f"  Page {r['page']}: [{status}] {r['url']}")
        else:
            print(f"  Page {r['page']}: ERROR - {r.get('error')}")
    print("="*60)
