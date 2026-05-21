# Roo Code Setup

Roo Code (VS Code) uses `.roo/` rules and custom modes.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .roo/skills/compose-kotlin-agent-skills
```

## .roo/rules/

Create `.roo/rules/compose-kotlin-agent-skills.md`:

```markdown
# compose-kotlin-agent-skills

Read `.roo/skills/compose-kotlin-agent-skills/SKILL.md` when working on `.kt` files.
Use `references/` for deep topics listed in SKILL.md routing table.

Code mode defaults:
- MVVM unless user asks for MVI
- Repository between ViewModel and DAO
- stringResource for strings
```

## Custom Mode (optional)

Roo → Modes → Duplicate "Code" → System prompt append:
"Follow compose-kotlin-agent-skills in `.roo/skills/`."

## Verification

Roo task: "Add Room entity + DAO + repository for Account."

Should separate Entity vs domain model or document single-model tradeoff per skill.
