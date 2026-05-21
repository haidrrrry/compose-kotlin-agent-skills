---
name: Bug report
about: A guardrail is wrong, a snippet doesn't compile, a link is broken, or an agent loads the skill incorrectly.
title: "[bug] "
labels: bug
assignees: haidrrrry
---

## What is broken

<!-- One sentence. e.g. "references/06-room-db.md migration snippet doesn't compile with Room 2.7" -->

## Where

- Skill / file: <!-- e.g. skills/android-kotlin-compose/SKILL.md -->
- Section / heading: <!-- e.g. "Recomposition stability" -->
- Line range (if applicable): <!-- e.g. L120–L145 -->

## Reproduction

<!-- Minimum steps. For code: paste the snippet + the error. For agents: paste the prompt and the wrong response. -->

```text

```

## Expected behavior

<!-- What should the agent / snippet do instead? -->

## Environment

- Agent + version: <!-- e.g. Cursor 0.4x, Claude Code 1.x -->
- Kotlin / AGP / Compose BOM versions:
- OS:

## Validator output (if relevant)

```text
$ python3 scripts/validate_skills.py --strict
```
