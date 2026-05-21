# OpenCode Setup

OpenCode uses `AGENTS.md` at project root (same pattern as Codex CLI).

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .opencode/skills/compose-kotlin-agent-skills
```

## AGENTS.md

```markdown
## Skills — compose-kotlin-agent-skills

Path: `.opencode/skills/compose-kotlin-agent-skills/`

For Android/Kotlin/Compose:
- Read `SKILL.md` before coding
- Read `references/<topic>.md` for deep dives
- Real patterns from production apps — not doc summaries

Mandatory: UiState in ViewModel, collectAsStateWithLifecycle, LazyColumn keys.
```

## Run

```bash
opencode "Read SKILL.md and scaffold MVVM feature module"
```

## Verification

OpenCode should route to `references/01-architecture.md` for module structure questions.
