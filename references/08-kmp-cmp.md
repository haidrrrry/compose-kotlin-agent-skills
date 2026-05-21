# KMP / CMP — Kotlin Multiplatform & Compose Multiplatform

## Contents

- Shared module structure
- expect/actual pattern
- Shared ViewModel with KMP
- Shared domain layer
- Platform-specific UI vs shared Compose UI
- Ktor for networking
- Room vs SQLDelight for KMP persistence
- Real patterns from Authenticator app

## Shared Module Structure

From Authenticator — real CMP project:

```
composeApp/
├── src/
│   ├── commonMain/          # Shared code — runs everywhere
│   │   └── kotlin/
│   │       ├── App.kt
│   │       ├── classes/     # Domain models
│   │       ├── dao/         # Room DAO (interface)
│   │       ├── di/          # Koin shared modules
│   │       ├── repository/  # Repository + ViewModel
│   │       ├── screens/     # Shared Compose UI
│   │       └── utils/       # AppColors, ThemeManager, TOTP
│   ├── androidMain/         # Android-specific
│   │   └── kotlin/
│   │       ├── MainActivity.kt
│   │       ├── dao/         # DatabaseFactory.android.kt
│   │       ├── di/          # Koin Android modules
│   │       └── utils/       # TOTP Android impl
│   ├── iosMain/             # iOS-specific
│   │   └── kotlin/
│   │       ├── MainViewController.kt
│   │       ├── dao/         # DatabaseFactory.ios.kt
│   │       ├── di/          # Koin iOS modules
│   │       └── utils/       # TOTP iOS impl
│   └── desktopMain/         # Desktop-specific
│       └── kotlin/
│           ├── main.kt
│           ├── dao/         # Desktop DB factory
│           └── utils/       # TOTP Desktop impl
```

**Rule:** maximum code in `commonMain`. Only platform-specific APIs go in `androidMain`/`iosMain`/`desktopMain`.

## expect/actual Pattern

Declare API in `commonMain`, implement per platform:

### Database Factory

```kotlin
// commonMain — expect declaration
expect class DatabaseFactory {
    fun create(): RoomDatabase.Builder<AppDatabase>
}

// androidMain — actual implementation
actual class DatabaseFactory(private val context: Context) {
    actual fun create(): RoomDatabase.Builder<AppDatabase> {
        val dbFile = context.getDatabasePath("auth.db")
        return Room.databaseBuilder(context, AppDatabase::class.java, dbFile.absolutePath)
    }
}

// iosMain — actual implementation
actual class DatabaseFactory {
    actual fun create(): RoomDatabase.Builder<AppDatabase> {
        val dbFile = NSHomeDirectory() + "/Documents/auth.db"
        return Room.databaseBuilder(AppDatabase::class.java, dbFile)
    }
}

// desktopMain — actual implementation
actual class DatabaseFactory {
    actual fun create(): RoomDatabase.Builder<AppDatabase> {
        val dbFile = File(System.getProperty("user.home"), ".auth/auth.db")
        return Room.databaseBuilder(AppDatabase::class.java, dbFile.absolutePath)
    }
}
```

### TOTP Generator (Crypto differs per platform)

```kotlin
// commonMain
expect class TOTPGenerator() {
    fun generateCode(secret: String, timeStep: Long = 30L): String
}

// androidMain — uses javax.crypto
actual class TOTPGenerator actual constructor() {
    actual fun generateCode(secret: String, timeStep: Long): String {
        val key = SecretKeySpec(Base32.decode(secret), "HmacSHA1")
        val mac = Mac.getInstance("HmacSHA1")
        mac.init(key)
        val time = System.currentTimeMillis() / 1000 / timeStep
        val hash = mac.doFinal(time.toByteArray())
        return extractOtp(hash)
    }
}

// iosMain — uses CommonCrypto
actual class TOTPGenerator actual constructor() {
    actual fun generateCode(secret: String, timeStep: Long): String {
        // CommonCrypto HMAC implementation
        // ...
    }
}
```

### Platform Time

```kotlin
// commonMain
expect fun getCurrentTimeSeconds(): Long

// androidMain
actual fun getCurrentTimeSeconds(): Long = System.currentTimeMillis() / 1000

// iosMain
actual fun getCurrentTimeSeconds(): Long =
    NSDate().timeIntervalSince1970.toLong()

// desktopMain
actual fun getCurrentTimeSeconds(): Long = System.currentTimeMillis() / 1000
```

## Shared ViewModel

```kotlin
// commonMain — ViewModel works across platforms with lifecycle-viewmodel-compose
class AuthViewModel(private val repository: AuthRepository) : ViewModel() {
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    val accounts: Flow<List<AuthAccount>> = combine(
        repository.getAllAccounts(),
        _searchQuery
    ) { accounts, query ->
        if (query.isBlank()) accounts
        else accounts.filter {
            it.serviceName.contains(query, ignoreCase = true)
        }
    }

    fun addAccount(account: AuthAccount) {
        viewModelScope.launch {
            repository.insertAccount(account)
        }
    }
}
```

```toml
# Dependency for shared ViewModel
lifecycle-viewmodel-compose = { module = "org.jetbrains.androidx.lifecycle:lifecycle-viewmodel-compose", version = "2.9.0" }
```

