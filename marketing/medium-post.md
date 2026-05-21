# Medium Article Draft

Long-form, SEO-friendly, 8-minute read. Copy-paste into Medium editor.
Add the logo (`assets/logo.png`) as the cover image. Tag with: **Android, Kotlin, Jetpack Compose, AI, Cursor, Claude.**

---

# I Stopped Letting AI Agents Write Broken Kotlin — Here's the Skill Kit That Fixed It

**Strict MVI, banned antipatterns, and 27 agent install guides — all in one markdown kit you clone into `.cursor/skills/` or `.claude/skills/`.**

---

## The problem nobody talks about

Cursor, Claude Code, Codex, Gemini, Copilot — they all write Kotlin/Compose code that **compiles** but ships bugs you only catch in production.

Here is the list I kept reverting on every PR:

- `_state.value = newState` — race condition, lost updates under concurrency.
- `collectAsState()` on a screen — keeps the Flow collector alive in the background and drains battery.
- Hardcoded `"Login"` literals — breaks localisation the moment QA opens a non-English build.
- `LazyColumn(items)` without `key { it.id }` — broken scroll position, recomposition storms, focus loss.
- `GlobalScope.launch { }` inside a ViewModel — leaks the coroutine past the screen lifecycle.
- `mutableStateListOf` as ViewModel state — survives config changes incorrectly.
- String-based `NavHost(route = "home/{id}")` — deprecated by Navigation 3.

Every Android engineer reading this is nodding. AI agents have read the same shallow blog posts you and I read in 2021, and they regurgitate the same broken patterns five years later.

