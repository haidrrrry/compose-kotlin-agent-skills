# Goose (Block) Setup

Goose desktop agent reads extensions and instruction files.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .goose/skills/compose-kotlin-agent-skills
```

## Goose Instructions

Goose → Settings → Instructions → add:

```markdown
Android/Kotlin projects: read `.goose/skills/compose-kotlin-agent-skills/SKILL.md`.
Use `references/` subdirectory for detailed patterns.
Apply gotchas from SKILL.md before suggesting code.
```

## Extension / Recipe

Save as Goose recipe "android-kotlin":

```yaml
instructions: |
  Load .goose/skills/compose-kotlin-agent-skills/SKILL.md
  For Compose animations load references/03-animations.md
```

## Verification

Goose: "Explain spring dampingRatio tuning for button press per skill."

Should cite DampingRatioMediumBouncy + StiffnessHigh from references/03-animations.md.
