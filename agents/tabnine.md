# Tabnine Setup

Tabnine Enterprise / Pro supports project context and `.tabnine` config.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .tabnine/skills/compose-kotlin-agent-skills
```

## Project Context

Tabnine Chat → Connect codebase → add instruction file:

`.tabnine/skills/compose-kotlin-agent-skills/SKILL.md`

Or `.tabnine/context.md`:

```markdown
For Kotlin completions and chat, follow compose-kotlin-agent-skills:
- SKILL.md for routing and mandatory defaults
- references/ for architecture, Compose, Room, Hilt, etc.
Prefer collectAsStateWithLifecycle over collectAsState.
```

## tabnine.toml (Enterprise)

```toml
[context]
include = [".tabnine/skills/compose-kotlin-agent-skills/**/*.md"]
```

## Verification

Tabnine chat: "Room DAO with Flow for list screen per compose-kotlin-agent-skills."

Should suggest `@Query` returning `Flow<List<Entity>>`.
