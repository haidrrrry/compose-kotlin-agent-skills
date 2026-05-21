# Augment Code Setup

Augment uses workspace rules and `.augment/` configuration.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .augment/skills/compose-kotlin-agent-skills
```

## Augment Rules

Create `.augment/rules/android-kotlin.md`:

```markdown
---
scope: kotlin
---

Source of truth: `.augment/skills/compose-kotlin-agent-skills/SKILL.md`

For Compose UI → `references/02-compose-ui.md`
For DI → `references/05-hilt-di.md`
For DB → `references/06-room-db.md`

Never skip LazyColumn keys. Never use collectAsState on Android screens.
```

## IDE

Augment panel → Workspace Guidelines → Import rules file above.

## Verification

Ask Augment: "Refactor to MVI with UiEvent/UiEffect per compose-kotlin-agent-skills."

Should show sealed UiEvent, Channel/Flow for effects, single UiState.
