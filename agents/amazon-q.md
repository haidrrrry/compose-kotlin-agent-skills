# Amazon Q Developer Setup

For Amazon Q in IDE (VS Code, JetBrains, etc.) and Amazon Q CLI.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .amazonq/skills/compose-kotlin-agent-skills
```

## Project Context

Create `.amazonq/rules/android-kotlin.md` (or use Q Developer → Add project context):

```markdown
# compose-kotlin-agent-skills

Read `.amazonq/skills/compose-kotlin-agent-skills/SKILL.md` for Kotlin/Compose/Android tasks.
References: `.amazonq/skills/compose-kotlin-agent-skills/references/`.

Production rules: Hilt ViewModel scope, Room Flow DAOs, offline-first repository,
Compose stability (@Immutable UiState), baseline profiles before release.
```

## Amazon Q CLI

```bash
q chat --project-context .amazonq/skills/compose-kotlin-agent-skills/SKILL.md
```

## Verification

Ask Q: "Generate Hilt module for AuthRepository per compose-kotlin-agent-skills."

Should use `@Binds` + `@Singleton`, not `@Provides` for simple interface binding.