I shipped three Android apps in the last year — [AnimatedClockJetpacl](https://github.com/haidrrrry/AnimatedClockJetpacl), [Authenticator](https://github.com/haidrrrry/Authenticator), and [RepLock](https://github.com/haidrrrry/RepLockPushupAppBlocker) — and I spent more time fixing my agent's Kotlin than writing my own.

So I built a fix.

---

## Introducing `compose-kotlin-agent-skills`

A markdown-only skill kit your AI coding agent reads **before** writing a single line of Kotlin.

**Repo:** https://github.com/haidrrrry/compose-kotlin-agent-skills
**License:** MIT
**Install:** one `git clone` into your agent's skills folder.

It teaches your agent:

1. **The 2026 Android toolchain** — Kotlin 2.x K2 compiler, AGP 9, Compose BOM 2026, Navigation 3, edge-to-edge by default.
2. **Strict MVI** — atomic `_state.update { it.copy(...) }`, `UiState` + `UiEvent` + `UiEffect`. Naked state assignment is explicitly banned.
3. **A banned-antipatterns table** — every wrong pattern paired with the correct fix in a side-by-side block.
4. **Decision matrices** — `StateFlow` vs `SharedFlow` vs `Channel`, Hilt vs Koin, Room vs DataStore, Compose Navigation vs Nav 3.
5. **Production gotchas** — bugs that only appear after Play Store rollout (R8 reflection, baseline profile drift, recomposition storms).

---

## How it works

Three layers, loaded on demand:

```
SKILL.md (routing hub + guardrails)
   |
   v
sub-skills/
   ├── architecture (Clean Arch, MVI, modules)
   ├── compose (UI, recomposition, M3, edge-to-edge)
   └── testing (Turbine, Hilt fakes, Compose UI tests)
   |
   v
references/ (13 deep dives)
   ├── 01-architecture.md
   ├── 02-compose-ui.md
   ├── 03-animations.md
   ├── 04-coroutines-flow.md
   ├── 05-hilt-di.md
   ├── 06-room-db.md
   ├── 07-navigation.md
   ├── 08-kmp-cmp.md
   ├── 09-networking.md
   ├── 10-performance.md
   ├── 11-testing.md
   ├── 12-camera-mlkit.md
   └── 13-release-checklist.md
```

When you ask Cursor or Claude Code _"how should I structure this ViewModel?"_, the agent reads `SKILL.md`, follows the routing rules, loads the architecture sub-skill, and pulls `references/01-architecture.md` for the deep dive.

It then writes Kotlin that looks like this:

```kotlin
@Immutable
data class FeatureUiState(
    val items: List<ItemUi> = emptyList(),
    val isLoading: Boolean = false,
    val error: UiError? = null
)

sealed interface FeatureUiEvent {
    data object Refresh : FeatureUiEvent
    data class SearchChanged(val query: String) : FeatureUiEvent
}

@HiltViewModel
class FeatureViewModel @Inject constructor(
    private val repository: FeatureRepository
) : ViewModel() {
    private val _state = MutableStateFlow(FeatureUiState())
    val state: StateFlow<FeatureUiState> = _state.asStateFlow()

    fun onEvent(event: FeatureUiEvent) {
        when (event) {
            FeatureUiEvent.Refresh -> refresh()
            is FeatureUiEvent.SearchChanged -> _state.update {
                it.copy(query = event.query)
            }
        }
    }

    private fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            runCatching { repository.fetch() }
                .onSuccess { items -> _state.update { it.copy(items = items, isLoading = false) } }
                .onFailure { e -> _state.update { it.copy(error = UiError.from(e), isLoading = false) } }
        }
    }
}
```

Not `_state.value = …`. Not `GlobalScope`. Not `collectAsState()` on the Composable. Every piece follows the guardrails.

---

## What changes when you install it

| Area | Without the kit | With the kit |
|---|---|---|
| ViewModel state | `_state.value = ...` | Atomic `_state.update { it.copy(...) }` |
| Flow collection | `collectAsState()` | `collectAsStateWithLifecycle()` |
| UI text | Hardcoded `"Login"` | `stringResource(R.string.login)` |
| Lists | `LazyColumn` no key | Stable `key` + `contentType` per item |
| Architecture | Mixed MVVM, state in Composable | Strict MVI — `UiState` / `UiEvent` / `UiEffect` |
| DI | `companion object Singleton` | `@HiltViewModel` + constructor injection |
| Navigation | String routes | Navigation 3 `NavKey` types |
| Coroutines | `GlobalScope.launch { }` | `viewModelScope` + structured concurrency |
| Edge-to-edge | Status bar overlap | `enableEdgeToEdge()` + correct insets |

---

## Install in 30 seconds

### Cursor

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git \
  .cursor/skills/compose-kotlin-agent-skills
```

Cursor auto-discovers `.cursor/skills/*/SKILL.md`.

### Claude Code

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git \
  ~/.claude/skills/compose-kotlin-agent-skills
```

Then add a five-line block to your `CLAUDE.md` — example in `agents/claude.md`.

### Codex CLI / Gemini CLI / Copilot / Windsurf / Kimi / DeepSeek / 21 more

Every agent gets a dedicated install guide in [`agents/`](https://github.com/haidrrrry/compose-kotlin-agent-skills/tree/main/agents). 27 total at time of writing.

---

## CI-validated, so the rules stay honest

A markdown skill kit that lies to your agent is worse than no skill kit. So the repo ships:

- `scripts/validate_skills.py` — frontmatter linter + internal link checker + md5 registry.
- `api/skills.lock` — every `SKILL.md` registered with its hash. CI fails on undocumented add / remove / edit.
- `.github/workflows/skill-lint.yml` — runs on every push and pull request, uploads JUnit XML, prints fix hints on failure.

Editing any `SKILL.md` is one helper script:

```bash
./scripts/update_lock.sh
```

Commit the lock file with your change. CI stays green.

---

## What this is NOT

I get DMs asking "is this a Compose UI library?" — no.

| Wrong guess | Reality |
|---|---|
| Android library you `implementation(...)` in Gradle | No. Nothing to import. Pure markdown. |
| Alexa / Bixby "skill" | No. The word "skill" follows the [agentskills.io](https://agentskills.io) format, not voice assistants. |
| On-device LLM SDK | No. Zero model inference, zero agent framework code. |
| Compose UI library (coachmarks, theming, charts) | No. We do not ship Composables. We teach how to write them. |

**TL;DR:** clone the repo into your agent's skills folder. The agent reads it before writing Kotlin. That is the entire product.

---

## What's next

Q3 2026 plans:

- Split `references/08-kmp-cmp.md` into its own sub-skill with a Ktor + SQLDelight matrix.
- Pull `references/12-camera-mlkit.md` into a dedicated CameraX/ML Kit sub-skill.
- Auto-extract every code block in `references/` into a Gradle project that compiles in CI.
- A "self-test" prompt suite — golden agent transcripts replayed against a frozen model.

Full roadmap → [`ROADMAP.md`](https://github.com/haidrrrry/compose-kotlin-agent-skills/blob/main/ROADMAP.md)

---

## Contributing

PRs welcome — especially new banned antipatterns you have caught your agent doing.

Every new sub-skill must:

1. Live under `skills/<kebab-name>/SKILL.md` with valid frontmatter.
2. Pass `python3 scripts/validate_skills.py --strict`.
3. Be registered in `AGENTS.md`.
4. Bump `api/skills.lock` via `./scripts/update_lock.sh`.

PR template enforces all four.

---

## Closing

Your AI agent is going to keep shipping `GlobalScope.launch { }` until you give it a playbook that says no. This is mine. Clone it, fork it, ship better Kotlin.

⭐ **Star on GitHub:** https://github.com/haidrrrry/compose-kotlin-agent-skills

If your agent has invented a new way to break MVI that I have not banned yet, open an issue. Genuinely curious.

— [Haider Ali Khan](https://github.com/haidrrrry)

---

**Tags (paste these on Medium):** Android, Kotlin, Jetpack Compose, Cursor, Claude AI, AI Coding, Software Engineering, Mobile Development

---

## Distribution checklist

- [ ] Cover image set to `assets/logo.png`
- [ ] Subtitle filled in (Medium prompts for one)
- [ ] Tags: Android, Kotlin, Jetpack Compose, Cursor, Claude
- [ ] Publish to a Medium publication if you have one (Better Programming, Android Bits, Proandroiddev) — 10x reach vs personal blog
- [ ] After publishing, tweet the URL with the cover image
- [ ] Cross-post the same draft on dev.to with `#android #kotlin #jetpackcompose #ai`
- [ ] Submit to https://androidweekly.net/issues — free curated newsletter, 90k+ Android devs
- [ ] Submit to https://kotlinweekly.net/ — 30k+ Kotlin devs
