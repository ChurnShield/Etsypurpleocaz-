# Ideas Backlog

Auto-populated from weekly YouTube digest. Deduplicated 2026-03-23.

---

## Agent Architecture & Automation

[ ] **Architecture** Sub-agent architecture for PurpleOcaz + ChurnShield
    - Orchestrator (Big Brain) assigns tasks to specialist sub-agents
    - Research Agent: YouTube feed monitoring, niche trends, ideas_backlog updates
    - Design Agent: asset sourcing + Canva MCP design building
    - Listing Agent: Etsy titles, descriptions, tags (SEO optimised)
    - QA Agent: reviews outputs before anything goes live
    - ChurnShield Outreach Agent: Reddit monitoring, draft responses for approval
    - ChurnShield Analytics Agent: PostHog churn signal monitoring
    - Key principle: agents propose, Andy approves — nothing live without sign-off
    - Frameworks to evaluate: agency-agents repo, Claude multi-agent API, n8n
    — Source: Strategic planning, 2026-03-11

[ ] **Autoresearch System** Self-improving prompt loop for CC skills (Karpathy method). 5 components:
    1. FIND WHY SKILLS FAIL — Act as skill diagnostician. Audit skill prompt, run against 5 test inputs, score each, identify failure patterns (vague instructions, missing constraints, weak output format), rank by frequency and impact, deliver diagnosis before fixes.
    2. BUILD SCORING CHECKLIST — Act as quality criteria specialist. Turn vague "good output" into 3-6 precise yes/no scoring questions. No subjectivity.
    3. RUN THE AUTORESEARCH LOOP — Act as autonomous prompt optimization agent. One change at a time, scored against checklist. Continuous improvement until plateau.
    4. TURN CHANGELOG INTO RULES — Act as prompt intelligence analyst. Extract permanent lessons from optimization logs into reusable rules for all future prompts.
    5. AUTORESEARCH ANYTHING YOU REPEAT — Act as optimization strategist. Take any repeatable task, build autoresearch system that improves it automatically.
    - Rules: diagnose before fixing, every failure must be specific, rank by frequency not obviousness, establish baseline before changes
    - PRIORITY: High — apply to Etsy listing skill, flyer build skill, and thumbnail pipeline first
    — Source: @alex_prompter on Twitter, 2026-03-23

[ ] **Skills** Implement IndyDevDan's library.yaml pattern for skill management — treat skills as versioned distributable packages, single source of truth. Evaluate github.com/disler/the-library before building. Watch the Library Meta-Skill video first (26 mins, IndyDevDan, 2026-03-23 digest). Dedicated session required — do not tidy skills/ folder until this is decided. — Source: Strategic decision 2026-03-23

[ ] **Agent Automation** Set up Mac Mini with autonomous agents for end-to-end device operation (GUI control, AirDrop delivery, 2-3 core skills max) — Source: Mac Mini Agents OpenClaw

[ ] **Automation** Manus for weekly niche research — automated Monday morning runs, drops findings to Google Sheet — Source: Strategic planning, 2026-03-16

[ ] **Vision** Overnight listing pipeline — Andy approves niche on phone → pipeline runs overnight → draft listing ready next morning. Zero manual steps. — Source: Strategic planning, 2026-03-16

[ ] **Pipeline** Build private skill distribution system using library.yaml — Source: The Library Meta-Skill, 2026-03-23

[ ] **Automation** Think in complete workflows rather than individual tasks — Source: You Have To Think In Workflows, 2026-03-23

[x] **Architecture** Verification agent step — GET verification after every API call. DONE: implemented in SOP and all publish workflows. — Source: 2026-03-16

[x] **Process** TODO.md per session — CC creates task list at session start. DONE: using TaskCreate/TaskUpdate. — Source: 2026-03-16

## PurpleOcaz — Etsy Strategy

[ ] **Etsy Keywords** Target "Ita bags" as unsaturated high-opportunity keyword — Source: eRank Trend Report, 2026-03-16

[ ] **Etsy Trends** Create spring 2026 products around trending colors/themes/aesthetics — Source: Our 2026 Spring Trends Forecast, 2026-03-16

[ ] **Etsy Trends** Target crochet-related keywords showing fast growth — Source: This Etsy Keyword is GROWING FAST, 2026-03-16

[ ] **Etsy SEO** Implement 5-step SEO optimization framework for better discoverability — Source: Struggling to get noticed on Etsy, 2026-03-16

[ ] **Etsy Strategy** Focus on broad customer appeal vs narrow niches to maximize revenue — Source: Why Niches LOSE You Money, 2026-03-16

[ ] **AI Tools** Test Nano Banana AI for digital template/product creation — Source: I discovered how to make $100K with Nano Banana AI, 2026-03-11