**CMP lifecycle note:** `collectAsStateWithLifecycle()` not available in `commonMain`. Use `collectAsState()` in shared code. On Android-specific composables, use the lifecycle-aware version.

## Koin DI in KMP

```kotlin
// commonMain — shared module
val sharedModule = module {
    single { AuthRepository(get()) }
    viewModel { AuthViewModel(get()) }
    single { ThemeManager() }
}

// commonMain — expect platform module
expect fun platformModule(): Module

// androidMain
actual fun platformModule(): Module = module {
    single<AuthAccountDao> {
        DatabaseFactory(get()).create()
            .fallbackToDestructiveMigration()
            .build()
            .authAccountDao()
    }
    single { TOTPGenerator() }
}

// iosMain
actual fun platformModule(): Module = module {
    single<AuthAccountDao> {
        DatabaseFactory().create()
            .fallbackToDestructiveMigration()
            .build()
            .authAccountDao()
    }
    single { TOTPGenerator() }
}

// Initialization — commonMain
fun initializeKoin() {
    startKoin {
        modules(sharedModule, platformModule())
    }
}
```

## Shared Compose UI

From Authenticator — entire UI in `commonMain`:

```kotlin
// commonMain — works on Android, iOS, Desktop
@Composable
fun App() {
    MaterialTheme {
        AuthenticatorApp()
    }
}

// Android entry point
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { App() }
    }
}

// iOS entry point
fun MainViewController(): UIViewController =
    ComposeUIViewController { App() }

// Desktop entry point
fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "Authenticator"
    ) { App() }
}
```

### Platform-Specific UI When Needed

```kotlin
// commonMain — expect composable
@Composable
expect fun PlatformStatusBar(isDark: Boolean)

// androidMain
@Composable
actual fun PlatformStatusBar(isDark: Boolean) {
    val systemUiController = rememberSystemUiController()
    systemUiController.setStatusBarColor(
        color = Color.Transparent,
        darkIcons = !isDark
    )
}

// iosMain
@Composable
actual fun PlatformStatusBar(isDark: Boolean) {
    // iOS handles this through UIKit appearance
}

// desktopMain
@Composable
actual fun PlatformStatusBar(isDark: Boolean) {
    // No-op on desktop
}
```

## Ktor for Networking in KMP

```kotlin
// commonMain
class AuthApi(private val client: HttpClient) {
    suspend fun getAccounts(): List<AccountDto> {
        return client.get("accounts").body()
    }

    suspend fun createAccount(dto: CreateAccountDto): AccountDto {
        return client.post("accounts") {
            contentType(ContentType.Application.Json)
            setBody(dto)
        }.body()
    }
}

// commonMain — shared client config
fun createHttpClient(): HttpClient {
    return HttpClient {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                prettyPrint = false
            })
        }
        install(Logging) {
            level = LogLevel.BODY
        }
        defaultRequest {
            url("https://api.example.com/v1/")
        }
    }
}
```

Platform engines:

```kotlin
// androidMain
actual fun createPlatformHttpClient(): HttpClient = HttpClient(OkHttp)

// iosMain
actual fun createPlatformHttpClient(): HttpClient = HttpClient(Darwin)

// desktopMain
actual fun createPlatformHttpClient(): HttpClient = HttpClient(CIO)
```

## Room vs SQLDelight for KMP

| Aspect | Room (2.7+) | SQLDelight |
|--------|-------------|------------|
| **KMP support** | Android + JVM + iOS (limited) | Full KMP (all targets) |
| **API style** | Annotations + DAO interface | Raw SQL + generated Kotlin |
| **Type safety** | Compile-time via KSP | Compile-time via SQL verification |
| **Flow support** | Built-in `Flow<List<T>>` | `.asFlow().mapToList()` |
| **Migration** | Auto + manual | Numbered `.sqm` files |
| **Learning curve** | Easier for Android devs | Easier for SQL-first devs |
| **Maturity on KMP** | Newer (2024+) | Battle-tested |

**Choose Room when:** team knows Room, targeting Android + iOS, using Koin/Hilt already.
**Choose SQLDelight when:** need all KMP targets, want SQL-first approach, complex queries.

From Authenticator — Room in KMP:

```kotlin
// commonMain
@Database(entities = [AuthAccountEntity::class], version = 1)
@ConstructedBy(AppDatabaseConstructor::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun authAccountDao(): AuthAccountDao
}

@Suppress("NO_ACTUAL_FOR_EXPECT")
expect object AppDatabaseConstructor : RoomDatabaseConstructor<AppDatabase>
```

## Anti-Patterns

- **Platform-specific code in commonMain** → won't compile on other targets. Use expect/actual
- **`Context` in shared ViewModel** → Android-only. Inject platform abstractions via DI
- **`collectAsStateWithLifecycle` in commonMain** → not available. Use `collectAsState` in shared code
- **Hardcoded file paths** → each platform has different file system. Use expect/actual for paths
- **Skipping `iosMain` implementations** → will crash on iOS launch. Always implement all expect declarations
- **Single platform Engine for Ktor** → use expect/actual to pick OkHttp/Darwin/CIO per platform
