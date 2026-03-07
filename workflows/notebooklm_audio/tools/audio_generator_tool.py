# =============================================================================
# workflows/notebooklm_audio/tools/audio_generator_tool.py
#
# Phase 2: Generates Audio Overviews from NotebookLM notebooks.
# Triggers the audio generation, polls for completion, and downloads
# the resulting audio files for packaging as digital products.
# =============================================================================

import json
import subprocess
import time
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool


class AudioGeneratorTool(BaseTool):
    """Generates Audio Overviews from NotebookLM notebooks.

    Uses the nlm CLI to trigger audio generation, poll status,
    and download completed audio files.
    """

    # Maximum time to wait for audio generation (5 minutes)
    AUDIO_GENERATION_TIMEOUT = 300
    POLL_INTERVAL = 15

    def execute(self, **kwargs) -> dict:
        notebooks = kwargs.get("notebooks", [])
        export_dir = kwargs.get("export_dir", "")

        if not notebooks:
            return {
                "success": False,
                "data": None,
                "error": "No notebooks provided for audio generation",
                "tool_name": self.get_name(),
                "metadata": {},
            }

        if not export_dir:
            return {
                "success": False,
                "data": None,
                "error": "export_dir is required",
                "tool_name": self.get_name(),
                "metadata": {},
            }

        try:
            os.makedirs(export_dir, exist_ok=True)
            audio_products = []
            failed = 0

            for notebook in notebooks:
                notebook_id = notebook.get("notebook_id", "")
                niche = notebook.get("niche", "unknown")

                if not notebook_id:
                    print(f"     Skipping notebook with no ID", flush=True)
                    failed += 1
                    continue

                print(f"     Generating audio for '{niche}' notebook...", flush=True)

                # Trigger audio overview generation
                request_id = self._trigger_audio_generation(notebook_id)
                if not request_id:
                    print(f"       -> Failed to trigger audio generation", flush=True)
                    failed += 1
                    continue

                # Poll for completion
                audio_url = self._poll_audio_status(notebook_id, request_id)
                if not audio_url:
                    print(f"       -> Audio generation timed out or failed", flush=True)
                    failed += 1
                    continue

                # Download the audio file
                filename = f"{niche}_audio_overview.wav"
                audio_path = os.path.join(export_dir, filename)
                if self._download_audio(notebook_id, audio_url, audio_path):
                    audio_products.append({
                        "niche": niche,
                        "notebook_id": notebook_id,
                        "audio_path": audio_path,
                        "filename": filename,
                    })
                    print(f"       -> Audio saved: {filename}", flush=True)
                else:
                    print(f"       -> Failed to download audio", flush=True)
                    failed += 1

            return {
                "success": len(audio_products) > 0,
                "data": {
                    "audio_products": audio_products,
                    "stats": {
                        "generated": len(audio_products),
                        "failed": failed,
                        "total": len(notebooks),
                    },
                },
                "error": None if audio_products else "No audio products generated",
                "tool_name": self.get_name(),
                "metadata": {
                    "generated": len(audio_products),
                    "failed": failed,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    def _trigger_audio_generation(self, notebook_id):
        """Trigger Audio Overview generation via nlm CLI."""
        try:
            result = subprocess.run(
                ["nlm", "studio", "create", notebook_id, "--format", "json"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("request_id", data.get("id", ""))
            return None
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            return None

    def _poll_audio_status(self, notebook_id, request_id):
        """Poll for audio generation completion."""
        elapsed = 0
        while elapsed < self.AUDIO_GENERATION_TIMEOUT:
            try:
                result = subprocess.run(
                    ["nlm", "studio", "status", notebook_id, "--format", "json"],
                    capture_output=True, text=True, timeout=15,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    status = data.get("status", "")
                    if status == "completed":
                        return data.get("audio_url", data.get("url", ""))
                    if status in ("failed", "error"):
                        return None
            except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
                pass

            time.sleep(self.POLL_INTERVAL)
            elapsed += self.POLL_INTERVAL
            print(f"       Waiting for audio generation... ({elapsed}s)", flush=True)

        return None

    def _download_audio(self, notebook_id, audio_url, output_path):
        """Download audio file from NotebookLM."""
        try:
            # Use nlm download-artifact command
            result = subprocess.run(
                ["nlm", "download-artifact", notebook_id,
                 "--output", output_path, "--format", "json"],
                capture_output=True, text=True, timeout=60,
            )
            return result.returncode == 0 and os.path.exists(output_path)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
