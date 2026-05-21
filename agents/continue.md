# Continue.dev Setup

Continue uses `.continue/config.yaml` for rules and context.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .continue/skills/compose-kotlin-agent-skills
```

## config.yaml

Add to `.continue/config.yaml`:

```yaml
rules:
  - uses: file
    with:
      path: .continue/skills/compose-kotlin-agent-skills/SKILL.md
    name: compose-kotlin-agent-skills
    description: Production Android/Kotlin + Compose patterns
```

Or paste rules inline:

```yaml
rules:
  - |
    For Kotlin/Android: read .continue/skills/compose-kotlin-agent-skills/SKILL.md.
    Load references/ for Room, Hilt, Compose, coroutines, etc.
```

## @docs / Context

In Continue chat: `@compose-kotlin-agent-skills` if you symlink or add as docs folder.

## Verification

Continue chat: "Explain LazyColumn key requirement per compose-kotlin-agent-skills."

Should explain item identity + recomposition state loss without keys.
