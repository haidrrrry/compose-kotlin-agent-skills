# Architecture — Clean Architecture + MVVM + MVI

## Contents

- Clean Architecture layers
- MVVM vs MVI — when to use which
- UiState sealed classes
- ViewModel + StateFlow + UiEvent + UiEffect
- UseCases — when to use, when NOT to use
- Module structure for large apps
- Anti-patterns

## Clean Architecture Layers

```
┌─────────────────────────────────────────────┐
│  presentation/   (UI + ViewModel)           │
│  ├── Composables render state               │
│  ├── ViewModel transforms domain → UiState  │
│  └── Depends on: domain                     │
├─────────────────────────────────────────────┤
│  domain/         (Pure Kotlin — no Android) │
│  ├── Models (data classes)                  │
│  ├── Repository interfaces                  │
│  ├── UseCases (optional)                    │
│  └── Depends on: nothing                    │
├─────────────────────────────────────────────┤
│  data/           (Implementation)           │
│  ├── Repository implementations             │
│  ├── Room entities + DAOs                   │
│  ├── Network DTOs + API services            │
│  ├── Mappers (DTO ↔ domain, Entity ↔ domain)│
│  └── Depends on: domain                     │
└─────────────────────────────────────────────┘
```

**The dependency rule:** outer layers depend on inner layers. Domain knows nothing about Room, Retrofit, or Compose. Data implements domain interfaces. Presentation consumes domain models.

## MVVM vs MVI — Decision Guide

| Aspect | MVVM | MVI |
|--------|------|-----|
| **State** | Multiple StateFlows | Single UiState sealed class |
| **Events** | Direct function calls | Sealed UiEvent dispatched |
| **Complexity** | Lower for simple screens | Higher, but predictable |
| **Debugging** | Harder — multiple state sources | Easier — single state timeline |
| **Use when** | Settings, forms, simple CRUD | Complex screens, multi-step flows |
| **Real example** | Authenticator's `AuthViewModel` | Workout flow with setup → camera → result |

**Rule of thumb:** start MVVM. Switch to MVI when you have 3+ interdependent state fields or multi-step flows.

## MVVM — Production Pattern

From Authenticator app — real ViewModel with search + CRUD:

```kotlin
data class AccountsUiState(
    val accounts: List<AuthAccount> = emptyList(),
    val searchQuery: String = "",
    val isLoading: Boolean = false,
    val error: String? = null
)

class AuthViewModel(private val repository: AuthRepository) : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val uiState: StateFlow<AccountsUiState> = combine(
        repository.getAllAccounts(),
        _searchQuery
    ) { accounts, query ->
        val filtered = if (query.isBlank()) accounts
            else accounts.filter {
                it.serviceName.contains(query, ignoreCase = true) ||
                it.accountName.contains(query, ignoreCase = true)
            }
        AccountsUiState(accounts = filtered, searchQuery = query)
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = AccountsUiState(isLoading = true)
    )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }

    fun onAddAccount(account: AuthAccount) {
        viewModelScope.launch {
            repository.insertAccount(account)
        }
    }

    fun onDeleteAccount(id: String) {
        viewModelScope.launch {
            repository.deleteAccountById(id)
        }
    }
}
```

**Key decisions:**
- `combine` merges two flows into single UiState — Room auto-emits on DB change
- `SharingStarted.WhileSubscribed(5_000)` — keeps flow active 5s after last subscriber (survives config change)
- No `Dispatchers.IO` — Room already switches threads internally
- Search is reactive — no manual "refresh" needed

### Screen Consumption

```kotlin
@Composable
fun AccountsScreen(viewModel: AuthViewModel = koinViewModel()) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    AccountsContent(
        accounts = state.accounts,
        searchQuery = state.searchQuery,
        onSearchChanged = viewModel::onSearchQueryChanged,
        onDelete = viewModel::onDeleteAccount,
        onAdd = viewModel::onAddAccount
    )
}

@Composable
private fun AccountsContent(
    accounts: List<AuthAccount>,
    searchQuery: String,
    onSearchChanged: (String) -> Unit,
    onDelete: (String) -> Unit,
    onAdd: (AuthAccount) -> Unit
) {
    // Pure UI — no ViewModel reference, fully previewable
    Column {
        SearchBar(query = searchQuery, onQueryChange = onSearchChanged)
        LazyColumn {
            items(accounts, key = { it.id }) { account ->
                AccountCard(account = account, onDelete = { onDelete(account.id) })
            }
        }
    }
}
```

