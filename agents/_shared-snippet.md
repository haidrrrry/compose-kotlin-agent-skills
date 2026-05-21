# Shared Instruction Snippet

Paste this block into any agent's project instructions file (`AGENTS.md`, `CLAUDE.md`, rules file, etc.):

```markdown
## Android/Kotlin Skill (compose-kotlin-agent-skills)

For all Kotlin, Jetpack Compose, and Android work:

1. Read `SKILL.md` in the compose-kotlin-agent-skills folder before writing code.
2. Load the matching file from `references/` for the topic (see routing table in SKILL.md).
3. Apply mandatory defaults: string resources (no hardcoded UI text), ViewModel-owned state,
   `collectAsStateWithLifecycle`, LazyColumn keys, correct Modifier order.

Repo: https://github.com/haidrrrry/compose-kotlin-agent-skills
```

**Verification prompt (all agents):**

```
How should I structure a ViewModel with UiState for Jetpack Compose?
Use compose-kotlin-agent-skills patterns.
```

Expected: `MutableStateFlow`, `data class XxxUiState`, `collectAsStateWithLifecycle`, container/content composable split.
