<p align="center">
  <img src="assets/logo.png" width="160" alt="compose-kotlin-agent-skills"/>
</p>

<h1 align="center">compose-kotlin-agent-skills</h1>

<p align="center">
  Make your AI coding agent actually understand <b>Jetpack Compose &amp; Kotlin</b> — on Android, Kotlin Multiplatform, and Compose Multiplatform.<br/>
  Strict MVI · Kotlin 2.x K2 · Compose 2026 · CI-validated · 27 agents supported.
</p>

<p align="center">
  <a href="#setup"><img src="https://img.shields.io/badge/setup-2%20min-brightgreen" alt="Setup time"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"/></a>
  <a href="https://github.com/haidrrrry/compose-kotlin-agent-skills/actions/workflows/skill-lint.yml"><img src="https://github.com/haidrrrry/compose-kotlin-agent-skills/actions/workflows/skill-lint.yml/badge.svg" alt="Skill Lint"/></a>
  <a href="agents/README.md"><img src="https://img.shields.io/badge/agents-27%2B-3DDC84?logo=android&logoColor=white" alt="Agents supported"/></a>
  <a href="SKILL.md"><img src="https://img.shields.io/badge/Kotlin-2.x%20K2-7F52FF?logo=kotlin&logoColor=white" alt="Kotlin"/></a>
  <a href="skills/android-kotlin-compose/SKILL.md"><img src="https://img.shields.io/badge/Jetpack%20Compose-2026-4285F4?logo=jetpackcompose&logoColor=white" alt="Compose"/></a>
  <a href="AGENTS.md"><img src="https://img.shields.io/badge/AGENTS.md-spec-818CF8" alt="AGENTS.md"/></a>
</p>

---

## The problem

AI coding agents generate Kotlin/Compose code that compiles but gets the details wrong:

- `_state.value = …` instead of atomic `_state.update { }` — race conditions
- `collectAsState()` instead of `collectAsStateWithLifecycle()` — battery drain
- Hardcoded UI strings instead of `stringResource(R.string.…)` — broken localisation
- `LazyColumn` without `key` + `contentType` — broken scroll, recomposition storms
- `GlobalScope.launch { }` inside ViewModels — leaks
- `mutableStateListOf` in ViewModel — survives config change wrong

This skill kit fixes that by giving your AI agent:

1. **A primary `SKILL.md`** with the 2026 toolchain, strict MVI guardrails, and an explicit **banned-antipatterns** table.
2. **3 modular sub-skills** (architecture, Compose, testing) loaded on demand.
3. **13 reference modules** covering every major Android/Kotlin topic.
4. **27 per-agent install guides** so Cursor, Claude Code, Codex, Copilot, Gemini, etc. each load it correctly.
5. **CI-validated** — every `SKILL.md` is frontmatter-linted, link-checked, and registered in `api/skills.lock` on every push.

---

## What this is NOT

