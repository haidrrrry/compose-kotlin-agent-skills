# Qwen Code CLI Setup

Alibaba Qwen Code agent (CLI) — similar to Claude Code / Codex patterns.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .qwen/skills/compose-kotlin-agent-skills
```

## QWEN.md

Create `QWEN.md` in project root:

```markdown
## compose-kotlin-agent-skills

Path: `.qwen/skills/compose-kotlin-agent-skills/`

Read `SKILL.md` before Android/Kotlin tasks.
Read `references/<topic>.md` for specific domains.
中文/English both OK — code patterns stay Kotlin idiomatic.
```

## CLI

```bash
qwen "阅读 SKILL.md，用 MVVM 实现带搜索的账户列表"
```

## Verification

Should output `combine()` + `MutableStateFlow` search pattern from Authenticator example.