**Pattern:** Container composable (has ViewModel) → Content composable (stateless, previewable). Content never touches ViewModel directly.

## MVI — Full Pattern

For complex screens with multi-step flows:

```kotlin
// State
data class WorkoutUiState(
    val phase: WorkoutPhase = WorkoutPhase.Setup,
    val workoutType: WorkoutType = WorkoutType.Pushups,
    val repCount: Int = 0,
    val targetReps: Int = 15,
    val timeRemaining: Duration = 3.minutes,
    val isLoading: Boolean = false,
    val error: WorkoutError? = null
)

enum class WorkoutPhase { Setup, Active, Completed, Failed }

// Events — user actions
sealed interface WorkoutEvent {
    data class SelectType(val type: WorkoutType) : WorkoutEvent
    data object StartWorkout : WorkoutEvent
    data object PauseWorkout : WorkoutEvent
    data class RepDetected(val count: Int) : WorkoutEvent
    data object Retry : WorkoutEvent
}

// Effects — one-shot side effects (navigation, snackbar, haptic)
sealed interface WorkoutEffect {
    data object NavigateToResults : WorkoutEffect
    data class ShowError(val message: String) : WorkoutEffect
    data object PlaySuccessHaptic : WorkoutEffect
}

class WorkoutViewModel(
    private val workoutManager: WorkoutSessionManager,
    private val historyRepo: WorkoutHistoryRepository
) : ViewModel() {

    private val _state = MutableStateFlow(WorkoutUiState())
    val state: StateFlow<WorkoutUiState> = _state.asStateFlow()

    private val _effects = Channel<WorkoutEffect>(Channel.BUFFERED)
    val effects: Flow<WorkoutEffect> = _effects.receiveAsFlow()

    fun onEvent(event: WorkoutEvent) {
        when (event) {
            is WorkoutEvent.SelectType -> {
                _state.update { it.copy(workoutType = event.type) }
            }
            is WorkoutEvent.StartWorkout -> startWorkout()
            is WorkoutEvent.PauseWorkout -> pauseWorkout()
            is WorkoutEvent.RepDetected -> onRepDetected(event.count)
            is WorkoutEvent.Retry -> retry()
        }
    }

    private fun onRepDetected(count: Int) {
        _state.update { it.copy(repCount = count) }
        if (count >= _state.value.targetReps) {
            _state.update { it.copy(phase = WorkoutPhase.Completed) }
            viewModelScope.launch {
                historyRepo.saveWorkout(/* ... */)
                _effects.send(WorkoutEffect.PlaySuccessHaptic)
                _effects.send(WorkoutEffect.NavigateToResults)
            }
        }
    }

    // ...
}
```

### Collecting Effects in Composable

```kotlin
@Composable
fun WorkoutScreen(viewModel: WorkoutViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    // Effects — one-shot, not state
    LaunchedEffect(Unit) {
        viewModel.effects.collect { effect ->
            when (effect) {
                is WorkoutEffect.NavigateToResults -> navController.navigate("results")
                is WorkoutEffect.ShowError -> snackbarHostState.showSnackbar(effect.message)
                is WorkoutEffect.PlaySuccessHaptic -> Haptics.success(context)
            }
        }
    }

    WorkoutContent(
        state = state,
        onEvent = viewModel::onEvent
    )
}
```

**Why Channel for effects, not SharedFlow?** Channel guarantees delivery exactly once. SharedFlow with `replay = 0` drops events if no collector is active (e.g., during config change).

## UseCases — When to Use, When NOT to Use

### Use When:
- Business logic shared by 2+ ViewModels
- Complex orchestration (multiple repos, validation, transformation)
- Logic needs unit testing independent of ViewModel

```kotlin
class GenerateTotpCodeUseCase(
    private val accountRepo: AuthRepository,
    private val totpGenerator: TOTPGenerator
) {
    suspend operator fun invoke(accountId: String): Result<String> {
        val account = accountRepo.getAccountById(accountId)
            ?: return Result.failure(AccountNotFound(accountId))
        return Result.success(totpGenerator.generate(account.secretKey))
    }
}
```

