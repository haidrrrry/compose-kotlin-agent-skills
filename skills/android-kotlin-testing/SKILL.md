---
name: android-kotlin-testing
description: >
  Android testing patterns — ViewModel unit tests with Turbine, Compose UI semantics,
  Hilt TestInstallIn fakes, coroutine test dispatchers, and release quality gates. Use when
  writing tests, setting up CI, mocking repositories, or asking "how to test ViewModel",
  "Compose UI test", "Turbine StateFlow".
---

# Android Kotlin — Testing Module

Parent kit: [`../../SKILL.md`](../../SKILL.md) · Index: [`../../AGENTS.md`](../../AGENTS.md)

## Read First

| File | When |
|------|------|
| [`../../references/11-testing.md`](../../references/11-testing.md) | Turbine, fakes, Compose test tags |
| [`../../references/05-hilt-di.md`](../../references/05-hilt-di.md) | TestInstallIn modules |
| [`../../references/13-release-checklist.md`](../../references/13-release-checklist.md) | Pre-ship checklist |

## ViewModel Test Template

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class FeatureViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val fakeRepo = FakeFeatureRepository()
    private lateinit var viewModel: FeatureViewModel

    @Before
    fun setup() {
        viewModel = FeatureViewModel(fakeRepo)
    }

    @Test
    fun `refresh success clears loading`() = runTest {
        fakeRepo.syncResult = Result.success(Unit)

        viewModel.onEvent(FeatureUiEvent.Refresh)

        viewModel.state.test {
            skipItems(1)
            val loading = awaitItem()
            assertTrue(loading.isLoading)
            val done = awaitItem()
            assertFalse(done.isLoading)
            assertNull(done.error)
        }
    }
}
```

## Fake Over Mock

```kotlin
class FakeFeatureRepository : FeatureRepository {
    var syncResult: Result<Unit> = Result.success(Unit)
    private val items = MutableStateFlow<List<Feature>>(emptyList())

    override fun observeItems(): Flow<List<Feature>> = items
    override suspend fun sync(): Result<Unit> = syncResult
}
```

Prefer fakes implementing real interfaces — tests behavior, not interaction order.

## Compose UI Test

```kotlin
class FeatureScreenTest {
    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun showsEmptyState() {
        composeRule.setContent {
            AppTheme {
                FeatureContent(
                    state = FeatureUiState(items = emptyList()),
                    onEvent = {}
                )
            }
        }
        composeRule.onNodeWithTag("feature_empty").assertIsDisplayed()
    }
}
```

Test **stateless** `FeatureContent`, not ViewModel-integrated screen.

## What to Test vs Skip

| Always test | Usually skip |
|-------------|--------------|
| ViewModel state transitions | Room generated SQL |
| Repository mappers | Hilt graph wiring (compile-time) |
| Error paths (`Result.failure`) | Pixel-perfect screenshots |
| Critical user flows (instrumented) | Third-party SDK internals |

## CI Gate

Repo skill validation must pass before merge:

```bash
python3 scripts/validate_skills.py --strict
```
