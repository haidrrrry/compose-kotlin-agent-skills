# Todo MVI Example

Minimal MVI todo list demonstrating patterns from this skill kit. **Not a compilable Gradle module** — reference snippets for agents and humans. Copy into your app module.

## MVI patterns demonstrated

| Pattern | Where |
|---|---|
| `UiState` / `UiEvent` / `UiEffect` sealed types | `TodoViewModel.kt` |
| Atomic `_state.update { it.copy(...) }` | `TodoViewModel.kt` |
| `SharedFlow` / `Channel` for one-shot effects | `TodoViewModel.kt` |
| `@HiltViewModel` + constructor injection | `TodoViewModel.kt` |
| `collectAsStateWithLifecycle()` | `TodoScreen.kt` |
| `LazyColumn` + `key` + `contentType` | `TodoScreen.kt` |
| `stringResource()` for all UI text | `TodoScreen.kt` |
| Repository + Room Flow offline-first | `TodoRepository.kt` |

## Antipatterns avoided

See [`references/00-banned-antipatterns.md`](../references/00-banned-antipatterns.md):

| Row | Antipattern | How this example avoids it |
|---|---|---|
| 1 | `GlobalScope` | `viewModelScope` only |
| 3 | Hardcoded strings | `stringResource(R.string.*)` in screen |
| 4 | `collectAsState()` | `collectAsStateWithLifecycle()` |
| 5 | `_state.value =` | `_state.update { }` throughout VM |
| 6 | `mutableStateListOf` in VM | `StateFlow<List<TodoUi>>` |
| 7 | LazyColumn without key | `key = { it.id }` + `contentType` |
| 8 | Pass ViewModel to child | Pass `state` + `onEvent` lambda |

## Files

- [`TodoViewModel.kt`](TodoViewModel.kt) — MVI core
- [`TodoScreen.kt`](TodoScreen.kt) — Compose UI
- [`TodoRepository.kt`](TodoRepository.kt) — offline-first data

## Verification prompt

> "Review `examples/todo-mvi/TodoScreen.kt` in REVIEW MODE."

Expected: 6-point checklist from [`skills/android-kotlin-compose/SKILL.md`](../skills/android-kotlin-compose/SKILL.md).
