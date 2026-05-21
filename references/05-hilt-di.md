# Hilt Dependency Injection — Patterns, Scopes, Testing

## Contents

- Core setup
- @HiltViewModel pattern
- @Binds vs @Provides
- Scopes — when to use which
- EntryPoint for non-Hilt classes
- Hilt vs Koin — detailed comparison
- Testing with Hilt
- Anti-patterns

## Core Setup

```kotlin
// Application class
@HiltAndroidApp
class MyApp : Application()

// Activity
@AndroidEntryPoint
class MainActivity : ComponentActivity()
```

```toml
# build.gradle.kts (app)
[plugins]
hilt = { id = "com.google.dagger.hilt.android", version = "2.56.2" }
ksp = { id = "com.google.devtools.ksp", version = "2.1.20-1.0.32" }

[dependencies]
hilt-android = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }
hilt-compiler = { module = "com.google.dagger:hilt-compiler", version.ref = "hilt" }
hilt-navigation-compose = { module = "androidx.hilt:hilt-navigation-compose", version = "1.2.0" }
```

**Use KSP, not kapt.** Kapt is deprecated and slower.

## @HiltViewModel Pattern

```kotlin
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val repository: AuthRepository,
    private val totpGenerator: TOTPGenerator,
    private val savedStateHandle: SavedStateHandle  // free from Hilt
) : ViewModel() {

    private val _state = MutableStateFlow(AccountsUiState())
    val state: StateFlow<AccountsUiState> = _state.asStateFlow()

    // Navigation arg from SavedStateHandle
    private val accountId: String? = savedStateHandle["accountId"]

    init {
        loadAccounts()
    }

    private fun loadAccounts() {
        viewModelScope.launch {
            repository.getAllAccounts()
                .collect { accounts ->
                    _state.update { it.copy(accounts = accounts) }
                }
        }
    }
}

// Composable usage
@Composable
fun AccountsScreen(
    viewModel: AuthViewModel = hiltViewModel()  // from hilt-navigation-compose
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    // ...
}
```

`hiltViewModel()` scopes the ViewModel to the navigation back stack entry. Each destination gets its own instance.

## @Binds vs @Provides

### @Binds — Interface to Implementation Mapping

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindAuthRepository(
        impl: AuthRepositoryImpl
    ): AuthRepository

    @Binds
    @Singleton
    abstract fun bindTotpGenerator(
        impl: HmacTotpGenerator
    ): TOTPGenerator
}
```

**Use when:** you have an interface + single implementation. Generates less code than `@Provides`.

### @Provides — Object Construction

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        )
            .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
            .build()
    }

    @Provides
    fun provideAuthAccountDao(database: AppDatabase): AuthAccountDao {
        return database.authAccountDao()
    }
}

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideHttpClient(): HttpClient {
        return HttpClient(OkHttp) {
            install(ContentNegotiation) { json() }
            install(Logging) { level = LogLevel.BODY }
            defaultRequest {
                url("https://api.example.com/")
                contentType(ContentType.Application.Json)
            }
        }
    }
}
```

**Use when:** constructing third-party objects you don't own, or complex construction logic.

### Decision Rule

| Scenario | Use |
|----------|-----|
| Interface → Implementation | `@Binds` |
| Third-party library object | `@Provides` |
| Complex construction with params | `@Provides` |
| Builder pattern (Room, Retrofit, Ktor) | `@Provides` |

## Scopes

| Scope | Lives as long as | Use for |
|-------|-----------------|---------|
| `@Singleton` | Application | Database, HttpClient, shared repos |
| `@ActivityScoped` | Activity | Rarely used in Compose-first apps |
| `@ViewModelScoped` | ViewModel | State shared between composables in one screen |
| `@ActivityRetainedScoped` | Survives config change | Shared between Activity-scoped and ViewModel-scoped |
| No scope (unscoped) | New instance every injection | Stateless helpers, mappers, UseCases |

```kotlin
// Singleton — one database for entire app
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(/*...*/): AppDatabase = /* ... */
}

// Unscoped — new UseCase per injection (lightweight, stateless)
class GenerateTotpCodeUseCase @Inject constructor(
    private val repo: AuthRepository
) {
    suspend operator fun invoke(accountId: String): String { /* ... */ }
}
```

**Rule:** scope as narrow as possible. `@Singleton` only for truly shared, expensive objects.

## EntryPoint — Non-Hilt Classes

For classes Hilt can't inject into (Services, Workers, ContentProviders):

