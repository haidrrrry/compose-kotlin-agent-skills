---
name: banned-antipatterns
description: >
  Master lookup table of AI-hallucinated Android/Kotlin/Compose patterns with WRONG/RIGHT
  fixes. Use when reviewing agent output, auditing PRs, or before merging generated code.
version: "2.2.0"
updated: "2026-05-21"
---

# Banned Antipatterns — AI Hallucination Lookup

Load this file before reviewing any agent-generated Kotlin. Every row is a production bug waiting to ship.

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
| 21 | `SharedPreferences.edit().apply()` | `dataStore.edit { }` suspend | Race + main-thread ANR risk |
| 22 | `collectAsLazyPagingItems()` in VM | `pager.flow.asState()` + presenter collect | Wrong layer + stale paging |
| 23 | Coil `AsyncImage` without network dep | `coil-compose` + `coil-network-okhttp` | Images never load |
| 24 | `contentDescription = null` on icons | Meaningful description or `null` only if decorative | TalkBack failure |
| 25 | `kapt` for Hilt/Room new project | KSP (`ksp(...)`) | Slow builds, K2 incompatibility |

## How to use in review mode

When auditing a file, grep for each WRONG column pattern. If found, cite row number and apply RIGHT fix before approving.

Parent routing: [`../SKILL.md`](../SKILL.md) · Compose audit checklist: [`../skills/android-kotlin-compose/SKILL.md`](../skills/android-kotlin-compose/SKILL.md)
