# /context — Switch Context Mode

Switch between build, research, and review modes. Each mode changes Claude's behaviour, priorities, agent selection, and which rules are enforced.

## Usage

```
/context build     — listing builds, pipeline runs, Canva/Etsy API work
/context research  — niche analysis, competitor research, keyword research
/context review    — listing quality audits, architecture review, health checks
```

## Process

1. Read the argument provided by the user: `$ARGUMENTS`
2. If the argument is `build`, `research`, or `review`:
   - Read `.claude/contexts/{argument}.md`
   - Confirm the mode switch with a one-line summary
   - Follow all behaviour rules in that context file for the rest of the session
3. If no argument or invalid argument:
   - List the 3 available modes with one-line descriptions
   - Ask which mode to activate

## Confirmation Format

After reading the context file, confirm with exactly:

```
Context: {mode} — {one-line description from the context file}
```

Examples:
```
Context: build — terse, fast, verify everything, planner then verifier
Context: research — thorough, cite sources, structured reports, no building
Context: review — critical, flag everything, approve nothing without evidence
```

## Rules

- Only one context can be active at a time
- Switching context replaces the previous mode entirely
- The context stays active until the user switches again or the session ends
- If the user asks to do something that conflicts with the active context (e.g., building in research mode), remind them of the active context and suggest switching