[ ] **Pricing Strategy** Avoid constant sales and deceptive pricing tactics on Etsy — Source: Constant Sales, Deceptive Pricing, 2026-03-11

[ ] **Marketplace** Monitor Etsy competitors like GoImagine for strategic insights — Source: Why Etsy's Biggest Alternative is Closing Down, 2026-03-11

[ ] **Conversion** Optimize for conversion rate over traffic volume — Source: Top Etsy sellers aren't working harder, 2026-03-11

## PurpleOcaz — Etsy (Added 2026-03-23)

[ ] **Etsy SEO** Avoid jumping on trending keyword spikes — track trends for consistency first — Source: A BIG mistake Etsy sellers make
[ ] **Etsy Strategy** Monitor offsite ads performance and understand auto opt-in implications — Source: Do You Understand Etsy Offsite Ads
[ ] **Keyword Research** Replace "digital" with specific niches like "digital planner templates" — Source: Dont use this Etsy Trending Keyword
[ ] **Trend Analysis** Pull trends from fashion/Pinterest into Etsy before they become saturated — Source: Etsy Trends To Sell NOW
[ ] **Listing Optimization** Use exclusive data on best days/times to list on Etsy — Source: Exclusive Data The Best Day to List on Etsy
[ ] **Template Creation** Focus on Canva template tutorials with step-by-step mockup process — Source: How to Sell Canva Templates
[ ] **Market Positioning** Position as ahead of saturation curve rather than following trends — Source: Is Etsy TOO Saturated in 2026
[ ] **Success Stories** Document low-start success stories ($5/month to growth) for social proof — Source: Sarah Started With $5Month on Etsy
[ ] **Trend Research** Implement Pinterest-first trend identification before Etsy adoption — Source: The BEST Trends To Sell on Etsy in 2026
[ ] **Quick Wins** Focus on immediate traffic generation techniques for first $100 — Source: The FASTEST Way To Make Money on Etsy

## ChurnShield

[ ] **ChurnShield** Apply "saying no" principle to feature requests and scope creep — Source: You Have To Learn To Say No, 2026-03-11

## Business & Mindset

[ ] **Business Focus** Concentrate on mastering one business before expanding to multiple — Source: I Don't Fear The Man With 10 Businesses, 2026-03-16
[ ] **Business Metrics** Understand difference between gross vs net profit for decision making — Source: Gross Profit VS Net Profit, 2026-03-11
[ ] **Customer Targeting** Ensure marketing attracts the right customer segments — Source: I'm Attracting The Wrong People, 2026-03-16
[ ] **Decision Making** Know when to push through vs pivot business strategies — Source: Push vs Pivot, 2026-03-16
[ ] **Business Resilience** Prepare for economic uncertainty affecting consumer spending — Source: The US-Iran War WILL Impact Small Businesses, 2026-03-23
[ ] **Customer Relationships** Let customers set their own goals to increase buy-in — Source: Let Them Set The Goal, 2026-03-23
[ ] **Value Creation** Create customer dependency through solving critical business problems — Source: Make Them Need You, 2026-03-23
[ ] **AI Strategy** Focus on human-AI collaboration gap as competitive advantage — Source: The Gap AI Is Creating, 2026-03-23
[ ] **Business Philosophy** Apply Rockefeller's systematic approach to wealth building — Source: The Greatest Lesson From Rockefeller, 2026-03-23

## From Weekly Digest 2026-03-23

- **Idea:** Track trends before they spike on Etsy by monitoring Pinterest and social media, then bringing fresh trends to Etsy before competition arrives
- **Apply to:** PurpleOcaz
- **Action:** Set up Pinterest monitoring workflow in n8n to identify emerging design trends 2-3 months before they hit Etsy
- **Effort:** Medium
- **Idea:** Implement "Library Meta-Skill" system for distributing and versioning AI skills/prompts across devices and projects using library.yaml config
- **Apply to:** AgentPipeline
- **Action:** Build library.yaml system to manage Claude Code skills and n8n workflows centrally
- **Effort:** High
- **Idea:** Niche down trending keywords instead of using broad terms - "digital planner templates" vs just "digital"
- **Apply to:** PurpleOcaz
- **Action:** Audit current listings and replace broad keywords with specific niche variations using eRank data
- **Effort:** Low
- **Idea:** Use best day/time data for Etsy listings to maximize visibility in algorithm
- **Apply to:** PurpleOcaz
- **Action:** Extract specific timing data from Starla Moore's exclusive research and schedule listings accordingly
- **Effort:** Low
- **Idea:** Build customer dependency through solving critical problems rather than just being convenient
- **Apply to:** ChurnShield
- **Action:** Position ChurnShield as essential business survival tool, not just nice-to-have analytics
- **Effort:** Medium
