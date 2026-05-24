# Changelog

All notable changes to **compose-kotlin-agent-skills** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Live verification prompt (skill self-test against a sample diff).
- KMP/CMP sub-skill split out of `references/08-kmp-cmp.md`.
- Per-agent install snippets translated to Japanese / Korean / Mandarin.
- Reference snippet compiler — compile all `examples/` and reference code blocks in CI.

## [2.2.0] — 2026-05-21

### Added
- **7 new reference modules** — `00-banned-antipatterns`, `14-datastore`, `15-paging3`, `16-coil-image`, `17-accessibility`, `18-gradle-build-logic`, `19-xml-to-compose-migration` (YAML frontmatter, 3+ WRONG/RIGHT pairs each, 2026 pinned versions).
- **`examples/todo-mvi/`** — MVI todo reference (`TodoViewModel`, `TodoScreen`, `TodoRepository`) with antipattern callouts.
- **REVIEW MODE** in `skills/android-kotlin-compose/SKILL.md` — 6-point silent audit checklist for composable/screen reviews.
- README — Quick install table, Review mode section, star history badge, 20-reference coverage table.
- AGENTS.md — all new references catalogued; `todo-mvi` example linked.

### Changed
- Root `SKILL.md` — banned table extracted to `references/00-banned-antipatterns.md`; routing table extended to 00–19; version `2.2.0`.
- `skills/android-kotlin-compose/SKILL.md` — split into REVIEW MODE + AUTHORING MODE; trigger phrases in description.

### Removed
- Inline banned-antipatterns table from root `SKILL.md` (moved to dedicated reference file).

## [2.1.0] — 2026-05-21

### Added
- **Root brand** — `assets/logo.png`, badges, value prop above the fold in `README.md`.
- `CHANGELOG.md`, `ROADMAP.md`, `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/{bug_report,feature_request,new_agent.md}`.
- `api/skills.lock` — registry of every `SKILL.md` + md5 hash. CI fails if a skill is added or removed without a lock bump.
- `scripts/validate_skills.py --junit <path>` — emit JUnit XML for CI test reporters.
- `scripts/validate_skills.py --lock-check api/skills.lock` — enforce registry parity.
- Concurrency guard in `.github/workflows/skill-lint.yml` — cancel superseded runs on the same ref.

### Changed
- `README.md` rewritten with collapsible install sections, skill catalog table, repo-layout tree.
- `.github/workflows/skill-lint.yml` now uploads `junit-results.xml` as a workflow artifact and runs `--lock-check` in strict mode.

## [2.0.0] — 2026-05-20

### Added
- **2026 toolchain enforcement** in `SKILL.md` — Kotlin 2.x K2, AGP 9, Compose BOM 2026, Navigation 3, edge-to-edge by default.
- **Strict MVI guardrails** — `_state.update { ... }` only, banned `_state.value = ...` and `mutableStateListOf` in ViewModel.
- **Banned Antipatterns** section — `GlobalScope`, `collectAsState()`, hardcoded UI strings, unscoped DI, etc.
- **Root `AGENTS.md`** — `agentskills.io`-style meta-discovery index with skill catalog, routing rules, boundaries.
- **Modular sub-skills** —
  - `skills/android-kotlin-architecture/SKILL.md`
  - `skills/android-kotlin-compose/SKILL.md`
  - `skills/android-kotlin-testing/SKILL.md`
- `scripts/validate_skills.py` — frontmatter + internal link validator with `--strict` mode.
- `.github/workflows/skill-lint.yml` — CI enforcement on every push and PR.

### Changed
- Root `SKILL.md` restructured around routing → sub-skills + reference modules.
- All 27 agent install guides now point to `https://github.com/haidrrrry/compose-kotlin-agent-skills.git`.

## [1.0.0] — 2026-05-19

### Added
- Initial release.
- `SKILL.md` covering architecture, Compose, animations, coroutines, Hilt, Room, navigation, KMP, networking, performance, testing, camera/ML, release.
- 13 reference files in `references/`.
- 27 per-agent setup files in `agents/`.
- `examples/animated-clock/` and `examples/authenticator/` snippets.
- MIT license.

[Unreleased]: https://github.com/haidrrrry/compose-kotlin-agent-skills/compare/v2.2.0...HEAD
[2.2.0]: https://github.com/haidrrrry/compose-kotlin-agent-skills/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/haidrrrry/compose-kotlin-agent-skills/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/haidrrrry/compose-kotlin-agent-skills/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/haidrrrry/compose-kotlin-agent-skills/releases/tag/v1.0.0
