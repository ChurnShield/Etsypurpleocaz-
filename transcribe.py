"""
YouTube Channel Monitor + Transcriber for Agentic AI Pipeline
=============================================================
Monitors YouTube channels, pulls videos from the last 7 days,
and saves clean .md transcripts into your transcripts/ folder.

Usage:
  python transcribe.py                        # process all channels in urls.txt
  python transcribe.py <youtube_channel_url>  # single channel
  python transcribe.py <youtube_video_url>    # single video

Requirements (install once in PowerShell):
  pip install yt-dlp openai-whisper
  winget install ffmpeg
"""

import sys
import os
import re
import json
import subprocess
import argparse
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR      = Path(__file__).parent
TRANSCRIPTS_DIR = SCRIPT_DIR / "transcripts"
URLS_FILE       = SCRIPT_DIR / "urls.txt"
WHISPER_MODEL   = "base"   # tiny | base | small | medium | large
DAYS_BACK       = 7        # only transcribe videos published within this many days

# ── Helpers ───────────────────────────────────────────────────────────────────

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()[:80]


def is_channel_url(url: str) -> bool:
    return any(x in url for x in ["/@", "/c/", "/channel/", "/user/"])


def get_cutoff_date() -> str:
    """Return date string N days ago in yt-dlp format YYYYMMDD."""
    cutoff = datetime.now() - timedelta(days=DAYS_BACK)
    return cutoff.strftime("%Y%m%d")


def get_channel_videos(channel_url: str) -> list:
    """
    Fetch metadata for all videos published in the last DAYS_BACK days
    from a YouTube channel. Returns list of video metadata dicts.
    """
    cutoff = get_cutoff_date()
    print(f"\n📡 Scanning channel: {channel_url}")
    print(f"   Looking for videos published since {cutoff} ({DAYS_BACK} days)...")

    result = subprocess.run(
        [
            "yt-dlp",
            "--dump-json",
            "--flat-playlist",
            "--dateafter", cutoff,
            "--yes-playlist",
            channel_url
        ],
        capture_output=True, text=True, encoding="utf-8"
    )

    videos = []
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            video_id = data.get("id") or data.get("url", "").split("v=")[-1]
            if video_id:
                videos.append({
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "title": data.get("title", "Unknown"),
                    "upload_date": data.get("upload_date", ""),
                })
        except json.JSONDecodeError:
            continue

    print(f"   Found {len(videos)} video(s) in the last {DAYS_BACK} days.")
    return videos


def get_video_metadata(url: str) -> dict:
    print(f"  → Fetching metadata...")
    result = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-playlist", url],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp metadata failed: {result.stderr[:200]}")
    data = json.loads(result.stdout)
    return {
        "title":       data.get("title", "Unknown Title"),
        "channel":     data.get("uploader", "Unknown Channel"),
        "duration":    data.get("duration_string", "?"),
        "upload_date": data.get("upload_date", ""),
        "url":         url,
        "video_id":    data.get("id", ""),
    }


def try_captions(url: str, out_dir: Path):
    print(f"  → Trying YouTube captions...")
    subprocess.run(
        [
            "yt-dlp",
            "--write-auto-sub", "--write-sub",
            "--sub-lang", "en",
            "--sub-format", "vtt",
            "--skip-download",
            "--no-playlist",
            "-o", str(out_dir / "captions"),
            url
        ],
        capture_output=True, text=True, encoding="utf-8"
    )
    vtt_files = list(out_dir.glob("*.vtt"))
    if not vtt_files:
        print(f"  → No captions found, falling back to Whisper...")
        return None
    print(f"  → Captions found!")
    return clean_vtt(vtt_files[0].read_text(encoding="utf-8"))


def clean_vtt(vtt_text: str) -> str:
    lines = []
    seen = set()
    for line in vtt_text.splitlines():
        if (line.startswith("WEBVTT") or
                "-->" in line or
                re.match(r"^\d+$", line.strip()) or
                line.strip() == ""):
            continue
        clean = re.sub(r"<[^>]+>", "", line).strip()
        if clean and clean not in seen:
            seen.add(clean)
            lines.append(clean)
    return " ".join(lines)


