# Windsurf Setup

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .windsurf/skills/compose-kotlin-agent-skills
```

Or global:

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git ~/.codeium/windsurf/skills/compose-kotlin-agent-skills
```

## Workspace Rules

Create `.windsurfrules` in project root (or append):

```markdown
## Android/Kotlin

Read `.windsurf/skills/compose-kotlin-agent-skills/SKILL.md` for all Kotlin/Compose work.
Load topic files from `references/` per SKILL.md routing table.
Never hardcode user-facing strings — use stringResource / strings.xml.
```

## Cascade Memory (optional)

Tell Cascade: "Remember: follow compose-kotlin-agent-skills in `.windsurf/skills/` for Android code."

## Verification

Ask Windsurf: "Structure a ViewModel with UiState using compose-kotlin-agent-skills."

Should cite `MutableStateFlow`, `collectAsStateWithLifecycle`, sealed/data UiState.
