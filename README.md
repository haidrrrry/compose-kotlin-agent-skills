<div align="center">

<img src="assets/logo.png" alt="Jetpack Compose and Kotlin AI agent skills for Cursor Claude Code and Codex" width="220" />

# compose-kotlin-agent-skills

**Jetpack Compose & Kotlin AI agent skills — Cursor, Claude Code, Codex, Gemini & 27+ agents.**

Production Android patterns · strict MVI · Kotlin 2.x K2 · Compose 2026 · CI-validated · not docs copy-paste.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skill Lint](https://github.com/haidrrrry/compose-kotlin-agent-skills/actions/workflows/skill-lint.yml/badge.svg)](https://github.com/haidrrrry/compose-kotlin-agent-skills/actions/workflows/skill-lint.yml)
[![Agents Supported](https://img.shields.io/badge/agents-27%2B-3DDC84?logo=android&logoColor=white)](agents/README.md)
[![Kotlin](https://img.shields.io/badge/Kotlin-2.x%20K2-7F52FF?logo=kotlin&logoColor=white)](SKILL.md)
[![Jetpack Compose](https://img.shields.io/badge/Jetpack%20Compose-2026-4285F4?logo=jetpackcompose&logoColor=white)](skills/android-kotlin-compose/SKILL.md)
[![AGENTS.md](https://img.shields.io/badge/AGENTS.md-spec-818CF8)](AGENTS.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](.github/pull_request_template.md)

[**Install**](#install) ·
[**Skill catalog**](AGENTS.md#skill-catalog) ·
[**Agents**](agents/README.md) ·
[**FAQ**](#faq) ·
[**Roadmap**](ROADMAP.md)

</div>

> **One-line install (Cursor):**
> `git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .cursor/skills/compose-kotlin-agent-skills`

---

## What is this?

**compose-kotlin-agent-skills** is an open-source **Android AI rules / agent skill** pack for coding assistants. It teaches agents how to write real **Kotlin**, **Jetpack Compose**, **MVVM/MVI**, **Hilt**, **Room**, **Navigation 3**, and **coroutines** code — with WRONG/RIGHT pairs, banned antipatterns, and pinned 2026 dependency versions.

Works with: **Cursor rules**, **Claude Code skills**, **OpenAI Codex AGENTS.md**, **Gemini CLI**, **GitHub Copilot**, **Windsurf**, **Cline**, **Aider**, **Continue**, and [20+ more](agents/README.md).

---

## Why use this over other Compose skills?

| Other skills | compose-kotlin-agent-skills |
|---|---|
| Docs copy-paste | Production patterns from shipped apps |
| Toy ViewModels | Strict MVI — `_state.update { }` only |
| No antipatterns list | Bans `GlobalScope`, `collectAsState()`, hardcoded strings |
| No CI | Every `SKILL.md` linted on every PR |
| Single agent | 27 agent install guides |

Backed by [AnimatedClockJetpacl](https://github.com/haidrrrry/AnimatedClockJetpacl) · [Authenticator](https://github.com/haidrrrry/Authenticator) · [RepLock](https://github.com/haidrrrry/RepLockPushupAppBlocker).

---

## Install {#install}

### Cursor (most popular)

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git \
  .cursor/skills/compose-kotlin-agent-skills
```

See [`agents/cursor.md`](agents/cursor.md) for `.cursor/rules` setup.

### Claude Code

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git \
  ~/.claude/skills/compose-kotlin-agent-skills
```

### Codex CLI · Gemini CLI · Copilot · Windsurf · Kimi · DeepSeek

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git
```

Then follow your agent guide in [`agents/`](agents/README.md) — each file has the exact path (`AGENTS.md`, `GEMINI.md`, `.github/skills/`, etc.).

---

## Skill catalog

| Skill | Load when |
|---|---|
| [`SKILL.md`](SKILL.md) | Any Android / Kotlin / Compose task |
| [`android-kotlin-architecture`](skills/android-kotlin-architecture/SKILL.md) | Clean Architecture, MVVM, MVI, UiState/Event/Effect |
| [`android-kotlin-compose`](skills/android-kotlin-compose/SKILL.md) | Jetpack Compose UI, recomposition, Material 3, edge-to-edge |
| [`android-kotlin-testing`](skills/android-kotlin-testing/SKILL.md) | ViewModel tests, Compose UI tests, Hilt fakes, Turbine |

Full routing index → [`AGENTS.md`](AGENTS.md)

---

## What's inside

- **13 reference modules** — architecture, Compose UI, animations, coroutines, Hilt, Room, Navigation 3, KMP, networking, performance, testing, CameraX/ML Kit, Play Store release
- **Banned antipatterns** — `GlobalScope`, naked `_state.value =`, `collectAsState()`, `mutableStateListOf` in ViewModel
- **2026 toolchain** — Kotlin 2.x K2, AGP 9, Compose BOM 2026, Navigation 3
- **CI validator** — `python3 scripts/validate_skills.py --strict --lock-check api/skills.lock`

---

## FAQ {#faq}

### Best Android agent skill for Cursor?

Clone this repo into `.cursor/skills/compose-kotlin-agent-skills` and point Cursor rules at `SKILL.md`. Covers Compose, MVI, Hilt, Room, and banned AI hallucinations.

### How do I add Kotlin rules to Claude Code?

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git ~/.claude/skills/compose-kotlin-agent-skills
```

Claude auto-discovers `SKILL.md` in the skills folder.

### Jetpack Compose cursor rules / AGENTS.md?

Paste [`agents/_shared-snippet.md`](agents/_shared-snippet.md) into your project's `AGENTS.md` or `.cursor/rules`. Forces `collectAsStateWithLifecycle`, `_state.update`, and `stringResource`.

### Does this work with GitHub Copilot?

Yes — see [`agents/copilot.md`](agents/copilot.md). Install under `.github/skills/compose-kotlin-agent-skills`.

### MVVM vs MVI — which does this skill enforce?

**MVI** with atomic `StateFlow` updates. `UiState` + `UiEvent` + `UiEffect`. Naked state assignment is explicitly banned.

### Kotlin Multiplatform / Compose Multiplatform?

See [`references/08-kmp-cmp.md`](references/08-kmp-cmp.md) — shared ViewModel, expect/actual, Ktor networking.

---

## Validate locally

```bash
python3 scripts/validate_skills.py --strict --lock-check api/skills.lock
```

---

## Contributing

PRs welcome — [`pull_request_template.md`](.github/pull_request_template.md)

Author: **[haidrrrry](https://github.com/haidrrrry)**

## License

MIT
