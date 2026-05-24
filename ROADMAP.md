# Roadmap

Living document. Reordered as agents adopt patterns. PRs welcome on any item.

Legend: `[ ]` planned · `[~]` in progress · `[x]` shipped

## Q3 2026 — Depth

- [~] Split `references/08-kmp-cmp.md` into its own `skills/android-kotlin-kmp/` sub-skill with Ktor + SQLDelight matrix.
- [ ] `skills/android-kotlin-camera-mlkit/` — pose detection, 1€ filter, real angle math, extracted from `references/12`.
- [ ] `skills/android-kotlin-release/` — R8 rules, baseline profiles, Play Store checklist, extracted from `references/13`.
- [~] WRONG/RIGHT diff harness — every banned antipattern paired with a working fix snippet, lint-checked (`00-banned-antipatterns.md` shipped).
- [ ] Reference snippet compiler — auto-extract code blocks from `references/*.md` + `examples/todo-mvi/` into a Gradle project that compiles in CI.
- [ ] GitHub Releases workflow — semver tags + tarball downloads per CHANGELOG version.

## Q4 2026 — Verification

- [ ] **Self-test prompt** — `tests/prompts/` directory with golden agent transcripts. CI replays them against a frozen model and asserts the skill is loaded + guardrails are applied.
- [ ] Compose recomposition counter snippets validated against Modifier.Node API.
- [ ] Hilt 2.x → KSP-only migration appendix.
- [ ] Material 3 Expressive token additions once stable.

## Q1 2027 — Reach

- [ ] Translations: 日本語, 한국어, 简体中文, Português (BR) for all 27 agent guides.
- [ ] Video walkthroughs embedded in `README.md` (per sub-skill).
- [ ] GitHub Pages docs site (Docsify-based) at `https://haidrrrry.github.io/compose-kotlin-agent-skills`.
- [ ] Anchor permalinks in every `SKILL.md` heading so agents can deep-link to a single guardrail.

## Continuous

- [ ] Track new Android/Kotlin/Compose stable releases within 14 days — bump pinned versions in references.
- [ ] Track new AI agents — add an install guide for each within 30 days of GA.
- [ ] Quarterly audit of `Banned Antipatterns` — drop fixed AI hallucinations, add newly-observed ones.

## Done

- [x] Root `AGENTS.md` (`agentskills.io`).
- [x] CI lint workflow (`.github/workflows/skill-lint.yml`).
- [x] Frontmatter + link validator (`scripts/validate_skills.py --strict`).
- [x] 27-agent install matrix in `agents/`.
- [x] Strict MVI guardrails + banned antipatterns in root `SKILL.md`.
- [x] Sub-skills split: architecture, compose, testing.
- [x] Repo brand: logo, badges, README rewrite, CHANGELOG, ROADMAP, PR + issue templates.
- [x] `api/skills.lock` registry + `--lock-check`.
- [x] References 00 + 14–19 (DataStore, Paging3, Coil, a11y, Gradle, XML migration).
- [x] Banned antipatterns extracted to `references/00-banned-antipatterns.md`.
- [x] Compose REVIEW MODE (6-point audit checklist).
- [x] `examples/todo-mvi/` MVI reference implementation.

## How to propose changes

1. Open an issue using [`feature_request`](.github/ISSUE_TEMPLATE/feature_request.md) describing the gap.
2. Reference the audit dimension it addresses (architecture, recomposition, testing, release, …).
3. PR against `main` — see [`pull_request_template.md`](.github/pull_request_template.md).
