# Testing — ViewModels, Compose UI, Hilt, E2E

## Contents

- ViewModel testing with Turbine
- TestDispatcher setup
- Compose UI testing
- Hilt testing — TestInstallIn, fakes
- What to test, what to skip

## ViewModel Testing with Turbine

Turbine = library for testing Kotlin Flows. Essential for testing ViewModels.

```toml
[dependencies]
turbine = { module = "app.cash.turbine:turbine", version = "1.2.0" }
kotlinx-coroutines-test = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-test", version.ref = "coroutines" }
```

### Basic ViewModel Test

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
    fun `initial state is loading`() = runTest {
        viewModel.uiState.test {
            val initial = awaitItem()
            assertTrue(initial.isLoading)
        }
    }

    @Test
    fun `accounts loaded after init`() = runTest {
        val accounts = listOf(
            AuthAccount("1", "Google", "test@gmail.com", "secret", "🔍")
        )
        fakeRepo.emitAccounts(accounts)

        viewModel.uiState.test {
            skipItems(1)  // skip loading state
            val loaded = awaitItem()
            assertFalse(loaded.isLoading)
            assertEquals(1, loaded.accounts.size)
            assertEquals("Google", loaded.accounts.first().serviceName)
        }
    }

    @Test
    fun `search filters accounts`() = runTest {
        fakeRepo.emitAccounts(listOf(
            AuthAccount("1", "Google", "test@gmail.com", "s1", "🔍"),
            AuthAccount("2", "GitHub", "user", "s2", "🐙")
        ))

        viewModel.uiState.test {
            skipItems(1)  // loading
            awaitItem()   // all accounts

            viewModel.onSearchChanged("git")
            val filtered = awaitItem()
            assertEquals(1, filtered.accounts.size)
            assertEquals("GitHub", filtered.accounts.first().serviceName)
        }
    }

    @Test
    fun `delete account removes from list`() = runTest {
        fakeRepo.emitAccounts(listOf(
            AuthAccount("1", "Google", "test", "s1", "🔍")
        ))

        viewModel.uiState.test {
            skipItems(1)
            awaitItem()  // 1 account

            viewModel.onDeleteAccount("1")
            val afterDelete = awaitItem()
            assertTrue(afterDelete.accounts.isEmpty())
        }
    }
}
```

### FakeRepository

```kotlin
class FakeAuthRepository : AuthRepository {
    private val accounts = MutableStateFlow<List<AuthAccount>>(emptyList())

    fun emitAccounts(list: List<AuthAccount>) {
        accounts.value = list
    }

    override fun getAllAccounts(): Flow<List<AuthAccount>> = accounts

    override suspend fun insertAccount(account: AuthAccount) {
        accounts.update { it + account }
    }

    override suspend fun deleteAccountById(id: String) {
        accounts.update { list -> list.filter { it.id != id } }
    }

    override suspend fun getAccountById(id: String): AuthAccount? =
        accounts.value.find { it.id == id }

    override fun searchAccounts(query: String): Flow<List<AuthAccount>> =
        accounts.map { list ->
            list.filter { it.serviceName.contains(query, ignoreCase = true) }
        }
}
```

**Fakes over mocks.** Fakes implement the interface with in-memory data. Mocks (Mockito/MockK) verify method calls but don't test behavior. Fakes catch bugs mocks miss.

## TestDispatcher Setup

```kotlin
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

**Why:** ViewModels use `viewModelScope` which dispatches on `Dispatchers.Main`. Tests run on JVM — no Main dispatcher. `MainDispatcherRule` replaces Main with test dispatcher.

`UnconfinedTestDispatcher` — executes eagerly (no delay). Use for most ViewModel tests.
`StandardTestDispatcher` — requires `advanceUntilIdle()`. Use when testing timing-sensitive code.

## Compose UI Testing

