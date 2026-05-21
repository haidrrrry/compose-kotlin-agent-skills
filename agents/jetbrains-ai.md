# JetBrains AI Assistant / Junie Setup

For Android Studio, IntelliJ IDEA with AI Assistant or Junie agent.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .junie/skills/compose-kotlin-agent-skills
```

Also works at:

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .idea/compose-kotlin-agent-skills
```

## AI Assistant Guidelines

Settings → Tools → AI Assistant → Guidelines → Add file:
`.junie/skills/compose-kotlin-agent-skills/SKILL.md`

Or create `.junie/guidelines.md`:

```markdown
Follow compose-kotlin-agent-skills (`.junie/skills/compose-kotlin-agent-skills/SKILL.md`).
For Compose performance read `references/10-performance.md`.
For Room read `references/06-room-db.md`.
Match existing module structure — feature/data/domain/presentation.
```

## Junie

Junie reads project docs — add SKILL.md to "trusted project files" in Junie settings.

## Verification

Ask Junie: "Add new feature module with Clean Architecture per skill."

Should propose domain interface + data impl + presentation ViewModel layers.
