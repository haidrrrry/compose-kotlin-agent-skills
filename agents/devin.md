# Devin Setup

Cognition Devin uses `devin.md` or project knowledge for repo-specific rules.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git devin-skills/compose-kotlin-agent-skills
```

## devin.md

Create `devin.md` in repo root:

```markdown
## Android Engineering — compose-kotlin-agent-skills

Read `devin-skills/compose-kotlin-agent-skills/SKILL.md` for all Kotlin/Compose work.
References: `devin-skills/compose-kotlin-agent-skills/references/`.

When creating PRs: verify LazyColumn keys, lifecycle-aware collection, Room migrations exist.
Do not use fallbackToDestructiveMigration in production.
```

## Devin Knowledge

Upload SKILL.md + relevant reference files to Devin Knowledge for the session.

## Verification

Devin plan should cite skill paths when scaffolding Android features.
