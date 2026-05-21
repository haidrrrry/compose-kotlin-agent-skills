<!-- Thanks for contributing to compose-kotlin-agent-skills. -->
<!-- Keep PRs focused: one skill change, one reference update, or one agent guide per PR. -->

## What this PR changes

<!-- 1–3 sentences. What did you add / change / remove? Which sub-skill or reference? -->

## Why

<!-- What gap, hallucination pattern, toolchain change, or audit finding drove this? -->

## Scope checklist

Mark all that apply:

- [ ] Root `SKILL.md`
- [ ] Sub-skill under `skills/<name>/SKILL.md`
- [ ] Reference under `references/`
- [ ] Agent install guide under `agents/`
- [ ] Example under `examples/`
- [ ] CI / validator (`scripts/`, `.github/workflows/`)
- [ ] Repo meta (README, CHANGELOG, ROADMAP, assets)

## Quality gates (must all pass)

- [ ] `python3 scripts/validate_skills.py --strict` is green locally.
- [ ] If any `SKILL.md` changed: ran `./scripts/update_lock.sh` and committed `api/skills.lock`.
- [ ] All new code blocks are real, compiling Kotlin / Gradle / YAML — no pseudocode.
- [ ] Pinned versions match the latest stable on the date of this PR.
- [ ] No banned antipatterns introduced (`GlobalScope`, naked `_state.value =`, `collectAsState()`, hardcoded UI strings, `mutableStateListOf` in ViewModel, unscoped DI).
- [ ] Any new SKILL added is registered in [`AGENTS.md`](../AGENTS.md#skill-catalog).
- [ ] `CHANGELOG.md` entry added under `[Unreleased]`.

## Screenshots / output (optional)

<!-- For README/docs/branding changes. Drag images here. -->

## Related issues

<!-- Closes #123, refs #456 -->
