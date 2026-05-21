# OpenHands Setup

OpenHands (formerly OpenDevin) uses `config.toml` and microagents.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .openhands/skills/compose-kotlin-agent-skills
```

## Microagent

Create `.openhands/microagents/android-kotlin.md`:

```markdown
---
name: compose-kotlin-agent-skills
type: knowledge
---

Read SKILL.md at `.openhands/skills/compose-kotlin-agent-skills/SKILL.md`.
All Kotlin changes must follow WRONG/RIGHT patterns in that skill.
References in `references/` for architecture, Room, Compose, testing, release.
```

## config.toml hint

```toml
[llm]
# Use your preferred model — skill is model-agnostic

[agent]
enable_prompt_extensions = true
```

## Verification

OpenHands task: "Fix LazyColumn recomposition issue using compose-kotlin-agent-skills."

Should add `key = { it.id }` and stable lambdas with `remember`.
