---
description: Show pipeline status and next actions
---
Pipeline status check:
1. Show last 5 git commits: git log --oneline -5
2. Show top 5 NEW ideas: grep "NEW" ideas_backlog.md 2>/dev/null | head -5
3. Show STANDUP.md header: head -40 STANDUP.md
4. Show cron jobs: crontab -l
5. Check Anthropic credit balance if possible
Summarise: what was done last, what should be done next.
