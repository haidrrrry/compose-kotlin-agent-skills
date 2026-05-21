# Cline Setup

Cline (VS Code extension) uses `.clinerules` and optional rule files.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .cline/skills/compose-kotlin-agent-skills
```

## .clinerules

Create or append `.clinerules`:

```markdown
# Android/Kotlin — compose-kotlin-agent-skills

Before editing any `.kt` or `.kts` file:
1. Read `.cline/skills/compose-kotlin-agent-skills/SKILL.md`
2. If task matches a topic (Room, Hilt, Compose UI, etc.), read that `references/NN-*.md` file
3. Follow WRONG/RIGHT examples — prefer skill patterns over generic tutorials

Critical: collectAsStateWithLifecycle (not collectAsState), LazyColumn keys, Modifier order.
```

## Cline Rule File (alternative)

In Cline settings → Custom Rules → add path:
`.cline/skills/compose-kotlin-agent-skills/SKILL.md`

## Verification

Task: "Add AuthViewModel with search filter using combine() per compose-kotlin-agent-skills."

Should use `combine(repository.getAllAccounts(), _searchQuery)`.