```kotlin
// Define the entry point
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppBlockerServiceEntryPoint {
    fun appBlockerEngine(): AppBlockerEngine
    fun unlockSessionManager(): UnlockSessionManager
}

// Use in AccessibilityService (Hilt can't inject here)
class RepLockAccessibilityService : AccessibilityService() {

    private lateinit var engine: AppBlockerEngine

    override fun onServiceConnected() {
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            AppBlockerServiceEntryPoint::class.java
        )
        engine = entryPoint.appBlockerEngine()
    }
}
```

### WorkManager + Hilt

```kotlin
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val repository: AuthRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return repository.syncAccounts()
            .fold(
                onSuccess = { Result.success() },
                onFailure = { Result.retry() }
            )
    }
}
```

## Hilt vs Koin — Detailed Comparison

| Aspect | Hilt | Koin |
|--------|------|------|
| **Error detection** | Compile-time (KSP) | Runtime (crash on missing dependency) |
| **KMP support** | Android only | Full (commonMain) |
| **Setup cost** | Higher (annotations, modules) | Lower (DSL) |
| **Build time impact** | KSP adds ~10-20% | Zero (no code gen) |
| **Performance** | Zero runtime reflection | Reflection at startup (small) |
| **ViewModel injection** | `hiltViewModel()` | `koinViewModel()` |
| **Testing** | `TestInstallIn`, `@UninstallModules` | `loadKoinModules()` override |
| **Navigation scoping** | Automatic with `hiltViewModel()` | Manual with `koinNavViewModel()` |
| **Community** | Google-backed, massive | JetBrains-friendly, growing |

### Koin Setup (from Authenticator)

```kotlin
// commonMain — shared module
val sharedModule = module {
    single { AuthRepository(get()) }
    viewModel { AuthViewModel(get()) }
}

// androidMain — platform module
val androidModule = module {
    single<AuthAccountDao> {
        Room.databaseBuilder(get(), AppDatabase::class.java, "auth_db")
            .build()
            .authAccountDao()
    }
}

// Initialization
fun initKoin() {
    startKoin {
        modules(sharedModule, platformModule())
    }
}
```

**Choose Hilt when:** Android-only, want compile-time safety, team already knows Dagger.
**Choose Koin when:** KMP/CMP, want simpler setup, small-to-medium app, rapid prototyping.

## Testing with Hilt

### Replace Module in Tests

```kotlin
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
abstract class FakeRepositoryModule {
    @Binds
    @Singleton
    abstract fun bindAuthRepository(
        impl: FakeAuthRepository
    ): AuthRepository
}

class FakeAuthRepository : AuthRepository {
    private val accounts = MutableStateFlow<List<AuthAccount>>(emptyList())

    override fun getAllAccounts(): Flow<List<AuthAccount>> = accounts
    override suspend fun insertAccount(account: AuthAccount) {
        accounts.update { it + account }
    }
}
```

### ViewModel Unit Test (No Hilt Needed)

```kotlin
class AuthViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var fakeRepo: FakeAuthRepository
    private lateinit var viewModel: AuthViewModel

    @Before
    fun setup() {
        fakeRepo = FakeAuthRepository()
        viewModel = AuthViewModel(fakeRepo)
    }

    @Test
    fun `adding account updates state`() = runTest {
        val account = AuthAccount("1", "Google", "test@gmail.com", "secret")

        viewModel.onAddAccount(account)

        viewModel.uiState.test {  // Turbine
            val state = awaitItem()
            assertEquals(1, state.accounts.size)
            assertEquals("Google", state.accounts.first().serviceName)
        }
    }
}
```

Fakes over mocks. Mocks (Mockito/MockK) test interaction, not behavior. Fakes test the actual contract.

## Anti-Patterns

- **`@Singleton` on ViewModel** → wrong. Use `@HiltViewModel`. ViewModel lifecycle is managed by the framework
- **Injecting `Context` directly** → use `@ApplicationContext` or `@ActivityContext` qualifiers
- **Module per class** → one module per layer (DatabaseModule, NetworkModule, RepositoryModule). Don't create DataStoreModule + PreferencesModule + SettingsModule for 3 related bindings
- **`@Provides` when `@Binds` works** → `@Binds` generates less code. Use it for simple interface→impl mappings
- **Scoping everything as `@Singleton`** → most objects don't need to live for the app's entire lifetime. Unscoped is fine for stateless objects like mappers and UseCases
- **Injecting ViewModel into ViewModel** → never. If two ViewModels need shared state, extract to a shared `@Singleton` repository or manager
