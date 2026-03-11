"""
YouTube Channel Monitor + Transcriber for Agentic AI Pipeline
=============================================================
Monitors YouTube channels, pulls videos from the last 7 days,
and saves clean .md transcripts into your transcripts/ folder.

Two modes:
  1. YouTube Data API v3 (recommended for servers — set YOUTUBE_API_KEY in .env)
  2. yt-dlp fallback (no API key needed, may hit bot detection on cloud IPs)

Transcripts are fetched via yt-dlp subtitle download (handles IP blocks better
than youtube-transcript-api).

Usage:
  python transcribe.py                        # process all channels in urls.txt
  python transcribe.py <youtube_channel_url>  # single channel
  python transcribe.py <youtube_video_url>    # single video

Requirements:
  pip install yt-dlp google-api-python-client python-dotenv
"""

import sys
import os
import re
import json
import time
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Ensure deno is on PATH (for yt-dlp fallback) ────────────────────────────
_deno_bin = os.path.expanduser("~/.deno/bin")
if _deno_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _deno_bin + os.pathsep + os.environ.get("PATH", "")

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR      = Path(__file__).parent
TRANSCRIPTS_DIR = SCRIPT_DIR / "transcripts"
URLS_FILE       = SCRIPT_DIR / "urls.txt"
DAYS_BACK       = 7
MAX_VIDEOS_PER_CHANNEL = 5
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
RATE_LIMIT_DELAY = 2  # seconds between transcript fetches

# ── Helpers ───────────────────────────────────────────────────────────────────

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()[:80]


def is_channel_url(url: str) -> bool:
    return any(x in url for x in ["/@", "/c/", "/channel/", "/user/"])


def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else ""


def extract_channel_id_from_url(url: str) -> str:
    """Extract @handle or channel ID from URL for API lookup."""
    # /@handle format
    match = re.search(r"/@([^/\s?]+)", url)
    if match:
        return f"@{match.group(1)}"
    # /channel/UCxxx format
    match = re.search(r"/channel/([^/\s?]+)", url)
    if match:
        return match.group(1)
    return ""


# ── YouTube Data API v3 ──────────────────────────────────────────────────────

def _get_youtube_service():
    """Build YouTube Data API v3 client."""
    from googleapiclient.discovery import build
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def _resolve_channel_id(youtube, handle_or_id: str) -> str:
    """Resolve @handle to channel ID using forHandle parameter."""
    if handle_or_id.startswith("UC"):
        return handle_or_id  # Already a channel ID

    handle = handle_or_id.lstrip("@")
    resp = youtube.channels().list(
        part="id", forHandle=handle
    ).execute()

    items = resp.get("items", [])
    if items:
        return items[0]["id"]

    raise RuntimeError(f"Cannot resolve channel handle: @{handle}")


def get_channel_videos_api(channel_url: str) -> list:
    """Fetch recent videos using YouTube Data API v3."""
    youtube = _get_youtube_service()
    handle_or_id = extract_channel_id_from_url(channel_url)
    if not handle_or_id:
        raise RuntimeError(f"Cannot parse channel URL: {channel_url}")

    print(f"\n  Scanning channel (API): {channel_url}")

    channel_id = _resolve_channel_id(youtube, handle_or_id)
    cutoff = (datetime.utcnow() - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Search for recent videos from this channel
    videos = []
    next_page = None

    while True:
        resp = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            publishedAfter=cutoff,
            type="video",
            order="date",
            maxResults=min(MAX_VIDEOS_PER_CHANNEL, 50),
            pageToken=next_page,
        ).execute()

        for item in resp.get("items", []):
            snippet = item["snippet"]
            video_id = item["id"]["videoId"]
            pub_date = snippet.get("publishedAt", "")[:10].replace("-", "")
            videos.append({
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "video_id": video_id,
                "title": snippet.get("title", "Unknown"),
                "channel": snippet.get("channelTitle", "Unknown"),
                "upload_date": pub_date,
                "duration": "?",
            })

        if len(videos) >= MAX_VIDEOS_PER_CHANNEL:
            videos = videos[:MAX_VIDEOS_PER_CHANNEL]
            break
        next_page = resp.get("nextPageToken")
        if not next_page:
            break

    print(f"   Found {len(videos)} video(s) in the last {DAYS_BACK} days.")
    return videos


# ── yt-dlp fallback ──────────────────────────────────────────────────────────

