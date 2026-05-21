# OpenAI Codex CLI Setup

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .codex/skills/compose-kotlin-agent-skills
```

## AGENTS.md Integration

Add to your project root `AGENTS.md`:

```markdown
## Android/Kotlin Skill

For all Kotlin and Android development, follow the instructions in
`.codex/skills/compose-kotlin-agent-skills/SKILL.md`.

When working on a specific topic (architecture, Compose UI, animations,
coroutines, DI, Room, navigation, KMP, networking, performance, testing,
camera/ML, or release), read the corresponding reference file from
`.codex/skills/compose-kotlin-agent-skills/references/`.

Key rules:
- ViewModel owns all state via MutableStateFlow
- Always use collectAsStateWithLifecycle (not collectAsState) on Android
- Always provide keys in LazyColumn/LazyRow
- Modifier order: padding → clip → background → clickable
- Never pass ViewModels to composables — pass lambdas
```

## Verification

```bash
codex "How should I set up Hilt dependency injection for a ViewModel?"
```

Should reference `@HiltViewModel`, `@Inject constructor`, scope rules from the skill.
