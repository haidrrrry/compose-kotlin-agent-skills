# Kimi (Moonshot) Setup

Works with Kimi CLI, Kimi Code, and IDE plugins that accept project instructions.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .kimi/skills/compose-kotlin-agent-skills
```

## KIMI.md / Project Instructions

Create `KIMI.md` in project root:

```markdown
## Android/Kotlin Skill

Read `.kimi/skills/compose-kotlin-agent-skills/SKILL.md` before any Kotlin or Compose change.
For deep topics, read matching `references/*.md` (architecture, Room, animations, etc.).
Follow WRONG/RIGHT patterns in skill — do not copy generic Android docs.
```

## Kimi CLI

```bash
kimi chat "Read .kimi/skills/compose-kotlin-agent-skills/SKILL.md then explain ViewModel + UiState pattern"
```

## Verification

Prompt: "用 compose-kotlin-agent-skills 说明 Jetpack Compose ViewModel 状态管理" or English equivalent.

Should mention `StateFlow`, `collectAsStateWithLifecycle`, not `collectAsState` on Android.
