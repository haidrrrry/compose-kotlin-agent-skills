---
name: New agent platform
about: Request an install guide for an AI coding agent not yet covered in agents/.
title: "[agent] add support for <name>"
labels: agent, enhancement
assignees: haidrrrry
---

## Agent

- Name:
- Vendor / org:
- Homepage:
- Public docs:
- Skill / rules / context file convention: <!-- e.g. AGENTS.md, .cursor/rules, ~/.claude/skills, etc. -->

## Why it's worth covering

<!-- Adoption, region, unique capability, request volume, etc. -->

## Install mechanics

<!-- Paste the official "how do I add custom instructions / skills / rules" docs link or excerpt. -->

## Skill loading model

- [ ] Reads a single root file (e.g. `AGENTS.md`)
- [ ] Reads a directory of skills (e.g. `~/.<agent>/skills/`)
- [ ] Reads inline rules (UI-configured)
- [ ] Other: <!-- describe -->

## Suggested install snippet

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git
# ...where does it go?
```
