---
name: Feature / new guardrail
about: Propose a new sub-skill, reference, banned antipattern, decision matrix, or pattern.
title: "[feature] "
labels: enhancement
assignees: haidrrrry
---

## What gap does this fill

<!-- Which AI hallucination, toolchain shift, or production bug is this addressing? -->

## Proposed addition

- [ ] New sub-skill under `skills/<kebab-name>/`
- [ ] New reference under `references/`
- [ ] New banned antipattern in root `SKILL.md`
- [ ] New decision matrix / WRONG-RIGHT pair
- [ ] Other: <!-- describe -->

## Sketch

<!-- Rough outline of headings or code skeleton. -->

```kotlin
// pseudo / signature only is fine here
```

## Why now

<!-- Stable release that landed, new agent quirk observed, audit finding, etc. -->

## Acceptance criteria

- [ ] Compiling Kotlin/Gradle/YAML snippets only.
- [ ] Pinned versions.
- [ ] Registered in `AGENTS.md` (if new sub-skill).
- [ ] `CHANGELOG.md` entry queued under `[Unreleased]`.
- [ ] `api/skills.lock` updated (if new sub-skill).
