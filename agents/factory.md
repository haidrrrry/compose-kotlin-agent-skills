# Factory Droid Setup

Factory.ai Droid uses repository context and `AGENTS.md` / droid instructions.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .factory/skills/compose-kotlin-agent-skills
```

## AGENTS.md

```markdown
## compose-kotlin-agent-skills

Location: `.factory/skills/compose-kotlin-agent-skills/`

Droid must read `SKILL.md` before Android PRs.
Load `references/` for review topics (performance, testing, release checklist).

PR checklist from `references/13-release-checklist.md` before shipping.
```

## Droid Session

Start session with context:

```
Use compose-kotlin-agent-skills in .factory/skills/ as authoritative Android guide.
```

## Verification

Droid: "Review PR for Compose anti-patterns per compose-kotlin-agent-skills."

Should flag missing keys, wrong Modifier order, hardcoded strings.
