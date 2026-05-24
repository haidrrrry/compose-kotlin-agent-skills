---
name: android-kotlin-compose
description: >
  Jetpack Compose UI engineering for 2026 — edge-to-edge, Material 3, recomposition
  stability, Modifier ordering, LazyColumn performance, and animations. Use when building
  composables, fixing jank, theming, adaptive layouts, Canvas drawing, auditing screens,
  or asking "why does my screen recompose", "Modifier order", "edge to edge Compose",
  "audit this composable", "review this screen".
---

# Android Kotlin — Compose UI Module

Parent kit: [`../../SKILL.md`](../../SKILL.md) · Index: [`../../AGENTS.md`](../../AGENTS.md) · Banned list: [`../../references/00-banned-antipatterns.md`](../../references/00-banned-antipatterns.md)

## REVIEW MODE

**Trigger phrases:** "audit this file", "check this composable", "review this screen", "review mode", "a11y pass on this composable".

When triggered, **silently run this 6-point checklist** on the target file before responding. Cite failures by checklist number and banned-antipattern row from [`../../references/00-banned-antipatterns.md`](../../references/00-banned-antipatterns.md).

| # | Check | Fail if |
|---|-------|---------|
| 1 | **Modifier param** | Missing `modifier: Modifier = Modifier` or not last optional param |
| 2 | **State hoisting** | Screen/business state inside `@Composable` that belongs in ViewModel |
| 3 | **Lazy list keys** | `LazyColumn`/`LazyRow` items missing `key = {}` or `contentType = {}` |
| 4 | **Lifecycle collection** | Uses `collectAsState()` instead of `collectAsStateWithLifecycle()` |
| 5 | **Side effects in composition** | IO, DB, network, or `viewModelScope` work directly in composable body |
| 6 | **Stability** | Data class params to child composables lack `@Stable` or `@Immutable` |

**Output format for REVIEW MODE:**

```
## Compose audit — <filename>

| # | Status | Finding |
|---|--------|---------|
| 1 | PASS/FAIL | ... |
...

### Banned antipatterns hit
- Row N: <pattern> → <fix>

### Suggested diff
<code block with minimal fix>
```

Load [`../../references/17-accessibility.md`](../../references/17-accessibility.md) when audit includes TalkBack, touch targets, or contrast.

---

## AUTHORING MODE

Default behavior when **writing new Compose UI** (not auditing). Follow all rules below.

## Read First

| File | When |
|------|------|
| [`../../references/02-compose-ui.md`](../../references/02-compose-ui.md) | Stability, slots, Material 3, CompositionLocal themes |
| [`../../references/03-animations.md`](../../references/03-animations.md) | Springs, Canvas, gestures |
| [`../../references/10-performance.md`](../../references/10-performance.md) | derivedStateOf, LazyColumn keys, baseline profiles |
| [`../../references/16-coil-image.md`](../../references/16-coil-image.md) | AsyncImage, Coil 3.4 network dep |
| [`../../references/17-accessibility.md`](../../references/17-accessibility.md) | Semantics, 48dp targets, WCAG |

## Edge-to-Edge (Default — AGP 9 / API 35+)

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContent {
            AppTheme {
                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    contentWindowInsets = WindowInsets(0, 0, 0, 0)
                ) { innerPadding ->
                    NavHost(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(innerPadding)
                    )
                }
            }
        }
    }
}
```

- `enableEdgeToEdge()` on every `ComponentActivity`
- Respect `WindowInsets` — never hardcode status bar padding
- Use `WindowInsets.safeDrawing` for interactive content
- Test gesture nav bar + display cutout on physical device

## Composable Contract

```kotlin
@Composable
fun AccountCard(
    account: AccountUi,
    onClick: () -> Unit,
    modifier: Modifier = Modifier  // always first param after required data
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
    ) {
        Text(
            text = stringResource(R.string.account_title, account.name),
            style = MaterialTheme.typography.titleMedium
        )
    }
}
```

## Recomposition Rules

1. Extract sub-composables for separate restart scopes
2. Defer scroll/animation reads: `Modifier.offset { IntOffset(...) }`
3. `@Immutable` on UiState / list wrappers passed to children
4. `remember(keys) { derivedStateOf { } }` for expensive derived values
5. Never write state in composable body after read (backwards write)

## LazyColumn Checklist

- [ ] `key = { it.id }` on every `items()`
- [ ] `contentType` when row layouts differ
- [ ] Stable lambdas: `remember(id) { { onClick(id) } }`
- [ ] No nested `verticalScroll` + `LazyColumn`
- [ ] Sort/filter in ViewModel or `remember`, not inline in `items {}`

## Anti-Patterns (Compose)

| Banned | Fix |
|--------|-----|
| Hardcoded `Text("Save")` | `stringResource(R.string.action_save)` |
| `collectAsState()` on Android | `collectAsStateWithLifecycle()` |
| `Modifier.clickable` before `padding` when touch target should exclude margin | Order: padding → clip → background → clickable |
| `items(list)` without key | `items(list, key = { it.id })` |
| Raw `fontSize = 16.sp` | `MaterialTheme.typography.bodyLarge` |

Full list: [`../../references/00-banned-antipatterns.md`](../../references/00-banned-antipatterns.md)
