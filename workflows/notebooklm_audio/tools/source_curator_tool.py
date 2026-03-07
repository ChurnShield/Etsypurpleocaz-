# =============================================================================
# workflows/notebooklm_audio/tools/source_curator_tool.py
#
# Phase 1: Curates and uploads source material to NotebookLM notebooks.
# Gathers content from existing listings, trend reports, and niche docs
# to build rich knowledge bases for audio product generation.
# =============================================================================

import json
import subprocess
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool


class SourceCuratorTool(BaseTool):
    """Curates and uploads sources to NotebookLM notebooks.

    Gathers source material from:
    - Existing listing descriptions (from database)
    - Niche expertise documents (from docs/ directory)
    - Product type guides

    Creates or updates NotebookLM notebooks per niche + product type.
    """

    def execute(self, **kwargs) -> dict:
        niches = kwargs.get("niches", ["tattoo"])
        product_types = kwargs.get("product_types", ["business_startup_guide"])
        notebook_ids = kwargs.get("notebook_ids", {})
        db = kwargs.get("db")

        try:
            # Check if nlm CLI is available
            if not self._check_nlm_available():
                return {
                    "success": False,
                    "data": None,
                    "error": "nlm CLI not installed or not authenticated",
                    "tool_name": self.get_name(),
                    "metadata": {},
                }

            curated_notebooks = []
            total_sources = 0

            for niche in niches:
                notebook_id = notebook_ids.get(niche, "")

                # Create notebook if none exists for this niche
                if not notebook_id:
                    notebook_id = self._create_notebook(niche)
                    if not notebook_id:
                        print(f"     Failed to create notebook for {niche}", flush=True)
                        continue

                print(f"     Curating sources for '{niche}' notebook...", flush=True)

                # Gather and add sources
                sources_added = 0

                # Source 1: Niche expertise content
                expertise_content = self._build_niche_expertise(niche)
                if expertise_content:
                    if self._add_text_source(notebook_id, f"{niche} Industry Guide", expertise_content):
                        sources_added += 1

                # Source 2: Product type guides
                for pt in product_types:
                    guide_content = self._build_product_guide(niche, pt)
                    if guide_content:
                        if self._add_text_source(notebook_id, f"{niche} {pt} Guide", guide_content):
                            sources_added += 1

                # Source 3: Existing listing data from database
                if db:
                    listing_content = self._gather_listing_data(db, niche)
                    if listing_content:
                        if self._add_text_source(notebook_id, f"{niche} Existing Listings", listing_content):
                            sources_added += 1

                curated_notebooks.append({
                    "niche": niche,
                    "notebook_id": notebook_id,
                    "sources_added": sources_added,
                })
                total_sources += sources_added
                print(f"     Added {sources_added} sources to '{niche}' notebook", flush=True)

            return {
                "success": True,
                "data": {
                    "notebooks": curated_notebooks,
                    "total_sources": total_sources,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "niches_processed": len(niches),
                    "total_sources": total_sources,
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

    def _check_nlm_available(self):
        """Check if the nlm CLI is installed and authenticated."""
        try:
            result = subprocess.run(
                ["nlm", "login", "--check"],
                capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _create_notebook(self, niche):
        """Create a new NotebookLM notebook for a niche."""
        try:
            result = subprocess.run(
                ["nlm", "notebook", "create",
                 f"{niche}-business-expertise",
                 "--format", "json"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("id", data.get("notebook_id", ""))
            return None
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            return None

    def _add_text_source(self, notebook_id, title, content):
        """Add a text source to a NotebookLM notebook."""
        try:
            result = subprocess.run(
                ["nlm", "source", "add", notebook_id,
                 "--type", "text",
                 "--title", title,
                 "--content", content[:50000]],  # NotebookLM source limit
                capture_output=True, text=True, timeout=30,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _build_niche_expertise(self, niche):
        """Build niche expertise content for NotebookLM ingestion."""
        expertise = {
            "tattoo": (
                "Tattoo Studio Business Guide\n\n"
                "Starting and running a successful tattoo studio requires attention to "
                "professional branding, client management, and regulatory compliance. "
                "Key business documents include: appointment cards, gift certificates, "
                "price lists, consent forms, aftercare cards, business cards, and intake forms.\n\n"
                "Industry Trends (2025-2026):\n"
                "- Fine-line and minimalist tattoos continue growing in popularity\n"
                "- Digital booking and client management systems are now expected\n"
                "- Professional branding differentiates studios in competitive markets\n"
                "- Gift certificates are a major revenue driver (average 30% markup)\n"
                "- Aftercare instructions reduce complications and improve reviews\n\n"
                "Common Pain Points:\n"
                "- Creating professional documents without design skills\n"
                "- Maintaining consistent branding across all client touchpoints\n"
                "- Managing appointment scheduling and client intake efficiently\n"
                "- Complying with health and safety documentation requirements\n"
            ),
            "nail": (
                "Nail Salon Business Guide\n\n"
                "Running a nail salon requires professional branding and efficient "
                "client management. Essential business documents include: service menus, "
                "price lists, gift certificates, appointment cards, and business cards.\n\n"
                "Industry Trends (2025-2026):\n"
                "- Nail art and custom designs are premium services\n"
                "- Social media marketing is critical for client acquisition\n"
                "- Gift cards drive 25-40% of new client visits\n"
                "- Professional branding increases perceived value\n"
            ),
            "hair": (
                "Hair Salon & Barber Business Guide\n\n"
                "Hair salons and barber shops need professional branding to stand out. "
                "Key documents: service menus, price lists, gift certificates, "
                "appointment cards, business cards, and consultation forms.\n\n"
                "Industry Trends (2025-2026):\n"
                "- Personalized consultations improve client retention\n"
                "- Gift certificates are top sellers during holidays\n"
                "- Professional branding commands premium pricing\n"
            ),
            "beauty": (
                "Beauty & Spa Business Guide\n\n"
                "Beauty professionals and spa owners need polished branding to "
                "attract and retain clients. Essential documents: service menus, "
                "price lists, gift certificates, consent forms, aftercare cards.\n\n"
                "Industry Trends (2025-2026):\n"
                "- Wellness and self-care services are booming\n"
                "- Professional consent forms build trust\n"
                "- Digital gift cards are increasingly popular\n"
            ),
        }
        return expertise.get(niche, "")

    def _build_product_guide(self, niche, product_type):
        """Build a product-specific guide for audio generation."""
        guides = {
            "business_startup_guide": (
                f"Starting a {niche.title()} Business: Complete Guide\n\n"
                f"This guide covers everything a new {niche} business owner needs:\n"
                f"1. Setting up your brand identity\n"
                f"2. Essential business documents and templates\n"
                f"3. Client management best practices\n"
                f"4. Marketing and social media strategy\n"
                f"5. Pricing your services competitively\n"
                f"6. Building a professional online presence\n"
            ),
            "template_walkthrough": (
                f"How to Customize Your {niche.title()} Business Templates\n\n"
                f"Step-by-step guide to editing professional templates:\n"
                f"1. Opening your template in Canva or PDF reader\n"
                f"2. Customizing colors, fonts, and images to match your brand\n"
                f"3. Adding your business information and contact details\n"
                f"4. Printing and sharing your finished documents\n"
                f"5. Tips for professional results\n"
            ),
            "industry_tips": (
                f"Expert Tips for {niche.title()} Business Owners\n\n"
                f"Professional insights for growing your {niche} business:\n"
                f"1. Building repeat business through exceptional client experience\n"
                f"2. Using gift certificates as a revenue growth tool\n"
                f"3. Social media strategies that actually work\n"
                f"4. Managing client expectations and communication\n"
                f"5. Seasonal promotions that drive traffic\n"
            ),
            "seasonal_guide": (
                f"Seasonal Marketing for {niche.title()} Businesses\n\n"
                f"How to capitalize on seasonal opportunities:\n"
                f"- Valentine's Day: Gift certificates, couples packages\n"
                f"- Mother's Day: Spa/beauty gift bundles\n"
                f"- Holiday Season: Gift cards, year-end promotions\n"
                f"- Back to School: Student specials\n"
                f"- Summer: Wedding season packages\n"
            ),
        }
        return guides.get(product_type, "")

    def _gather_listing_data(self, db, niche):
        """Gather existing listing data from the database for a niche."""
        try:
            rows = db.table("execution_logs").select(
                "metadata"
            ).eq("workflow_id", "auto_listing_creator").execute()

            if not rows:
                return ""

            # Extract listing titles and descriptions from metadata
            content_parts = []
            for row in rows[:20]:  # Limit to recent entries
                meta = row.get("metadata")
                if meta and isinstance(meta, str):
                    try:
                        meta = json.loads(meta)
                    except json.JSONDecodeError:
                        continue
                if isinstance(meta, dict):
                    title = meta.get("title", "")
                    if title and niche.lower() in title.lower():
                        content_parts.append(f"- {title}")

            if content_parts:
                return f"Existing {niche} Products in PurpleOcaz Shop:\n" + "\n".join(content_parts)
            return ""
        except Exception:
            return ""
