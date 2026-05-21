# GitHub Copilot Setup

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .github/skills/compose-kotlin-agent-skills
```

## .github/copilot-instructions.md Integration

Add to `.github/copilot-instructions.md`:

```markdown
## Android/Kotlin Engineering

For all Kotlin and Jetpack Compose code, follow the patterns in
`.github/skills/compose-kotlin-agent-skills/SKILL.md`.

Critical rules:
- ViewModel owns state via MutableStateFlow, not mutableStateOf
- Composables collect state with collectAsStateWithLifecycle
- Pass lambdas to composables, never ViewModels
- Modifier order matters: padding → clip → background → clickable
- LazyColumn always needs key parameter
- Use Room Flow queries for reactive data
- Use combine() for derived/filtered state in ViewModel

For specific topics, read the matching file from
`.github/skills/compose-kotlin-agent-skills/references/`.
```

## Copilot Chat Usage

In Copilot Chat, reference the skill:

```
@workspace How should I structure my ViewModel? Follow the compose-kotlin-agent-skills patterns.
```

## Verification

Ask Copilot: "Set up a Room DAO with Flow queries following the compose-kotlin-agent-skills."

Should produce `@Dao` interface with `Flow<List<T>>` return type, `suspend` for writes, `@Query` annotations.
