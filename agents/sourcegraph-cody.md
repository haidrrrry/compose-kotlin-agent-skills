# Sourcegraph Cody Setup

Cody uses workspace context and optional `.sourcegraph/cody.json`.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .sourcegraph/skills/compose-kotlin-agent-skills
```

## Cody Custom Instructions

VS Code / JetBrains → Cody Settings → Custom Instructions:

```markdown
For Android/Kotlin in this repo, prioritize:
`.sourcegraph/skills/compose-kotlin-agent-skills/SKILL.md` and `references/`.
Use production patterns (ViewModel UiState, Room Flow, Hilt scopes).
```

## Context File

Add to Cody "@-mention" favorites or `cody.json`:

```json
{
  "customInstructions": "Read .sourcegraph/skills/compose-kotlin-agent-skills/SKILL.md for Kotlin work."
}
```

## Verification

Cody chat: "@workspace compose-kotlin-agent-skills ViewModel pattern"

Should reference StateFlow + container/content composable split.
