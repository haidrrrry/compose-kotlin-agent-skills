# Contributing to compose-kotlin-agent-skills

Thank you for helping keep this skill kit honest. The goal is simple: every rule in every `SKILL.md` must reflect what actually works in 2026 Android development — not what was correct three or four years ago.

---

## What you can contribute

| Type | Examples |
|------|---------|
| **New antipattern** | A wrong pattern your agent keeps generating that isn't in the banned list yet |
| **Stale rule fix** | A version pin, API call, or best practice that has become outdated |
| **New reference module** | A missing topic (e.g. `WorkManager`, `DataStore`, `Media3`) |
| **New agent install guide** | A `agents/<agent-name>.md` for a supported agent not yet covered |
| **CI / tooling** | Improvements to frontmatter linting or md5 lock scripts |
| **Typo / clarity** | Wording that confused you or your agent |

---

## Ground rules

- **Every rule must be testable.** If you can't point to an agent output or a compiler error that proves the rule is needed, it probably doesn't belong.
- **Wrong pattern + correct fix, always together.** The banned-antipatterns table format exists so agents see both sides. Don't add a "don't do X" without a "do Y instead."
- **Version-pin everything.** Vague advice like "use the latest BOM" is useless. Pin the exact version.
- **No opinions without evidence.** Performance claims need a benchmark or a link to one.

---

## How to contribute

### 1. Fork and clone

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git
cd compose-kotlin-agent-skills
```

### 2. Make your change

- Editing an existing skill → find the relevant `SKILL.md` and edit in place.
- Adding a new reference module → create `references/<topic>/SKILL.md` following the existing module structure.
- Adding a new agent guide → create `agents/<agent-name>.md` (install steps + verification).

### 3. Run the CI checks locally

```bash
# Lint frontmatter on all SKILL.md files
./scripts/lint-frontmatter.sh

# Regenerate md5 locks (required after any SKILL.md edit)
./scripts/lock-skills.sh
```

Both scripts must pass with zero errors before you open a PR. CI will rerun them on push — a red check means your PR won't be merged.

### 4. Open a pull request

Use the template below as your PR description:

```
## What changed
<!-- One-line summary -->

## Why
<!-- What agent output, compiler error, or breaking change prompted this? -->

## Evidence
<!-- Link, screenshot, or code snippet that proves the rule is correct -->

## Checklist
- [ ] `lint-frontmatter.sh` passes locally
- [ ] `lock-skills.sh` run and md5 hashes updated
- [ ] Wrong pattern and correct fix both present (if adding an antipattern)
- [ ] Version numbers are pinned, not "latest"
```

---

## SKILL.md structure

Every `SKILL.md` must start with this frontmatter block:

```yaml
---
skill: <slug>
version: <semver>
applies_to: [kotlin, compose, android]  # adjust as needed
min_toolchain:
  kotlin: "2.1.x"
  agp: "9.x"
  compose_bom: "2026.x"
---
```

After frontmatter, the expected sections in order:

1. **Purpose** — one sentence on what the agent learns from this file.
2. **Toolchain** — pinned versions used throughout the skill.
3. **Rules** — the positive patterns the agent must follow.
4. **Banned antipatterns** — two-column table: ❌ wrong | ✅ correct.
5. **References** — links to official docs, KotlinConf talks, or benchmarks that back the rules.

---

## Reporting a broken rule

If an agent is following a rule in this kit and still producing bad output, open an issue using the **Broken Rule** template. Include:

- The rule text (copy-paste from the `SKILL.md`)
- The agent and model version
- The prompt you gave
- What the agent output
- What it should have output instead

---

## Scope

This repo covers **Kotlin + Jetpack Compose on Android**. Out of scope:

- Kotlin Multiplatform desktop or web targets (open a separate issue to discuss)
- Framework-specific rules for non-Google libraries unless they're in widespread use
- General software engineering advice not specific to Android/Compose

---

## License

By contributing you agree that your changes will be released under the [MIT License](./LICENSE) that covers this project.