| Wrong guess | Reality |
|---|---|
| Android library / Gradle dependency | **No** — nothing to `implementation(...)`. Pure markdown. |
| Alexa / Bixby / voice-assistant "skill" | **No** — not a voice platform. The word "skill" here = [agentskills.io](https://agentskills.io) format. |
| On-device LLM runtime / tool-calling SDK | **No** — no model inference, no agent framework. |
| Compose UI library (coachmarks, theming, charts) | **No** — we don't ship Composables; we teach how to write them. |
| Backend or REST API | **No** — markdown files plus a Python validator. |

**TL;DR:** clone this repo into your agent's skills folder. The agent reads it before writing Kotlin. That's it.

---

## What changes when you install it

| Area | Without the skill | With the skill |
|---|---|---|
| ViewModel state | `_state.value = ...` (race conditions) | Atomic `_state.update { it.copy(...) }` |
| Flow collection | `collectAsState()` (drains battery in background) | `collectAsStateWithLifecycle()` |
| UI text | Hardcoded `"Login"` literals | `stringResource(R.string.login)` |
| Lists | `LazyColumn` with no key | Stable `key` + `contentType` per item |
| Architecture | Mixed MVVM / state in Composable | Strict MVI — `UiState` + `UiEvent` + `UiEffect` |
| DI | `companion object Singleton` | `@HiltViewModel` + constructor injection |
| Navigation | String routes (deprecated) | Navigation 3 type-safe `NavKey` routes |
| Coroutines | `GlobalScope.launch { }` | `viewModelScope` + structured concurrency |
| Compose perf | Unstable params → constant recomposition | `@Stable` / `@Immutable` + deferred reads |
| Edge-to-edge | Status bar overlaps content | `enableEdgeToEdge()` + correct insets |
| Versions | Made up / outdated | Pinned to 2026 stable releases |

---

## Platforms

| | Supported |
|---|---|
| **Target (what the docs teach)** | Android · Kotlin Multiplatform · Compose Multiplatform |
| **Host (where the docs are read)** | macOS · Linux · Windows — anywhere your AI agent runs |
| **Agent compatibility** | 27 install guides (see [`agents/README.md`](agents/README.md)) |
| **Languages taught** | Kotlin 2.x (K2 compiler) |
| **Tooling enforced** | AGP 9, Compose BOM 2026, Navigation 3 |

---

## Skill catalog

| Skill | When the agent loads it |
|---|---|
| [`SKILL.md`](SKILL.md) (root) | Any Android / Kotlin / Compose work — toolchain, MVI guardrails, banned antipatterns |
| [`skills/android-kotlin-architecture/SKILL.md`](skills/android-kotlin-architecture/SKILL.md) | Clean Architecture, MVVM/MVI, modules, UseCases, `UiState` / `UiEvent` / `UiEffect` |
| [`skills/android-kotlin-compose/SKILL.md`](skills/android-kotlin-compose/SKILL.md) | Jetpack Compose UI, recomposition, Material 3, edge-to-edge, animations |
| [`skills/android-kotlin-testing/SKILL.md`](skills/android-kotlin-testing/SKILL.md) | ViewModel tests, Compose UI tests, Hilt fakes, Turbine |

Full routing index → [`AGENTS.md`](AGENTS.md)

---

## What's covered

| Topic | Reference | What the agent learns |
|---|---|---|
| Architecture | [`references/01-architecture.md`](references/01-architecture.md) | Clean Arch, MVVM, MVI, module structure |
| Compose UI | [`references/02-compose-ui.md`](references/02-compose-ui.md) | Composition, stability, Modifier order, theming |
| Animations | [`references/03-animations.md`](references/03-animations.md) | Springs, Canvas, gestures, shared elements |
| Coroutines & Flow | [`references/04-coroutines-flow.md`](references/04-coroutines-flow.md) | `StateFlow`, structured concurrency, error handling |
| Hilt DI | [`references/05-hilt-di.md`](references/05-hilt-di.md) | Scopes, `EntryPoint`, testing |
| Room | [`references/06-room-db.md`](references/06-room-db.md) | Migrations, offline-first, DAOs |
| Navigation | [`references/07-navigation.md`](references/07-navigation.md) | Navigation 3, type-safe routes, deep links |
| KMP / CMP | [`references/08-kmp-cmp.md`](references/08-kmp-cmp.md) | `expect`/`actual`, shared ViewModel, Ktor |
| Networking | [`references/09-networking.md`](references/09-networking.md) | Ktor, JWT, DTO mappers |
| Performance | [`references/10-performance.md`](references/10-performance.md) | Recomposition, `LazyColumn`, baseline profiles |
| Testing | [`references/11-testing.md`](references/11-testing.md) | Turbine, Compose UI tests, Hilt `TestInstallIn` |
| Camera & ML | [`references/12-camera-mlkit.md`](references/12-camera-mlkit.md) | CameraX, ML Kit pose, angle math |
| Release | [`references/13-release-checklist.md`](references/13-release-checklist.md) | Signing, R8, Play Store |

---

## How it works

```
You ask about Kotlin / Compose
        |
        v
  AI reads SKILL.md (routing + guardrails + banned antipatterns)
        |
        v
  Loads the right sub-skill
        |
        +-- skills/android-kotlin-architecture/SKILL.md
        +-- skills/android-kotlin-compose/SKILL.md
        +-- skills/android-kotlin-testing/SKILL.md
        |
        v
  Pulls topic reference
        |
        +-- references/01-architecture.md
        +-- references/02-compose-ui.md
        +-- references/04-coroutines-flow.md
        +-- ... 13 references total
        |
        v
  Writes code that follows the guardrails
```

**Layer 1: root skill** (`SKILL.md`) — single source of truth for toolchain versions, mandatory defaults, and banned antipatterns.

**Layer 2: sub-skills** (3 files) — focused playbooks loaded only when the task matches the domain.

**Layer 3: references** (13 files) — deep dives with WRONG/RIGHT pairs, decision matrices, pinned versions.

**Layer 4: validator** (`scripts/validate_skills.py`) — CI enforces frontmatter, link integrity, and skill-registry parity.

---

## File structure

```
compose-kotlin-agent-skills/
├── SKILL.md                              # Routing hub + MVI guardrails + banned antipatterns
├── AGENTS.md                             # agentskills.io meta-discovery index
├── CHANGELOG.md                          # Keep a Changelog · semver
├── ROADMAP.md                            # Planned milestones
├── api/
│   └── skills.lock                       # CI-tracked registry of every SKILL.md (md5)
├── skills/
│   ├── android-kotlin-architecture/SKILL.md
│   ├── android-kotlin-compose/SKILL.md
│   └── android-kotlin-testing/SKILL.md
├── references/                           # 13 topic deep-dives
├── agents/                               # 27 per-agent install guides + index
├── examples/                             # Real code from shipped apps
├── assets/
│   └── logo.png
├── scripts/
│   ├── validate_skills.py                # Frontmatter + link + lock validator (JUnit XML capable)
│   └── update_lock.sh                    # Regenerate api/skills.lock after editing any SKILL.md
└── .github/
    ├── workflows/skill-lint.yml          # CI: validator + JUnit report
    ├── pull_request_template.md
    └── ISSUE_TEMPLATE/                   # bug, feature, new-agent
```

---

## Setup {#setup}

The skill is just markdown. Every agent below reads the same content — pick yours.

### Cursor

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git \
  .cursor/skills/compose-kotlin-agent-skills
```

Cursor auto-discovers `.cursor/skills/*/SKILL.md`. For a rules-file alternative see [`agents/cursor.md`](agents/cursor.md).

### Claude Code

```bash
# Personal — available in all your projects
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git \
  ~/.claude/skills/compose-kotlin-agent-skills

# Project-specific
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git \
  .claude/skills/compose-kotlin-agent-skills
```

Add a 5-line block to your project's `CLAUDE.md` — see [`agents/claude.md`](agents/claude.md).

### Codex CLI (OpenAI)

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git
```

Then add a reference block to your project's root `AGENTS.md` — see [`agents/codex.md`](agents/codex.md).

### Gemini CLI

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git
```

Then add a reference block to `GEMINI.md` — see [`agents/gemini.md`](agents/gemini.md).

### GitHub Copilot

Clone into `.github/skills/compose-kotlin-agent-skills/` and add a block to `.github/copilot-instructions.md` — see [`agents/copilot.md`](agents/copilot.md).

### Other agents (22 more)

Windsurf · Kimi · DeepSeek · Cline · Aider · Continue.dev · OpenCode · Zed · Amazon Q · JetBrains AI / Junie · Sourcegraph Cody · Replit Agent · Augment · Roo Code · Goose · OpenHands · Qwen Code · Trae · Tabnine · Factory Droid · Devin · Bolt.new

Full table → [`agents/README.md`](agents/README.md)
Paste-anywhere snippet → [`agents/_shared-snippet.md`](agents/_shared-snippet.md)

---

## Quick example

After setup, talk to your AI agent normally:

```
"My LazyColumn jank — fix it."
```

What happens:

1. Agent reads `SKILL.md` for the routing rules.
2. Loads `skills/android-kotlin-compose/SKILL.md` and `references/10-performance.md`.
3. Checks your code for missing `key` / `contentType`, unstable items, heavy work in item blocks.
4. Returns a fix that follows the guardrails — `key = { it.id }`, `@Immutable` data class, `derivedStateOf` where appropriate.

No hallucinated APIs. No `GlobalScope`. No `_state.value = …`.

---

## Validate locally

```bash
python3 scripts/validate_skills.py --strict --lock-check api/skills.lock
```

CI runs the same command on every push and pull request. If you edit any `SKILL.md`:

```bash
./scripts/update_lock.sh
```

Then commit `api/skills.lock` alongside your change.

---

## FAQ

### Best Kotlin / Compose skill for Cursor?

Clone this repo into `.cursor/skills/compose-kotlin-agent-skills` and point Cursor rules at `SKILL.md`. Covers Compose, MVI, Hilt, Room, Navigation 3, and the banned-antipatterns table.

### How do I add Kotlin rules to Claude Code?

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git ~/.claude/skills/compose-kotlin-agent-skills
```

Claude auto-discovers `SKILL.md` in the skills folder.

### MVVM vs MVI — which does this enforce?

**MVI** with atomic `StateFlow` updates. `UiState` + `UiEvent` + `UiEffect`. Naked state assignment (`_state.value = ...`) is explicitly banned.

### Kotlin Multiplatform / Compose Multiplatform?

See [`references/08-kmp-cmp.md`](references/08-kmp-cmp.md) — shared ViewModel, `expect`/`actual`, Ktor networking, SQLDelight vs Room.

### Is this a Compose UI library or an Alexa skill?

**No.** It's markdown instructions for coding AIs — clone with `git`, not `implementation(...)`. The word "skill" follows the [agentskills.io](https://agentskills.io) format, unrelated to voice assistants.

---

## Contributing

PRs welcome — see [`.github/pull_request_template.md`](.github/pull_request_template.md).

Every new sub-skill must:

1. Live under `skills/<kebab-case-name>/SKILL.md` with valid frontmatter.
2. Pass `python3 scripts/validate_skills.py --strict`.
3. Be registered in [`AGENTS.md`](AGENTS.md#skill-catalog).
4. Bump [`api/skills.lock`](api/skills.lock) via `./scripts/update_lock.sh`.

## License

MIT — see [LICENSE](LICENSE).

Author: **[haidrrrry](https://github.com/haidrrrry)**
