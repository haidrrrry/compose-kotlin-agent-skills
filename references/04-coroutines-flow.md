# Coroutines & Flow — Dispatchers, StateFlow, Error Handling

## Contents

- viewModelScope vs lifecycleScope
- Dispatchers — IO vs Default vs Main
- StateFlow vs SharedFlow vs Channel
- collectAsStateWithLifecycle
- stateIn and shareIn
- Error handling — Result, sealed errors
- Structured concurrency and cancellation

## viewModelScope vs lifecycleScope

| Scope | Tied to | Survives config change | Use for |
|-------|---------|----------------------|---------|
| `viewModelScope` | ViewModel lifecycle | Yes | Data loading, state updates, business logic |
| `lifecycleScope` | Activity/Fragment | No | UI-bound work (permissions, navigation side effects) |
| `rememberCoroutineScope()` | Composable | No | One-shot composable actions (scroll, animation) |

```kotlin
// ViewModel — survives rotation
class AuthViewModel(private val repo: AuthRepository) : ViewModel() {
    init {
        viewModelScope.launch {
            repo.syncAccounts()  // survives config change
        }
    }
}

// Composable — one-shot scroll
@Composable
fun AccountsList(accounts: List<AuthAccount>) {
    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()

    LazyColumn(state = listState) { /* items */ }

    FloatingActionButton(onClick = {
        scope.launch {
            listState.animateScrollToItem(0)  // UI-only, doesn't need ViewModel
        }
    })
}
```

**Never use `GlobalScope`**. It ignores structured concurrency — coroutines leak.

## Dispatchers

| Dispatcher | Thread | Use for |
|-----------|--------|---------|
| `Dispatchers.Main` | Main/UI thread | UI updates, state emission, small logic |
| `Dispatchers.IO` | Shared IO pool (64+ threads) | Network calls, file I/O, DB (when not Room) |
| `Dispatchers.Default` | CPU cores pool | Heavy computation, JSON parsing, sorting large lists |
| `Dispatchers.Main.immediate` | Main, no re-dispatch | Already on Main, avoid queue hop |

### When NOT to Switch Dispatchers

```kotlin
// WRONG — Room already dispatches to background
viewModelScope.launch(Dispatchers.IO) {  // unnecessary thread hop
    val accounts = dao.getAllAccounts()
}

// RIGHT — Room handles threading internally
viewModelScope.launch {
    val accounts = dao.getAllAccounts()  // Room moves to IO internally
}
```

**Room, Retrofit (with suspend), and Ktor** handle dispatcher switching internally. Don't wrap them in `withContext(Dispatchers.IO)`.

### When TO Switch

```kotlin
// Heavy CPU work — parse 10k items
viewModelScope.launch {
    val parsed = withContext(Dispatchers.Default) {
        rawData.map { parseComplexItem(it) }  // CPU-bound
    }
    _state.update { it.copy(items = parsed) }
}

// File I/O not wrapped by a library
viewModelScope.launch {
    val content = withContext(Dispatchers.IO) {
        File("large.json").readText()
    }
}
```

## StateFlow vs SharedFlow vs Channel

### StateFlow — UI State

```kotlin
class AuthViewModel(private val repo: AuthRepository) : ViewModel() {
    private val _state = MutableStateFlow(AccountsUiState())
    val state: StateFlow<AccountsUiState> = _state.asStateFlow()

    // Derived state from Room
    val accounts: StateFlow<List<AuthAccount>> = repo.getAllAccounts()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = emptyList()
        )

    fun onSearchChanged(query: String) {
        _state.update { it.copy(searchQuery = query) }
    }
}
```

- Always has a value (`.value`)
- Conflates — if two rapid updates happen, collector only sees latest
- Replays latest value to new collectors
- Use for: any UI state

### SharedFlow — Events to Multiple Subscribers

```kotlin
class AnalyticsManager {
    private val _events = MutableSharedFlow<AnalyticsEvent>(
        replay = 0,          // no replay for new subscribers
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<AnalyticsEvent> = _events.asSharedFlow()

    suspend fun track(event: AnalyticsEvent) {
        _events.emit(event)
    }
}
```

- No current value
- Multiple subscribers each get the event
- Configurable replay and buffer
- Use for: analytics, logging, broadcast events

### Channel — One-Shot Commands

```kotlin
class WorkoutViewModel : ViewModel() {
    private val _effects = Channel<UiEffect>(Channel.BUFFERED)
    val effects: Flow<UiEffect> = _effects.receiveAsFlow()

    fun onWorkoutComplete() {
        viewModelScope.launch {
            _effects.send(UiEffect.NavigateToResults)
            _effects.send(UiEffect.PlayHaptic)
        }
    }
}

// Collect in composable
LaunchedEffect(Unit) {
    viewModel.effects.collect { effect ->
        when (effect) {
            UiEffect.NavigateToResults -> navController.navigate("results")
            UiEffect.PlayHaptic -> haptics.success()
        }
    }
}
```

- Delivered to exactly ONE collector
- Never dropped (unless channel is full with DROP strategy)
- Use for: navigation commands, snackbar, haptics — one-shot effects

## collectAsStateWithLifecycle

```kotlin
// WRONG — keeps collecting when app backgrounded
val state by viewModel.state.collectAsState()

// RIGHT — stops collecting in onStop, resumes in onStart
val state by viewModel.state.collectAsStateWithLifecycle()

// With custom lifecycle state
val state by viewModel.state.collectAsStateWithLifecycle(
    minActiveState = Lifecycle.State.RESUMED  // only collect when visible
)
```

