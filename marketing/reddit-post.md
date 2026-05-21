# Reddit Post Drafts

Three subreddit-tuned versions. Pick one per sub. Post to **r/androiddev first** (highest signal), wait 24h before others to avoid spam flags.

---

## Version A — r/androiddev

**Title:**
> I got tired of Cursor and Claude writing broken Compose code, so I built a skill kit that forces them to follow real MVI rules

**Body:**

Every AI coding agent ships the same broken Kotlin patterns:

- `_state.value = …` instead of `_state.update { }`
- `collectAsState()` instead of `collectAsStateWithLifecycle()`
- Hardcoded UI strings — no `stringResource`
- `LazyColumn` with no `key` or `contentType`
- `GlobalScope.launch { }` inside ViewModels
- String-based Navigation routes (deprecated)

I shipped a few Android apps and watched my agents undo my MVI patterns every other PR. So I wrote a skill kit that ships as markdown, drops into `.cursor/skills/` or `.claude/skills/`, and gets read **before** the agent writes any Kotlin.

It enforces:

- Kotlin 2.x K2, AGP 9, Compose BOM 2026, Navigation 3
- Strict MVI — atomic `_state.update`, `UiState` / `UiEvent` / `UiEffect`
- A banned-antipatterns table with the correct fix next to every wrong pattern
- Edge-to-edge by default, `collectAsStateWithLifecycle`, `LazyColumn` keys

13 reference modules (architecture, Compose UI, animations, coroutines, Hilt, Room, Navigation 3, KMP, Ktor, performance, testing, CameraX/ML Kit, release checklist), 3 modular sub-skills, install guides for 27 agents (Cursor, Claude Code, Codex, Gemini, Copilot, Windsurf, Kimi, DeepSeek, Cline, Aider, Continue, Zed, JetBrains AI, etc.).

CI-validated — every `SKILL.md` is frontmatter-linted and md5-locked on every push.

**Repo:** https://github.com/haidrrrry/compose-kotlin-agent-skills

**Install (Cursor):**
```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .cursor/skills/compose-kotlin-agent-skills
```

**Install (Claude Code):**
```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git ~/.claude/skills/compose-kotlin-agent-skills
```

MIT. PRs welcome — especially new banned antipatterns you have caught your agent doing.

What patterns has your agent broken in your codebase? Curious to add them to the banned list.

---

## Version B — r/Kotlin

**Title:**
> Kotlin/Compose agent skill kit — forces Cursor, Claude Code, Codex to write production code, not docs copy-paste

**Body:**

Open-sourced a markdown-only skill kit your AI coding agent loads from `.cursor/skills/` or `.claude/skills/`. Teaches strict MVI, Kotlin 2.x K2 idioms, atomic `StateFlow` updates, and a banned-antipatterns table covering the usual hallucinations (`GlobalScope`, naked `_state.value =`, `collectAsState()`, hardcoded UI strings, no `LazyColumn` keys).

Coverage:

- Clean Architecture + MVI (`UiState` / `UiEvent` / `UiEffect`)
- Jetpack Compose UI, recomposition, stability annotations, Modifier ordering
- Coroutines + Flow decision matrix (`StateFlow` vs `SharedFlow` vs `Channel`)
- Hilt DI with scopes + `TestInstallIn` fakes
- Room — migrations, offline-first, Flow DAOs
- Navigation 3 type-safe routes
- Kotlin Multiplatform / Compose Multiplatform (`expect` / `actual`, shared ViewModel, Ktor)
- Performance, baseline profiles, Play Store checklist

27 per-agent install guides. CI-validated on every push.

Repo: https://github.com/haidrrrry/compose-kotlin-agent-skills

MIT licensed. Looking for feedback on patterns I might have missed.

---

## Version C — r/cursor

**Title:**
> [Skill] Production Android & Kotlin rules for Cursor — strict MVI, banned antipatterns, 13 reference modules

**Body:**

Built a Cursor skill pack for Android/Kotlin/Jetpack Compose development. Stops Cursor hallucinating `GlobalScope`, `collectAsState()`, naked `_state.value =`, hardcoded strings, etc.

**Install:**
```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .cursor/skills/compose-kotlin-agent-skills
```

Cursor auto-discovers `.cursor/skills/*/SKILL.md`. Or wire it as a rule — see `agents/cursor.md`.

**What it ships:**

- 1 root `SKILL.md` with routing + MVI guardrails + banned antipatterns
- 3 sub-skills: architecture, Compose UI, testing
- 13 reference modules
- Pinned 2026 dependency versions
- Verification prompt to confirm the skill loaded

**Verification:**

> "How should I structure a ViewModel with UiState for Jetpack Compose?"

Should mention `MutableStateFlow`, `data class XxxUiState`, `collectAsStateWithLifecycle`, `_state.update`.

Repo: https://github.com/haidrrrry/compose-kotlin-agent-skills

PRs welcome. MIT.

---

## Posting tips

- Post Tue/Wed morning US time for r/androiddev (highest traffic).
- Don't cross-post within 24h — Reddit shadowbans.
- Answer every comment in the first hour — drives sort-by-new.
- Don't drop the repo URL in your first comment, put it in the post body once.
- Have a screenshot ready of the README hero — Reddit auto-previews images.
