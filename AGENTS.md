# AGENTS.md — compose-kotlin-agent-skills

Enterprise Android/Kotlin agent skill kit. Plain-text index for agentic IDEs (Cursor, Claude Code, Codex, Gemini, Copilot, Windsurf, OpenHands, and 20+ others).

**Repository:** https://github.com/haidrrrry/compose-kotlin-agent-skills  
**Primary skill:** [`SKILL.md`](SKILL.md) — read this first for every Kotlin/Android task.

## Build & Validation

```bash
# Validate all SKILL.md files (frontmatter + links) — must pass before merge
python3 scripts/validate_skills.py

# Strict mode + lock parity + JUnit report (matches CI exactly)
python3 scripts/validate_skills.py \
  --strict \
  --lock-check api/skills.lock \
  --junit junit-results.xml

# When you add or remove a SKILL.md, regenerate the lock file:
python3 scripts/validate_skills.py --write-lock api/skills.lock
```

CI runs the same script on every push and pull request (`.github/workflows/skill-lint.yml`) and uploads `junit-results.xml` as an artifact.

## Skill Catalog

| Skill | Path | Load When |
|-------|------|-----------|
| **compose-kotlin-agent-skills** (primary) | [`SKILL.md`](SKILL.md) | Any Android/Kotlin/Compose work — toolchain, MVI guardrails, banned antipatterns |
| **android-kotlin-architecture** | [`skills/android-kotlin-architecture/SKILL.md`](skills/android-kotlin-architecture/SKILL.md) | Clean Architecture, MVVM/MVI, modules, UseCases, UiState/Event/Effect |
| **android-kotlin-compose** | [`skills/android-kotlin-compose/SKILL.md`](skills/android-kotlin-compose/SKILL.md) | Compose UI, recomposition, Material 3, edge-to-edge, animations, performance |
| **android-kotlin-testing** | [`skills/android-kotlin-testing/SKILL.md`](skills/android-kotlin-testing/SKILL.md) | ViewModel tests, Compose UI tests, Hilt fakes, Turbine, CI quality gates |

## Reference Modules (deep dives)

Load from `references/` after reading the matching skill above. One level deep only — do not chain reference-to-reference.

### Architecture & Platform

| Reference | Topic |
|-----------|-------|
| [`references/01-architecture.md`](references/01-architecture.md) | Clean Arch, MVVM, MVI, module structure |
| [`references/04-coroutines-flow.md`](references/04-coroutines-flow.md) | StateFlow, structured concurrency, errors |
| [`references/05-hilt-di.md`](references/05-hilt-di.md) | Hilt, scopes, EntryPoint, testing |
| [`references/06-room-db.md`](references/06-room-db.md) | Room, migrations, offline-first |
| [`references/07-navigation.md`](references/07-navigation.md) | Navigation 3, type-safe routes, deep links |
| [`references/08-kmp-cmp.md`](references/08-kmp-cmp.md) | KMP, expect/actual, shared ViewModel |
| [`references/09-networking.md`](references/09-networking.md) | Ktor, JWT, DTO mappers |

### Compose & Performance

| Reference | Topic |
|-----------|-------|
| [`references/02-compose-ui.md`](references/02-compose-ui.md) | Composition, stability, Modifier order, theming |
| [`references/03-animations.md`](references/03-animations.md) | Springs, Canvas, gestures, shared elements |
| [`references/10-performance.md`](references/10-performance.md) | Recomposition, LazyColumn, baseline profiles |

### Quality & Ship

| Reference | Topic |
|-----------|-------|
| [`references/11-testing.md`](references/11-testing.md) | Turbine, Compose tests, Hilt TestInstallIn |
| [`references/12-camera-mlkit.md`](references/12-camera-mlkit.md) | CameraX, ML Kit pose, angle math |
| [`references/13-release-checklist.md`](references/13-release-checklist.md) | Signing, R8, Play Store |

## Agent Install Guides (27 platforms)

Directory: [`agents/`](agents/) · Index: [`agents/README.md`](agents/README.md) · Paste snippet: [`agents/_shared-snippet.md`](agents/_shared-snippet.md)

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git <agent-dir>/skills/compose-kotlin-agent-skills
```

Replace `<agent-dir>` per agent (`.cursor`, `.claude`, `.codex`, `.windsurf`, etc.) — see the matching file in `agents/`.

## Production Code Examples

| Example | Source repo |
|---------|-------------|
| [`examples/animated-clock/`](examples/animated-clock/) | [AnimatedClockJetpacl](https://github.com/haidrrrry/AnimatedClockJetpacl) — Canvas, CMP, particles |
| [`examples/authenticator/`](examples/authenticator/) | [Authenticator](https://github.com/haidrrrry/Authenticator) — Room, MVVM, Koin, theming |

## Boundaries — Do Not

- Invent dependency versions — use the version table in `SKILL.md`
- Use `GlobalScope`, naked `_state.value =`, or hardcoded UI strings
- Skip `LazyColumn` keys or use `collectAsState()` on Android screens
- Merge without passing `python3 scripts/validate_skills.py --strict --lock-check api/skills.lock`
- Add reference files without linking them from `SKILL.md` or this index
- Add a new `SKILL.md` without bumping [`api/skills.lock`](api/skills.lock) and the catalog table above

## Verification Prompt

```
Read AGENTS.md and SKILL.md. Structure a Navigation 3 screen with MVI UiState,
edge-to-edge insets, and collectAsStateWithLifecycle. Cite banned antipatterns you avoided.
```

Expected: Kotlin 2.x, AGP 9, `_state.update { }`, `stringResource`, NavKey routes, no GlobalScope.
