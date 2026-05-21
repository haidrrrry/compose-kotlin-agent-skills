# Replit Agent Setup

For Replit Agent and Replit Android/Kotlin projects.

## Install

In Replit shell or import from GitHub:

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git skills/compose-kotlin-agent-skills
```

## replit.md

Create `replit.md` in project root:

```markdown
## Android Skill

Read `skills/compose-kotlin-agent-skills/SKILL.md` before modifying Kotlin files.
Load `skills/compose-kotlin-agent-skills/references/` for topic-specific help.

Replit Android: use Gradle Kotlin DSL, Compose BOM versions from SKILL.md version table.
```

## Replit Agent Prompt

Pin in Agent instructions:

```
Always follow compose-kotlin-agent-skills in skills/compose-kotlin-agent-skills/ for Android code.
```

## Verification

Replit Agent: "Set up Compose screen with ViewModel per compose-kotlin-agent-skills."

Should use `viewModel()` / factory pattern and `collectAsStateWithLifecycle`.
