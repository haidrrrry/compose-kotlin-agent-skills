# Bolt.new / StackBlitz Setup

For web-based agents — copy skill into repo or sync from GitHub.

## Install

Import repo or add subtree:

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git skills/compose-kotlin-agent-skills
```

Bolt does not run native Android builds — use skill for **Kotlin/Compose code generation** and architecture guidance only.

## bolt.md / AGENTS.md

```markdown
## compose-kotlin-agent-skills

Read `skills/compose-kotlin-agent-skills/SKILL.md` when generating Kotlin or Compose code.
Note: Bolt environment may not compile Android — output must still follow skill patterns.
```

## Verification

Generated Compose should include `modifier` param, tokens, no hardcoded strings.