```kotlin
class AccountsScreenTest {
    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun `displays account list`() {
        val accounts = listOf(
            AuthAccount("1", "Google", "test@gmail.com", "s1", "🔍"),
            AuthAccount("2", "GitHub", "user", "s2", "🐙")
        )

        composeRule.setContent {
            MaterialTheme {
                AccountsContent(
                    accounts = accounts,
                    searchQuery = "",
                    onSearchChanged = {},
                    onDelete = {},
                    onAdd = {}
                )
            }
        }

        composeRule.onNodeWithText("Google").assertIsDisplayed()
        composeRule.onNodeWithText("GitHub").assertIsDisplayed()
    }

    @Test
    fun `search bar filters content`() {
        var capturedQuery = ""
        composeRule.setContent {
            AccountsContent(
                accounts = emptyList(),
                searchQuery = "",
                onSearchChanged = { capturedQuery = it },
                onDelete = {},
                onAdd = {}
            )
        }

        composeRule.onNodeWithTag("search_bar").performTextInput("Google")
        assertEquals("Google", capturedQuery)
    }

    @Test
    fun `delete button triggers callback`() {
        var deletedId = ""
        composeRule.setContent {
            AccountCard(
                account = AuthAccount("1", "Google", "test", "s1", "🔍"),
                onDelete = { deletedId = it }
            )
        }

        composeRule.onNodeWithContentDescription("Delete account")
            .performClick()
        assertEquals("1", deletedId)
    }
}
```

### Test Tags

```kotlin
// In production code
TextField(
    modifier = Modifier.testTag("search_bar"),
    value = query,
    onValueChange = onQueryChange
)

// In test
composeRule.onNodeWithTag("search_bar").performTextInput("query")
```

### Testing Content Composable, Not Screen

```kotlin
// DON'T test the screen with ViewModel — that's integration testing
// DO test the stateless content composable
@Composable
fun AccountsContent(  // ← test this
    accounts: List<AuthAccount>,
    searchQuery: String,
    onSearchChanged: (String) -> Unit,
    onDelete: (String) -> Unit,
    onAdd: (AuthAccount) -> Unit
)
```

Stateless content composables are pure functions of their params. Easy to test in isolation.

## Hilt Testing

### TestInstallIn — Replace Module

```kotlin
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
abstract class TestRepositoryModule {
    @Binds
    @Singleton
    abstract fun bindRepo(impl: FakeAuthRepository): AuthRepository
}

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class AccountsIntegrationTest {
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeRule = createAndroidComposeRule<MainActivity>()

    @Inject
    lateinit var repo: AuthRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun fullAccountFlow() {
        // Test with real DI graph but fake repository
        composeRule.onNodeWithText("Add Account").performClick()
        // ...
    }
}
```

## What to Test vs Skip

### Always Test
| What | Why | Tool |
|------|-----|------|
| ViewModel state logic | Core business logic | Turbine + runTest |
| Flow transformations | combine, map, filter correctness | Turbine |
| Error handling paths | Failure states must work | Fake that throws |
| Repository mapping | DTO/Entity → Domain correctness | Unit test |

### Test If Time Allows
| What | Why | Tool |
|------|-----|------|
| Compose UI rendering | Catch layout regressions | composeRule |
| Navigation flows | Correct destination on actions | TestNavHostController |
| Accessibility | TalkBack reads correctly | semantics assertions |

### Skip
| What | Why |
|------|-----|
| Room DAO queries (simple) | Room's annotation processor generates correct SQL |
| Hilt module wiring | Compile-time verified |
| UI pixel perfection | Screenshot tests are brittle, use design review instead |
| External API calls | Mock the repository, not the HTTP client |

## Test File Organization

```
src/test/             # Unit tests (JVM, fast)
├── viewmodel/
│   ├── AuthViewModelTest.kt
│   └── WorkoutViewModelTest.kt
├── repository/
│   └── AuthRepositoryTest.kt
└── fakes/
    ├── FakeAuthRepository.kt
    └── FakeWorkoutRepository.kt

src/androidTest/      # Instrumented tests (device/emulator)
├── ui/
│   ├── AccountsScreenTest.kt
│   └── WorkoutFlowTest.kt
└── navigation/
    └── AppNavigationTest.kt
```

## Anti-Patterns

- **Mocking everything with MockK** → tests pass but don't verify behavior. Fakes > mocks
- **Testing ViewModel with real repository** → slow, flaky, tests two things. Use fake
- **`Thread.sleep()` in tests** → flaky. Use `advanceUntilIdle()` or Turbine's `awaitItem()`
- **Testing private ViewModel functions** → test through public state. If `_calculateScore()` is correct, `state.score` reflects it
- **One giant test class** → split by feature. `AuthViewModelTest`, `WorkoutViewModelTest`
- **No test dispatcher rule** → tests hang or fail on `Dispatchers.Main`. Always include `MainDispatcherRule`
