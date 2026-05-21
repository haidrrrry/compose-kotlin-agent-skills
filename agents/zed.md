# Zed Editor Setup

Zed supports project rules via `.rules` or Assistant instructions.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .zed/skills/compose-kotlin-agent-skills
```

## Project Rules

Create `.rules` in project root:

```markdown
---
globs: ["**/*.kt", "**/*.kts", "**/build.gradle.kts"]
---

Follow compose-kotlin-agent-skills at `.zed/skills/compose-kotlin-agent-skills/SKILL.md`.
Load `references/` files for topic-specific Android guidance.
ViewModel + StateFlow + stateless composables. stringResource for all UI text.
```

## Zed Assistant

Settings → Assistant → Add instruction:
"Use `.zed/skills/compose-kotlin-agent-skills/` for all Kotlin work."

## Verification

Edit a `.kt` file, ask Assistant: "Review against compose-kotlin-agent-skills defaults."

Should flag hardcoded strings, missing LazyColumn keys, collectAsState misuse.
