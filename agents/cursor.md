# Cursor Setup

## Option 1: As a Skill (Recommended)

Clone into your project's `.cursor/skills/` directory:

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .cursor/skills/compose-kotlin-agent-skills
```

Cursor auto-discovers skills from `.cursor/skills/*/SKILL.md`.

## Option 2: As a Rule

Create `.cursor/rules/android-kotlin.md`:

```markdown
---
description: Android/Kotlin development with Jetpack Compose
globs: ["**/*.kt", "**/*.kts"]
alwaysApply: false
---

You are a senior Android engineer. Follow the compose-kotlin-agent-skills for all Kotlin code.

Read `.cursor/skills/compose-kotlin-agent-skills/SKILL.md` before writing any Kotlin.
When the task involves a specific topic (architecture, animations, Room, etc.),
read the matching reference file from `references/` as listed in SKILL.md.
```

## Option 3: Global Install

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git ~/.cursor/skills/compose-kotlin-agent-skills
```

Available across all Cursor projects.

## Verification

Open Cursor, start a chat, and ask: "How should I structure a ViewModel with UiState?"

The agent should reference patterns from the skill — `MutableStateFlow`, `collectAsStateWithLifecycle`, `data class XxxUiState`.
