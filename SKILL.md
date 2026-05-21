---
name: compose-kotlin-agent-skills
description: >
  Enterprise Android/Kotlin skill for 2026 — Kotlin 2.x K2 compiler, AGP 9, Navigation 3,
  edge-to-edge Compose, strict MVI with atomic _state.update, banned AI antipatterns.
  Jetpack Compose, Hilt, Room, KMP, CameraX/ML Kit, performance, testing. Use when writing
  Kotlin for Android, building Compose UI, MVVM/MVI architecture, debugging recomposition,
  Room DAOs, Navigation 3, coroutines, or asking "structure Android app", "ViewModel UiState",
  "collectAsStateWithLifecycle", "edge to edge", "AGP 9", "K2 compiler", "Play Store release".
license: MIT
metadata:
  author: haidrrrry
  version: "2.0.0"
  standard: agentskills.io
  platforms:
    target: ["android", "kotlin-multiplatform", "compose-multiplatform"]
    host: ["macos", "linux", "windows"]
    agent_compatibility: 27
---

# Android & Kotlin — Enterprise Production Skill (2026)

Authoritative Android engineering kit. Real patterns from [AnimatedClockJetpacl](https://github.com/haidrrrry/AnimatedClockJetpacl), [Authenticator](https://github.com/haidrrrry/Authenticator), [RepLock](https://github.com/haidrrrry/RepLockPushupAppBlocker).

> **Not** an Android library, Alexa/Bixby skill, or on-device LLM SDK. **Not** a UI library like [Lumen](https://github.com/aldefy/Lumen).
> This is **markdown for coding AIs** — clone into `.cursor/skills/` or `.claude/skills/`. See README § "What this is NOT".

**Meta index:** [`AGENTS.md`](AGENTS.md) · **CI:** `python3 scripts/validate_skills.py`

## Sub-Skills (Modular)

| Skill | Path | Scope |
|-------|------|-------|
| Architecture | [`skills/android-kotlin-architecture/SKILL.md`](skills/android-kotlin-architecture/SKILL.md) | MVI/MVVM, modules, UseCases, UDF |
| Compose UI | [`skills/android-kotlin-compose/SKILL.md`](skills/android-kotlin-compose/SKILL.md) | UI, edge-to-edge, performance, motion |
| Testing | [`skills/android-kotlin-testing/SKILL.md`](skills/android-kotlin-testing/SKILL.md) | Turbine, Compose tests, Hilt fakes |

## 2026 Toolchain — Non-Negotiable

| Tool | Minimum | Notes |
|------|---------|-------|
| Kotlin | **2.0+** (2.1.x) | K2 compiler only — no K1 fallback |
| AGP | **9.0+** | Built-in Kotlin, new DSL defaults |
| Compose BOM | **2025.05+** | Material 3, strong skipping default |
| Navigation | **3.x** (`2.9+` artifact) | Type-safe `NavKey`, `@Serializable` routes |
| compileSdk / targetSdk | **35+** | Edge-to-edge mandatory |
| JDK | **17** | Required for AGP 9 |

```toml
[versions]
kotlin = "2.1.20"
agp = "9.0.0"
compose-bom = "2025.05.00"
navigation = "2.9.0"
room = "2.7.1"
hilt = "2.56.2"
lifecycle = "2.9.0"
coroutines = "1.10.2"
```

## Kotlin 2.x / K2 Compiler Constraints

1. **Enable K2** — `kotlin.compiler.execution.strategy` default; use `ksp` not `kapt` for Hilt/Room.
2. **Smart casts** — prefer `when (val x = state) { is Loaded -> ... }` over unsafe `!!`.
3. **Sealed hierarchy** — `sealed interface UiState` + `data object Loading : UiState` for exhaustive `when`.
4. **`@JvmInline value class`** for IDs (`@JvmInline value class UserId(val raw: String)`).
5. **`@Immutable` / `@Stable`** on UiState and UI models passed to Compose.
6. **Explicit API** optional for libraries — `kotlin { explicitApi() }` in published modules.
7. **No `!!`** except in tests with comment — use `requireNotNull` / early return.
8. **`data class` copy** for state — never mutate UiState fields in place.

```kotlin
sealed interface AccountsUiState {
    data object Loading : AccountsUiState
    data class Ready(
        val accounts: List<AccountUi>,
        val query: String = ""
    ) : AccountsUiState
    data class Error(@StringRes val messageRes: Int) : AccountsUiState
}
```

## MVI Guardrails — Atomic State Only

**Allowed mutation:** `_state.update { it.copy(...) }` or `_state.update { prev -> ... }`.

**Banned in ViewModel:**

```kotlin
// BANNED
_state.value = AccountsUiState(...)           // naked assign
_state.value.accounts.add(item)               // mutating list inside state
mutableStateOf / mutableStateListOf in VM      // Compose scope only
viewModelScope.launch { _state.value = ... }  // use update inside launch
```

**Required pattern:**

```kotlin
class AccountsViewModel @Inject constructor(
    private val repository: AccountsRepository
) : ViewModel() {

    private val _state = MutableStateFlow<AccountsUiState>(AccountsUiState.Loading)
    val state: StateFlow<AccountsUiState> = _state.asStateFlow()

    private val _effects = Channel<AccountsEffect>(Channel.BUFFERED)
    val effects: Flow<AccountsEffect> = _effects.receiveAsFlow()

    fun onEvent(event: AccountsEvent) {
        when (event) {
            AccountsEvent.Refresh -> refresh()
            is AccountsEvent.QueryChanged -> _state.update { current ->
                when (current) {
                    is AccountsUiState.Ready -> current.copy(query = event.query)
                    else -> current
                }
            }
        }
    }

    private fun refresh() {
        viewModelScope.launch {
            _state.update { AccountsUiState.Loading }
            repository.load()
                .onSuccess { list ->
                    _state.update { AccountsUiState.Ready(accounts = list.map { it.toUi() }) }
                }
                .onFailure {
                    _state.update { AccountsUiState.Error(R.string.error_load_failed) }
                }
        }
    }
}
```

**UI collects:**

```kotlin
@Composable
fun AccountsRoute(vm: AccountsViewModel = hiltViewModel()) {
    val state by vm.state.collectAsStateWithLifecycle()
    LaunchedEffect(Unit) {
        vm.effects.collect { effect -> /* one-shot: nav, snackbar */ }
    }
    AccountsScreen(state = state, onEvent = vm::onEvent)
}
```

## Navigation 3 + Edge-to-Edge

```kotlin
@Serializable data object Home
@Serializable data class Detail(val id: String)

@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController, startDestination = Home) {
        composable<Home> { HomeScreen(onOpen = { navController.navigate(Detail(it)) }) }
        composable<Detail> { entry ->
            val route = entry.toRoute<Detail>()
            DetailScreen(id = route.id)
        }
    }
}
```

- Routes = `@Serializable` types, not string paths
- Pass **IDs** in nav args — fetch models in destination ViewModel
- `enableEdgeToEdge()` in Activity — see compose sub-skill

Deep dive: [`references/07-navigation.md`](references/07-navigation.md)

## Banned Antipatterns — AI Hallucination Lookup

| # | Banned (WRONG) | Correct (RIGHT) | Why it breaks |
|---|----------------|-----------------|---------------|
| 1 | `GlobalScope.launch { }` | `viewModelScope.launch { }` | Leaks past lifecycle |
| 2 | `runBlocking { }` on main | `suspend` + proper scope | ANR |
| 3 | `Text("Hello")` in UI | `stringResource(R.string.hello)` | No localization |
| 4 | `collectAsState()` Android | `collectAsStateWithLifecycle()` | Background battery drain |
| 5 | `_state.value = x` | `_state.update { x }` | Race + non-atomic |
| 6 | `mutableStateListOf` in VM | `StateFlow<List<T>>` + immutable list | Not snapshot-safe |
| 7 | `items(list)` no key | `items(list, key = { it.id })` | Lost item state |
| 8 | Pass `ViewModel` to child | Pass lambdas / state | Broken previews + tight coupling |
| 9 | `remember { mutableStateOf }` for screen state | ViewModel `StateFlow` | Dies on rotation |
| 10 | `Dispatchers.IO` around Room | `viewModelScope.launch` only | Double dispatch |
| 11 | `@Provides` interface bind | `@Binds` interface | Extra allocation |
| 12 | Nav arg = whole object | Nav arg = `id: String` | Process death crash |
| 13 | `fallbackToDestructiveMigration()` prod | Explicit `Migration` | Data wipe |
| 14 | `Modifier.clickable` before `clip` wrong order | padding→clip→bg→clickable | Wrong hit target |
| 15 | Sort inside `LazyColumn` items | `remember` or VM sort | Recompose every frame |
| 16 | `derivedStateOf` without `remember` | `remember { derivedStateOf { } }` | Recreated each frame |
| 17 | Backwards write in `@Composable` | Write in event handlers only | Infinite recompose |
| 18 | `!!` on nullable state | Smart cast / `when` | NPE |
| 19 | Ktor `HttpClient()` no engine | `HttpClient(OkHttp)` / `Darwin` | Runtime crash |
| 20 | Hardcode `compileSdk 34` new app | `compileSdk 35` + edge-to-edge | Play policy |

## Reference Routing

| File | Topic |
|------|-------|
| `references/01-architecture.md` | Clean Arch, MVVM, modules |
| `references/02-compose-ui.md` | Composition, M3, theming |
| `references/03-animations.md` | Motion, Canvas |
| `references/04-coroutines-flow.md` | Flow, errors, cancellation |
| `references/05-hilt-di.md` | DI, scopes |
| `references/06-room-db.md` | Room, offline-first |
| `references/07-navigation.md` | Nav 3, deep links |
| `references/08-kmp-cmp.md` | KMP, expect/actual |
| `references/09-networking.md` | Ktor, JWT |
| `references/10-performance.md` | Recomposition, Coil, profiles |
| `references/11-testing.md` | Turbine, UI tests |
| `references/12-camera-mlkit.md` | CameraX, pose |
| `references/13-release-checklist.md` | R8, Play Store |

## Platforms

**Target (what the docs teach):** Android · Kotlin Multiplatform · Compose Multiplatform
**Host (where the docs are read):** macOS · Linux · Windows — anywhere your AI agent runs
**Agent compatibility:** 27 install guides → [`agents/README.md`](agents/README.md)

Repo: `https://github.com/haidrrrry/compose-kotlin-agent-skills`

## Mandatory Defaults (Summary)

- **Strings:** `stringResource` / `@StringRes` — zero hardcoded UI text
- **State:** ViewModel `StateFlow` + `_state.update { }`
- **UI:** Stateless composables, `modifier` first optional param
- **Lists:** `LazyColumn` + keys + `contentType`
- **DI:** `@HiltViewModel` + constructor inject
- **Tests:** Fakes + Turbine — see testing sub-skill

## Validation Before PR

```bash
python3 scripts/validate_skills.py --strict
```

## Anti-Rationalizations

| Excuse | Reality |
|--------|---------|
| "UiState overkill" | `data object Loading` costs one line |
| "Keys later" | Broken scroll/focus NOW |
| "Prototype skip repo" | Prototypes ship |
| "collectAsState fine" | Background collector drains battery |

## Examples

| Path | Patterns |
|------|----------|
| `examples/animated-clock/` | Canvas, `rotate()`, particles |
| `examples/authenticator/` | Room Flow, `combine`, CompositionLocal theme |