### Skip When:
- Simple pass-through to repository (ViewModel can call repo directly)
- Logic used by only one ViewModel
- Adds indirection without adding value

```kotlin
// BAD — UseCase that's just a proxy
class GetAllAccountsUseCase(private val repo: AuthRepository) {
    operator fun invoke(): Flow<List<AuthAccount>> = repo.getAllAccounts()
}

// Just call the repo directly in ViewModel
class AuthViewModel(private val repo: AuthRepository) : ViewModel() {
    val accounts = repo.getAllAccounts()
}
```

**Rule:** if UseCase body is a single line delegating to one repo, delete it.

## Module Structure for Large Apps

```
app/                          # Application module — wires everything
├── build.gradle.kts
├── src/main/
│   ├── AndroidManifest.xml
│   └── kotlin/.../
│       ├── App.kt            # @HiltAndroidApp or manual DI
│       └── MainActivity.kt

core/
├── core-ui/                  # Design system, shared composables, theme
│   └── DesignSystem.kt, AppColors.kt, Spacing.kt
├── core-domain/              # Shared domain models, base UseCase
│   └── DomainError.kt, BaseUseCase.kt
├── core-data/                # Shared data utilities, network client
│   └── NetworkClient.kt, BaseRepository.kt
└── core-testing/             # Test utilities, fakes, rules
    └── TestDispatcherRule.kt, FakeRepository.kt

feature/
├── feature-auth/
│   ├── data/                 # AuthRepository impl, DTO mappers
│   ├── domain/               # AuthAccount model, AuthRepository interface
│   └── presentation/         # AuthViewModel, AuthScreen
├── feature-workout/
│   ├── data/
│   ├── domain/
│   └── presentation/
└── feature-settings/
    ├── data/
    ├── domain/
    └── presentation/
```

**Module dependency rules:**
- `feature-*` depends on `core-*` only — never on other features
- `core-domain` depends on nothing (pure Kotlin)
- `core-data` depends on `core-domain`
- `app` depends on all features (wiring only)
- Feature-to-feature communication via shared `core-domain` interfaces or Navigation args

## Anti-Patterns

### God ViewModel
```kotlin
// BAD — 800-line ViewModel handling everything
class MainViewModel : ViewModel() {
    val accounts = ...
    val settings = ...
    val workoutState = ...
    val notifications = ...
    fun onLogin() { }
    fun onStartWorkout() { }
    fun onUpdateSettings() { }
}
```

One ViewModel per screen/feature. If ViewModel exceeds ~200 lines, extract UseCases or split screen.

### Domain Model = Entity = DTO
```kotlin
// BAD — Room annotations leak into domain
@Entity(tableName = "accounts")
data class AuthAccount(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "service_name") val serviceName: String,
    val secretKey: String  // domain shouldn't know about DB columns
)
```

```kotlin
// RIGHT — separate models with mappers
// domain/
data class AuthAccount(val id: String, val serviceName: String, val secretKey: String)

// data/
@Entity(tableName = "accounts")
data class AuthAccountEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "service_name") val serviceName: String,
    @ColumnInfo(name = "secret_key") val secretKey: String
)

fun AuthAccountEntity.toDomain() = AuthAccount(id, serviceName, secretKey)
fun AuthAccount.toEntity() = AuthAccountEntity(id, serviceName, secretKey)
```

Trade-off: for small apps with no network layer, single model is acceptable. Split when you have DTO + Entity + Domain or when Room annotations would leak into shared KMP modules.

### Exposing MutableStateFlow

```kotlin
// BAD — UI can mutate state directly
class AuthViewModel : ViewModel() {
    val state = MutableStateFlow(AccountsUiState())
}

// RIGHT — private mutable, public read-only
class AuthViewModel : ViewModel() {
    private val _state = MutableStateFlow(AccountsUiState())
    val state: StateFlow<AccountsUiState> = _state.asStateFlow()
}
```

Always expose `StateFlow`, never `MutableStateFlow`. State changes happen through ViewModel functions only.
