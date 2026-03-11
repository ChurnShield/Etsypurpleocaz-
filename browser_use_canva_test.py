"""
Browser Use smoke test — navigates to a GitHub repo page.
Uses a whitelisted domain (github.com) to prove Browser Use works
end-to-end on this container before moving to a real droplet.
"""

import asyncio
import os
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from browser_use import Agent, BrowserProfile, BrowserSession, Controller, ChatAnthropic
from browser_use.browser.profile import ProxySettings

# ── Config ──────────────────────────────────────────────────────────────────
ENV_PATH = Path("/home/user/Etsypurpleocaz-/.env")
load_dotenv(ENV_PATH)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LOG_DIR = Path(__file__).parent / "logs"
SCREENSHOT_DIR = LOG_DIR / "screenshots"
LOG_FILE = LOG_DIR / "browser_use_test.log"

# ── Logging ─────────────────────────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(LOG_FILE, mode="w")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logger = logging.getLogger("browser_test")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ── Screenshot helper ───────────────────────────────────────────────────────
screenshot_counter = 0


async def take_screenshot(page, label: str):
    """Save a timestamped screenshot."""
    global screenshot_counter
    screenshot_counter += 1
    ts = datetime.now().strftime("%H%M%S")
    filename = f"{screenshot_counter:03d}_{ts}_{label}.png"
    filepath = SCREENSHOT_DIR / filename
    await page.screenshot(path=str(filepath), full_page=False)
    logger.info(f"Screenshot saved: {filepath}")
    return str(filepath)


# ── Controller with screenshot action ───────────────────────────────────────
controller = Controller()


@controller.action("Save a screenshot of the current page with a descriptive label")
async def screenshot_action(browser: BrowserSession, label: str = "step"):
    page = await browser.get_current_page()
    path = await take_screenshot(page, label)
    return f"Screenshot saved to {path}"


async def run_test():
    logger.info("=" * 60)
    logger.info(f"=== BROWSER USE SMOKE TEST — {datetime.now().isoformat()} ===")
    logger.info("=" * 60)

    if not ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not found. Check /home/user/Etsypurpleocaz-/.env")
        return

    logger.info("API key loaded (ends with ...%s)" % ANTHROPIC_API_KEY[-4:])

    # ── Browser (headless, with proxy from environment) ────────────────
    proxy_url = os.environ.get("npm_config_proxy") or os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    proxy_settings = None
    if proxy_url:
        parsed = urlparse(proxy_url)
        proxy_settings = ProxySettings(
            server=f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
            username=parsed.username or "",
            password=parsed.password or "",
        )
        logger.info(f"Using proxy: {parsed.scheme}://{parsed.hostname}:{parsed.port}")

    profile = BrowserProfile(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--ignore-certificate-errors",
            "--ignore-ssl-errors=yes",
        ],
        keep_alive=False,
        proxy=proxy_settings,
        disable_security=True,
    )
    session = BrowserSession(browser_profile=profile)

    # ── LLM ─────────────────────────────────────────────────────────────
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=ANTHROPIC_API_KEY,
        max_tokens=8192,
    )

    # ── Task (uses whitelisted github.com domain) ───────────────────────
    task = """Go to https://www.github.com/browser-use/browser-use and do the following:

1. Read the repository name and description from the page.
2. Take a screenshot using screenshot_action with label "repo_homepage".
3. Find and click on the "README" or scroll down to see the README content.
4. Take a screenshot using screenshot_action with label "readme_content".
5. Tell me:
   - The repository name
   - The description/tagline
   - The number of stars (approximate is fine)
   - The first 2-3 sentences of the README

Take screenshots after each major step."""

    agent = Agent(
        task=task,
        llm=llm,
        browser_session=session,
        controller=controller,
        max_actions_per_step=4,
    )

    logger.info("Starting Browser Use agent...")
    logger.info(f"Target: github.com/browser-use/browser-use")
    logger.info(f"Screenshots → {SCREENSHOT_DIR}")

    try:
        result = await agent.run(max_steps=15)
        logger.info("=== AGENT COMPLETED ===")

        final = result.final_result()
        logger.info(f"Final result:\n{final}")
        print("\n" + "=" * 60)
        print("AGENT FINAL ANSWER:")
        print("=" * 60)
        print(final)
        print("=" * 60)

        # Log step history
        logger.info("--- Step-by-step log ---")
        for i, history_item in enumerate(result.history):
            logger.info(f"Step {i + 1}: {history_item.result}")

        # Final screenshot
        try:
            page = await session.get_current_page()
            await take_screenshot(page, "final_state")
        except Exception:
            logger.warning("Could not take final screenshot.")

    except Exception as e:
        logger.error(f"Agent failed: {e}", exc_info=True)
        print(f"\nERROR: {e}")
    finally:
        await session.stop()
        logger.info("Browser closed.")


if __name__ == "__main__":
    asyncio.run(run_test())
