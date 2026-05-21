---
name: android-kotlin-architecture
description: >
  Enforces Clean Architecture, MVVM/MVI, and unidirectional data flow for Android apps.
  Covers UiState, UiEvent, UiEffect, UseCase boundaries, module structure, and atomic
  ViewModel state via _state.update. Use when structuring features, refactoring ViewModels,
  splitting modules, or asking "MVVM vs MVI", "where does state live", "UseCase when".
---

# Android Kotlin — Architecture Module

Parent kit: [`../../SKILL.md`](../../SKILL.md) · Index: [`../../AGENTS.md`](../../AGENTS.md)

## Read First

| File | When |
|------|------|
| [`../../references/01-architecture.md`](../../references/01-architecture.md) | Full MVVM/MVI patterns, container/content composables |
| [`../../references/04-coroutines-flow.md`](../../references/04-coroutines-flow.md) | StateFlow, Channel effects, stateIn |
| [`../../references/05-hilt-di.md`](../../references/05-hilt-di.md) | @HiltViewModel, repository wiring |
| [`../../references/06-room-db.md`](../../references/06-room-db.md) | Repository + Room offline-first |

## MVI Contract (Mandatory)

```kotlin
@Immutable
data class FeatureUiState(
    val items: List<ItemUi> = emptyList(),
    val isLoading: Boolean = false,
    val error: UiError? = null
)

sealed interface FeatureUiEvent {
    data class SearchChanged(val query: String) : FeatureUiEvent
    data object Refresh : FeatureUiEvent
    data class ItemClicked(val id: String) : FeatureUiEvent
}

sealed interface FeatureUiEffect {
    data class ShowMessage(@StringRes val messageRes: Int) : FeatureUiEffect
    data class NavigateToDetail(val id: String) : FeatureUiEffect
}

class FeatureViewModel @Inject constructor(
    private val repository: FeatureRepository
) : ViewModel() {

    private val _state = MutableStateFlow(FeatureUiState())
    val state: StateFlow<FeatureUiState> = _state.asStateFlow()

    private val _effects = Channel<FeatureUiEffect>(Channel.BUFFERED)
    val effects: Flow<FeatureUiEffect> = _effects.receiveAsFlow()

    fun onEvent(event: FeatureUiEvent) {
        when (event) {
            is FeatureUiEvent.SearchChanged -> onSearchChanged(event.query)
            FeatureUiEvent.Refresh -> refresh()
            is FeatureUiEvent.ItemClicked -> emitNavigate(event.id)
        }
    }

    private fun onSearchChanged(query: String) {
        _state.update { it.copy(searchQuery = query) }  // ONLY mutation style allowed
    }

    private fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            repository.sync()
                .onSuccess { _state.update { it.copy(isLoading = false) } }
                .onFailure { e ->
                    _state.update { it.copy(isLoading = false, error = e.toUiError()) }
                }
        }
    }

    private fun emitNavigate(id: String) {
        viewModelScope.launch { _effects.send(FeatureUiEffect.NavigateToDetail(id)) }
    }
}
```

## Module Layout (Large Apps)

```
app/
feature-<name>/
  presentation/   # Composables + ViewModel
  domain/         # Models, repository interfaces, UseCases
  data/           # Room, Ktor, mappers
core/
  core-ui/        # Design system
  core-domain/
  core-testing/
```

Feature modules must not depend on other feature modules — only `core-*` and `domain` contracts.

## UseCase Rule

| Use UseCase | Skip UseCase |
|-------------|--------------|
| Logic shared by 2+ ViewModels | Single-line repo delegate |
| Multi-repo orchestration | One ViewModel, one repo |
| Needs isolated unit tests | CRUD with no extra rules |

## Anti-Patterns (Architecture)

| Banned | Fix |
|--------|-----|
| `_state.value = newState` | `_state.update { it.copy(...) }` |
| God ViewModel (>200 lines) | Split screen or extract UseCases |
| ViewModel in composable params | Pass `onEvent` lambdas |
| Domain model with `@Entity` | Entity in `data/`, map in repository |
| Collecting Flow in `init` without `stateIn` | `stateIn(WhileSubscribed(5_000))` |