def get_channel_videos_ytdlp(channel_url: str) -> list:
    """Fetch recent videos using yt-dlp flat-playlist (fallback)."""
    cutoff = (datetime.now() - timedelta(days=DAYS_BACK)).strftime("%Y%m%d")
    print(f"\n  Scanning channel (yt-dlp): {channel_url}")
    print(f"   Looking for videos since {cutoff} ({DAYS_BACK} days)...")

    result = subprocess.run(
        [
            "yt-dlp",
            "--dump-json",
            "--flat-playlist",
            "--dateafter", cutoff,
            "--yes-playlist",
            "--no-warnings",
            channel_url
        ],
        capture_output=True, text=True, encoding="utf-8",
        timeout=120,
    )

    videos = []
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            video_id = data.get("id") or ""
            if video_id:
                videos.append({
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "video_id": video_id,
                    "title": data.get("title", "Unknown"),
                    "channel": (data.get("playlist_uploader")
                                or data.get("uploader")
                                or "Unknown Channel"),
                    "upload_date": data.get("upload_date", ""),
                    "duration": data.get("duration_string")
                               or str(int(data.get("duration", 0) or 0)) + "s",
                })
        except json.JSONDecodeError:
            continue

    if len(videos) > MAX_VIDEOS_PER_CHANNEL:
        print(f"   Found {len(videos)} video(s), capping to {MAX_VIDEOS_PER_CHANNEL}.")
        videos = videos[:MAX_VIDEOS_PER_CHANNEL]
    else:
        print(f"   Found {len(videos)} video(s).")
    return videos


def get_channel_videos(channel_url: str) -> list:
    """Route to API or yt-dlp depending on available credentials."""
    if YOUTUBE_API_KEY:
        return get_channel_videos_api(channel_url)
    return get_channel_videos_ytdlp(channel_url)


# ── Transcript fetching ──────────────────────────────────────────────────────

def _parse_vtt(vtt_text: str) -> str:
    """Parse VTT subtitle content into plain text, removing duplicates."""
    lines = []
    seen = set()
    for line in vtt_text.splitlines():
        # Skip VTT header, timestamps, positioning tags, and blank lines
        if (not line.strip()
                or line.startswith("WEBVTT")
                or line.startswith("Kind:")
                or line.startswith("Language:")
                or line.startswith("NOTE")
                or re.match(r"^\d{2}:\d{2}", line)
                or re.match(r"^[\d\s]*$", line)):
            continue
        # Strip HTML tags (e.g. <c>, </c>, <00:01:02.345>)
        clean = re.sub(r"<[^>]+>", "", line).strip()
        if clean and clean not in seen:
            seen.add(clean)
            lines.append(clean)
    return " ".join(lines)


def fetch_transcript(video_id: str) -> str:
    """Fetch transcript using yt-dlp to download subtitles as VTT, then parse."""
    import tempfile

    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "subs")

        result = subprocess.run(
            [
                "yt-dlp",
                "--write-auto-sub",
                "--write-sub",
                "--sub-lang", "en",
                "--sub-format", "vtt",
                "--skip-download",
                "--no-warnings",
                "-o", output_template,
                url,
            ],
            capture_output=True, text=True, encoding="utf-8",
            timeout=120,
        )

        # Find the VTT file (could be subs.en.vtt or subs.en.*.vtt)
        vtt_files = list(Path(tmpdir).glob("*.vtt"))
        if not vtt_files:
            stderr = result.stderr.strip()[:200] if result.stderr else ""
            raise RuntimeError(
                f"No subtitles found for {video_id}. yt-dlp stderr: {stderr}"
            )

        # Prefer manually uploaded subs over auto-generated
        vtt_file = vtt_files[0]
        for f in vtt_files:
            if ".en." in f.name and ".en-orig" not in f.name:
                vtt_file = f
                break

        vtt_text = vtt_file.read_text(encoding="utf-8")
        transcript = _parse_vtt(vtt_text)

        if not transcript.strip():
            raise RuntimeError(f"Parsed transcript is empty for {video_id}")

        return transcript


# ── Tagging + Saving ─────────────────────────────────────────────────────────

def tag_transcript(title: str, transcript: str) -> str:
    text = (title + " " + transcript[:2000]).lower()
    tags = []
    if any(w in text for w in ["etsy", "template", "digital product", "canva", "listing", "design trend"]):
        tags.append("#PurpleOcaz")
    if any(w in text for w in ["saas", "churn", "retention", "b2b", "subscription", "customer success"]):
        tags.append("#ChurnShield")
    if any(w in text for w in ["ai agent", "claude", "llm", "automation", "n8n", "mcp", "agentic", "openai", "workflow"]):
        tags.append("#AgentLearning")
    if not tags:
        tags.append("#General")
    return " ".join(tags)


