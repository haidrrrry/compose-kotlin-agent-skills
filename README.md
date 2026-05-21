<div align="center">

<img src="assets/logo.png" alt="compose-kotlin-agent-skills" width="220" />

# compose-kotlin-agent-skills

**Enterprise-grade Android/Kotlin Agent Skill for 27+ AI coding agents.**
Strict MVI · 2026 toolchain · banned antipatterns · CI-validated.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skill Lint](https://github.com/haidrrrry/compose-kotlin-agent-skills/actions/workflows/skill-lint.yml/badge.svg)](https://github.com/haidrrrry/compose-kotlin-agent-skills/actions/workflows/skill-lint.yml)
[![Agents Supported](https://img.shields.io/badge/agents-27%2B-3DDC84?logo=android&logoColor=white)](agents/README.md)
[![Kotlin](https://img.shields.io/badge/Kotlin-2.x%20K2-7F52FF?logo=kotlin&logoColor=white)](SKILL.md)
[![Compose](https://img.shields.io/badge/Jetpack%20Compose-2026-4285F4?logo=jetpackcompose&logoColor=white)](skills/android-kotlin-compose/SKILL.md)
[![AGENTS.md](https://img.shields.io/badge/AGENTS.md-spec-818CF8)](AGENTS.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](.github/pull_request_template.md)

[**Skill Catalog**](AGENTS.md#skill-catalog) ·
[**Install**](#install) ·
[**Agents**](agents/README.md) ·
[**References**](references/) ·
[**Roadmap**](ROADMAP.md) ·
[**Changelog**](CHANGELOG.md)

</div>

---

## Why this skill exists

Every Compose skill on GitHub is shallow — official docs copy-paste, no tradeoffs, toy examples. This kit ships:

- **Strict MVI guardrails** — `_state.update { ... }` only. Naked `_state.value = ...` is banned.
- **2026 toolchain** — Kotlin 2.x K2, AGP 9, Compose BOM 2026, Navigation 3, edge-to-edge by default.
- **Banned antipatterns list** — `GlobalScope`, `collectAsState()`, `mutableStateListOf` in ViewModel, hardcoded UI strings, all flagged with the correct fix.
- **CI-validated** — every `SKILL.md` is frontmatter-linted and link-checked on every push.
- **27+ agent setups** — Cursor, Claude Code, Codex, Gemini CLI, Copilot, Windsurf, Kimi, DeepSeek, Cline, Aider, Continue, Zed, Cody, JetBrains AI, Replit, Devin, Factory, and more.
- **Real production code** — backed by [AnimatedClockJetpacl](https://github.com/haidrrrry/AnimatedClockJetpacl) and [Authenticator](https://github.com/haidrrrry/Authenticator).

## Skill catalog

| Skill | When to load |
|---|---|
| [`SKILL.md`](SKILL.md) (root) | Any Android/Kotlin/Compose work — toolchain, MVI guardrails, banned antipatterns |
| [`skills/android-kotlin-architecture`](skills/android-kotlin-architecture/SKILL.md) | Clean Architecture, MVVM/MVI, modules, UseCases, UiState/Event/Effect |
| [`skills/android-kotlin-compose`](skills/android-kotlin-compose/SKILL.md) | Compose UI, recomposition, Material 3, edge-to-edge, animations, performance |
| [`skills/android-kotlin-testing`](skills/android-kotlin-testing/SKILL.md) | ViewModel tests, Compose UI tests, Hilt fakes, Turbine, CI quality gates |

Routing rules + full reference index live in [`AGENTS.md`](AGENTS.md).

## Install

<details open>
<summary><b>Cursor</b></summary>

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git \
  .cursor/skills/compose-kotlin-agent-skills
```
Or add as a Cursor rule — see [`agents/cursor.md`](agents/cursor.md).
</details>

<details>
<summary><b>Claude Code / Claude CLI</b></summary>

```bash
# Global
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git \
  ~/.claude/skills/compose-kotlin-agent-skills

# Per-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git \
  .claude/skills/compose-kotlin-agent-skills
```
</details>

<details>
<summary><b>Codex CLI / OpenAI Codex</b></summary>

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git
# Then add reference block to AGENTS.md — see agents/codex.md
```
</details>

<details>
<summary><b>Gemini CLI</b></summary>

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git
# Then add reference block to GEMINI.md — see agents/gemini.md
```
</details>

<details>
<summary><b>Other agents (23 more)</b></summary>

Windsurf, Kimi, DeepSeek, Cline, Aider, Continue.dev, OpenCode, Zed, Amazon Q, JetBrains AI, Sourcegraph Cody, Replit Agent, Augment, Roo Code, Goose, OpenHands, Qwen Code, Trae, Tabnine, Factory Droid, Devin, Bolt, GitHub Copilot.

Full table → [`agents/README.md`](agents/README.md)
Universal snippet → [`agents/_shared-snippet.md`](agents/_shared-snippet.md)
</details>

## Validate locally

```bash
# Frontmatter + link check (matches CI)
python3 scripts/validate_skills.py --strict
```

Want CI on your fork? `.github/workflows/skill-lint.yml` runs the same script on every push / PR.

## Repository layout

```
compose-kotlin-agent-skills/
├── SKILL.md                        # Root skill — routing hub + MVI guardrails + banned antipatterns
├── AGENTS.md                       # agentskills.io meta-discovery index
├── README.md                       # This file
├── CHANGELOG.md                    # Semver-tagged release history
├── ROADMAP.md                      # What's planned next
├── api/
│   └── skills.lock                 # CI-tracked skill registry (no new SKILL.md without bump)
├── skills/
│   ├── android-kotlin-architecture/SKILL.md
│   ├── android-kotlin-compose/SKILL.md
│   └── android-kotlin-testing/SKILL.md
├── references/                     # 13 deep-dive files (architecture → release)
├── agents/                         # 27 per-agent setup guides
├── modules/README.md               # Logical grouping of references
├── examples/                       # Real code from shipped apps
├── assets/
│   └── logo.png                    # Repo brand
├── scripts/
│   └── validate_skills.py          # Frontmatter + link validator (JUnit XML capable)
└── .github/
    ├── workflows/skill-lint.yml    # CI: validator + JUnit report
    ├── pull_request_template.md
    └── ISSUE_TEMPLATE/             # bug, feature, new-agent
```

## What makes the patterns different

- **WRONG / RIGHT pairs** on every concept — naked `_state.value =` next to the `_state.update` fix.
- **Decision matrices** — StateFlow vs SharedFlow vs Channel, Hilt vs Koin, Room vs DataStore, Compose Navigation vs Nav 3.
- **Anti-rationalisations** — pre-written rebuttals for when an agent tries to skip `collectAsStateWithLifecycle`, ignore process death, or hardcode strings.
- **Production gotchas** — bugs that only appear after Play Store rollout (R8, baseline profile drift, recomposition storms).
- **Pinned versions** — every reference snippet locks the dependency version it was written for.

## Contributing

PRs welcome — see the [PR template](.github/pull_request_template.md). Every new sub-skill must:

1. Live under `skills/<kebab-case-name>/SKILL.md`.
2. Pass `python3 scripts/validate_skills.py --strict`.
3. Be added to [`AGENTS.md`](AGENTS.md#skill-catalog) routing table.
4. Bump [`api/skills.lock`](api/skills.lock).

## License

MIT © [haidrrrry](https://github.com/haidrrrry)