def try_whisper(url: str, out_dir: Path) -> str:
    print(f"  → Downloading audio for Whisper (this may take a moment)...")
    audio_path = out_dir / "audio.mp3"
    dl = subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "mp3", "--no-playlist",
         "-o", str(audio_path), url],
        capture_output=True, text=True, encoding="utf-8"
    )
    if dl.returncode != 0:
        raise RuntimeError(f"Audio download failed: {dl.stderr[:200]}")

    audio_files = (list(out_dir.glob("*.mp3")) +
                   list(out_dir.glob("*.m4a")) +
                   list(out_dir.glob("*.webm")))
    if not audio_files:
        raise RuntimeError("No audio file found after download.")

    print(f"  → Running Whisper ({WHISPER_MODEL})... (1-2 mins for a typical video)")
    import whisper
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(str(audio_files[0]))
    return result["text"]


def tag_transcript(title: str, transcript: str) -> str:
    """Auto-tag transcript by likely use case for agent context."""
    text = (title + " " + transcript).lower()
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

    upload_date = meta["upload_date"]
    if len(upload_date) == 8:
        upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"

    tags = tag_transcript(meta["title"], transcript)

    content = f"""# {meta['title']}

**Channel:** {meta['channel']}  
**URL:** {meta['url']}  
**Published:** {upload_date}  
**Duration:** {meta['duration']}  
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


def transcribe_video(url: str) -> Path:
    """Full pipeline for a single video URL."""
    print(f"\n🎬 Processing: {url}")
    tmp_dir = SCRIPT_DIR / ".tmp_transcribe"
    tmp_dir.mkdir(exist_ok=True)
    try:
        meta = get_video_metadata(url)
        print(f"  Title:   {meta['title']}")
        print(f"  Channel: {meta['channel']}")

        transcript = try_captions(url, tmp_dir)
        method = "YouTube captions"
        if not transcript:
            transcript = try_whisper(url, tmp_dir)
            method = f"Whisper ({WHISPER_MODEL})"

        out_path = save_transcript(meta, transcript, method)
        print(f"  ✅ Saved → transcripts/{out_path.name}")
        return out_path
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def load_channels() -> list:
    """Read channel URLs from urls.txt."""
    if not URLS_FILE.exists():
        print(f"❌ urls.txt not found at {URLS_FILE}")
        print("   Create it in Notepad with one YouTube channel URL per line.")
        sys.exit(1)
    channels = [
        line.strip() for line in URLS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    return channels


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="YouTube Channel Monitor → Transcript Pipeline"
    )
    parser.add_argument(
        "url", nargs="?",
        help="Single YouTube channel or video URL (omit to use urls.txt)"
    )
    args = parser.parse_args()

    # Determine sources
    if args.url:
        sources = [args.url]
    else:
        sources = load_channels()
        print(f"📋 Loaded {len(sources)} channel(s) from urls.txt")

    results = []
    errors  = []

    for source in sources:
        try:
            if is_channel_url(source):
                videos = get_channel_videos(source)
                if not videos:
                    print(f"  ℹ️  No new videos in the last {DAYS_BACK} days.")
                    continue
                for video in videos:
                    try:
                        path = transcribe_video(video["url"])
                        results.append(path)
                    except Exception as e:
                        print(f"  ❌ Failed: {video['url']}\n     {e}")
                        errors.append((video["url"], str(e)))
            else:
                # Direct video URL
                path = transcribe_video(source)
                results.append(path)
        except Exception as e:
            print(f"❌ Error processing {source}: {e}")
            errors.append((source, str(e)))

    # Summary
    print(f"\n{'='*55}")
    print(f"✅ Done! {len(results)} transcript(s) saved to /transcripts/")
    if results:
        for r in results:
            print(f"   📄 {r.name}")
    if errors:
        print(f"\n❌ {len(errors)} failed:")
        for url, err in errors:
            print(f"   {url}: {err}")
    print(f"{'='*55}")
    print(f"\n💡 Your agent will auto-load these next Claude Code session.")


if __name__ == "__main__":
    main()