def save_transcript(meta: dict, transcript: str, method: str) -> Path:
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_title = sanitize_filename(meta["title"])
    filename = f"{date_str}_{safe_title}.md"
    out_path = TRANSCRIPTS_DIR / filename

    upload_date = meta.get("upload_date", "")
    if len(upload_date) == 8:
        upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"

    tags = tag_transcript(meta["title"], transcript)

    content = f"""# {meta['title']}

**Channel:** {meta['channel']}
**URL:** {meta['url']}
**Video ID:** {meta.get('video_id', '')}
**Published:** {upload_date}
**Duration:** {meta.get('duration', '?')}
**Transcribed:** {date_str} via {method}
**Tags:** {tags}

---

## Transcript

{transcript.strip()}

---

*Auto-generated for agentic AI context pipeline | {tags}*
"""
    out_path.write_text(content, encoding="utf-8")
    return out_path


def _already_transcribed(video_id: str) -> bool:
    if not TRANSCRIPTS_DIR.exists():
        return False
    for f in TRANSCRIPTS_DIR.glob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")[:500]
            if video_id in content:
                return True
        except Exception:
            continue
    return False


def transcribe_video(url: str, meta: dict = None) -> Path:
    """Full pipeline for a single video URL."""
    video_id = extract_video_id(url)
    if not video_id:
        raise RuntimeError(f"Cannot extract video ID from: {url}")

    if _already_transcribed(video_id):
        print(f"   Skipping (already transcribed): {video_id}")
        return None

    if meta is None:
        meta = {"url": url, "video_id": video_id, "title": "Unknown",
                "channel": "Unknown", "upload_date": "", "duration": "?"}
    meta["video_id"] = video_id

    print(f"\n  Processing: {meta['title'][:60]}")
    print(f"   Fetching transcript...")

    transcript = fetch_transcript(video_id)
    method = "yt-dlp-subtitles"

    word_count = len(transcript.split())
    print(f"   Got {word_count} words")

    out_path = save_transcript(meta, transcript, method)
    print(f"   Saved -> transcripts/{out_path.name}")
    return out_path


def load_channels() -> list:
    if not URLS_FILE.exists():
        print(f"ERROR: urls.txt not found at {URLS_FILE}")
        sys.exit(1)
    return [
        line.strip() for line in URLS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="YouTube Channel Monitor -> Transcript Pipeline"
    )
    parser.add_argument(
        "url", nargs="?",
        help="Single YouTube channel or video URL (omit to use urls.txt)"
    )
    args = parser.parse_args()

    mode = "YouTube Data API v3" if YOUTUBE_API_KEY else "yt-dlp (no API key)"
    print(f"[transcribe] Mode: {mode}")

    if args.url:
        sources = [args.url]
    else:
        sources = load_channels()
        print(f"[transcribe] Loaded {len(sources)} channel(s) from urls.txt")

    results = []
    errors  = []

    for source in sources:
        try:
            if is_channel_url(source):
                videos = get_channel_videos(source)
                if not videos:
                    print(f"   No new videos in the last {DAYS_BACK} days.")
                    continue
                for video in videos:
                    try:
                        path = transcribe_video(video["url"], meta=video)
                        if path:
                            results.append(path)
                        time.sleep(RATE_LIMIT_DELAY)
                    except Exception as e:
                        err_msg = str(e)[:120]
                        print(f"   FAILED: {video.get('title', '?')[:40]}: {err_msg}")
                        errors.append((video["url"], err_msg))
            else:
                path = transcribe_video(source)
                if path:
                    results.append(path)
        except Exception as e:
            err_msg = str(e)[:120]
            print(f"ERROR: {source}: {err_msg}")
            errors.append((source, err_msg))

    # Summary
    print(f"\n{'='*55}")
    print(f"Done! {len(results)} transcript(s) saved to transcripts/")
    if results:
        for r in results:
            print(f"   {r.name}")
    if errors:
        print(f"\n{len(errors)} failed:")
        for url, err in errors:
            print(f"   {url}: {err}")
    print(f"{'='*55}")


if __name__ == "__main__":
    main()