**Why this matters:** `collectAsState` keeps the flow active when app is in background. If the flow is expensive (location, sensor data, network polling), it wastes battery and CPU for invisible UI.

**CMP exception:** in `commonMain`, `collectAsStateWithLifecycle` unavailable. Use `collectAsState` there. On Android targets, always use lifecycle-aware version.

Dependency:
```toml
androidx-lifecycle-runtime-compose = { module = "androidx.lifecycle:lifecycle-runtime-compose", version.ref = "lifecycle" }
```

## stateIn and shareIn

Convert cold Flow (Room query) to hot StateFlow for UI:

```kotlin
// WRONG — new flow on every collector, Room query runs N times
val accounts: Flow<List<AuthAccount>> = repo.getAllAccounts()

// RIGHT — shared, single Room query, all collectors share result
val accounts: StateFlow<List<AuthAccount>> = repo.getAllAccounts()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = emptyList()
    )
```

### SharingStarted Strategies

| Strategy | Behavior | Use when |
|----------|----------|----------|
| `WhileSubscribed(5_000)` | Active while subscribed + 5s buffer | Default for most UI flows |
| `Eagerly` | Active immediately, never stops | App-wide state (auth, theme) |
| `Lazily` | Active on first subscriber, never stops | Data that should load once |

**Why 5000ms?** Survives config change rotation (~2-3s) without restarting the upstream flow. Arbitrary but battle-tested.

## Error Handling

### Result + Sealed Domain Errors

```kotlin
// Domain errors — NOT exceptions
sealed interface DomainError {
    data class Network(val code: Int, val message: String) : DomainError
    data object Unauthorized : DomainError
    data object NotFound : DomainError
    data class Unknown(val cause: Throwable) : DomainError
}

// Repository returns Result
class AuthRepository(private val api: AuthApi, private val dao: AuthAccountDao) {
    suspend fun syncAccounts(): Result<List<AuthAccount>> {
        return try {
            val remote = api.getAccounts()
            val domain = remote.map { it.toDomain() }
            dao.insertAccounts(domain.map { it.toEntity() })
            Result.success(domain)
        } catch (e: HttpException) {
            when (e.code()) {
                401 -> Result.failure(DomainError.Unauthorized)
                404 -> Result.failure(DomainError.NotFound)
                else -> Result.failure(DomainError.Network(e.code(), e.message()))
            }
        } catch (e: IOException) {
            Result.failure(DomainError.Network(-1, "No connection"))
        }
    }
}

// ViewModel handles Result
viewModelScope.launch {
    _state.update { it.copy(isLoading = true) }
    repo.syncAccounts()
        .onSuccess { accounts ->
            _state.update { it.copy(accounts = accounts, isLoading = false) }
        }
        .onFailure { error ->
            _state.update { it.copy(error = error, isLoading = false) }
        }
}
```

### runCatching — Use with Caution

```kotlin
// DANGEROUS — catches CancellationException, breaks structured concurrency
val result = runCatching { repo.fetchData() }

// SAFE — rethrow CancellationException
suspend fun <T> safeRunCatching(block: suspend () -> T): Result<T> {
    return try {
        Result.success(block())
    } catch (e: CancellationException) {
        throw e  // never swallow this
    } catch (e: Throwable) {
        Result.failure(e)
    }
}
```

**Critical:** `runCatching` and `try/catch(Throwable)` catch `CancellationException`. This silently breaks coroutine cancellation. Always rethrow `CancellationException`.

## Structured Concurrency

### Parallel Execution

```kotlin
viewModelScope.launch {
    // WRONG — sequential, slow
    val accounts = repo.getAccounts()
    val settings = repo.getSettings()

    // RIGHT — parallel
    val accountsDeferred = async { repo.getAccounts() }
    val settingsDeferred = async { repo.getSettings() }
    val accounts = accountsDeferred.await()
    val settings = settingsDeferred.await()

    _state.update { it.copy(accounts = accounts, settings = settings) }
}
```

### Cancellation

```kotlin
class AuthViewModel : ViewModel() {
    private var searchJob: Job? = null

    fun onSearchChanged(query: String) {
        searchJob?.cancel()  // cancel previous search
        searchJob = viewModelScope.launch {
            delay(300)  // debounce
            val results = repo.search(query)
            _state.update { it.copy(searchResults = results) }
        }
    }
}
```

### SupervisorJob — Isolate Failures

```kotlin
// WRONG — one child failure cancels sibling
viewModelScope.launch {
    launch { syncAccounts() }   // if this fails...
    launch { syncSettings() }   // ...this gets cancelled too
}

// RIGHT — supervisor scope isolates failures
viewModelScope.launch {
    supervisorScope {
        launch { syncAccounts() }   // failure here...
        launch { syncSettings() }   // ...doesn't affect this
    }
}
```

## Anti-Patterns

- **Collecting Flow in `init {}` with manual launch** → use `stateIn` to convert to StateFlow
- **`delay()` for debouncing in ViewModel** → works but cancel/relaunch is manual. Consider `Flow.debounce()` or `Flow.distinctUntilChanged()`
- **`flowOn(Dispatchers.IO)` on Room Flow** → Room already dispatches. Double-hop
- **SharedFlow with `replay = 1` for UI state** → just use StateFlow. That's what it is
- **`collect {}` without lifecycle awareness** → use `collectAsStateWithLifecycle` or `repeatOnLifecycle`
