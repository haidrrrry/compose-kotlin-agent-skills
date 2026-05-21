# Claude Code / Claude CLI Setup

## Global Install

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git ~/.claude/skills/compose-kotlin-agent-skills
```

Claude Code auto-discovers skills from `~/.claude/skills/*/SKILL.md`.

## Per-Project Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .claude/skills/compose-kotlin-agent-skills
```

## CLAUDE.md Integration

Add to your project's `CLAUDE.md`:

```markdown
## Skills

For all Android/Kotlin work, read `.claude/skills/compose-kotlin-agent-skills/SKILL.md` first.
Load the matching reference file from `references/` for the specific topic.
```

## Verification

```bash
claude "How should I structure a ViewModel with UiState in Jetpack Compose?"
```

Should reference `MutableStateFlow`, `collectAsStateWithLifecycle`, `data class XxxUiState` pattern.
