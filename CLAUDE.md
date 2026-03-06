# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projects

- **PurpleOcaz** — Etsy Star Seller shop, 900+ digital template listings, automating the design-to-listing pipeline
- **ChurnShield** — B2B SaaS churn reduction tool, performance-based pricing (20% of saved revenue, capped at £500/month), built with Lovable/React/TypeScript/Supabase/Stripe
- **Tails of Sinton Green** — Dog grooming business

## GitHub Repos

- `github.com/ChurnShield/keep-them-happy` — ChurnShield
- `github.com/ChurnShield/Etsypurpleocaz-` — PurpleOcaz automation

## Key Tools & Stack

- **Lovable** for frontend (React/TypeScript/Supabase)
- **n8n** for automation workflows
- **Canva Pro** for templates
- **Gemini** image generation (Nano Banana pipeline)
- **Replicate/FLUX.1** for image generation
- **Google Sheets** as data layer
- **Anthropic (Claude)** for AI processing (model: claude-sonnet-4-6)

## Service Integrations (configured via .env)

- **Google Sheets** — Output destination (spreadsheet "AI News" via service account)
- **Etsy** — Shop integration (shop ID: 34071205)
- **Canva** — Design/image generation
- **Replicate (FLUX.1)** — Primary SVG image provider
- **RSS Feeds** — TechCrunch AI, The Verge AI, VentureBeat AI, Hacker News, Reddit (r/artificial, r/MachineLearning, r/singularity)

## Working Style

- Andy is frequently mobile — keep tasks async and approvable
- Prefer step-by-step reasoning before acting
- Always diagnose before fixing

## Important Notes

- `.env` contains all API keys and secrets — never commit it
- Google credentials file (`google-credentials.json`) is expected in the project root
- Original development environment is Windows (paths in .env reference `C:\Users\andyn\...`)
