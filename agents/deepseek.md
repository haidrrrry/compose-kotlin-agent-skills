# DeepSeek Setup

For DeepSeek Chat IDE, DeepSeek Coder, and agents with `AGENTS.md` / rules support.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .deepseek/skills/compose-kotlin-agent-skills
```

## AGENTS.md Integration

Add to project `AGENTS.md`:

```markdown
## compose-kotlin-agent-skills

Path: `.deepseek/skills/compose-kotlin-agent-skills/`

Rules:
- Read `SKILL.md` first for all Android/Kotlin tasks
- Use `references/` for topic-specific guidance
- ViewModel owns state; composables are stateless
- LazyColumn requires `key = { it.id }`
```

## VS Code / Cursor with DeepSeek model

Copy skill to `.cursor/skills/` or `.continue/` and point model to DeepSeek — skill content is model-agnostic.

## Verification

Ask: "Implement Room DAO with Flow following compose-kotlin-agent-skills."

Should output `@Dao`, `Flow<List<T>>`, `suspend` writes, repository layer.
