# Aider Setup

Aider reads `CONVENTIONS.md`, `.aider.conf.yml`, and files you add to context.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .aider/skills/compose-kotlin-agent-skills
```

## CONVENTIONS.md

Create `CONVENTIONS.md` in project root:

```markdown
# Android Conventions — compose-kotlin-agent-skills

Read `.aider/skills/compose-kotlin-agent-skills/SKILL.md` before Kotlin changes.
Topic guides: `.aider/skills/compose-kotlin-agent-skills/references/`.

Stack defaults: Compose + Material 3 + ViewModel + StateFlow + Room Flow + Hilt or Koin.
No hardcoded UI strings. No ViewModels passed into composables.
```

## aider.conf.yml

```yaml
read:
  - CONVENTIONS.md
  - .aider/skills/compose-kotlin-agent-skills/SKILL.md
```

## Usage

```bash
aider --read .aider/skills/compose-kotlin-agent-skills/SKILL.md
aider --message "Refactor this screen to container/content pattern per skill"
```

## Verification

Aider should load SKILL.md and produce `collectAsStateWithLifecycle` + `data class UiState`.
