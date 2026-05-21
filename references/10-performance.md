# Performance — Recomposition, Stability, LazyColumn, Baseline Profiles

## Contents

- Recomposition debugging
- Stability annotations
- derivedStateOf
- LazyColumn optimization
- Image loading — Coil 3
- Baseline profiles

## Recomposition Debugging

### Layout Inspector

1. Run app in debug mode
2. Android Studio → Layout Inspector → Select process
3. Enable "Show Recomposition Counts" in toolbar
4. Recomposition count shows how many times each composable recomposed
5. High numbers on static composables = problem

### Compose Compiler Metrics

```bash
# Add to build.gradle.kts
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P", "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${project.buildDir}/compose_metrics",
        "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${project.buildDir}/compose_reports"
    )
}
```

Generates:
- `*-composables.txt` — stability of each composable's params
- `*-classes.txt` — stability of each class
- `*-module.json` — summary stats

Look for `UNSTABLE` params. Each unstable param prevents skipping.

## Stability Annotations

### @Immutable — Value Never Changes

```kotlin
@Immutable
data class AccountsUiState(
    val accounts: List<AuthAccount> = emptyList(),
    val searchQuery: String = "",
    val isLoading: Boolean = false
)
```

Promise to compiler: once constructed, no property changes. Enables skipping when same instance passed.

### @Stable — Changes Are Observable

```kotlin
@Stable
class ThemeManager {
    var themeMode by mutableStateOf(ThemeMode.SYSTEM)
        private set

    fun setTheme(mode: ThemeMode) { themeMode = mode }
}
```

Promise to compiler: if value changes, Compose snapshot system will know. Use for classes with `mutableStateOf` properties.

### When NOT to Annotate

```kotlin
// Already stable — primitives, String, enum
data class SimpleState(val count: Int, val name: String)  // auto-stable

// Don't lie — if class has var properties without mutableStateOf, @Stable is a lie
@Stable  // WRONG — regular var, Compose can't observe changes
class BadManager {
    var count = 0  // not mutableStateOf, changes invisible to Compose
}
```

## derivedStateOf

Memoize computed state — recalculates only when dependencies change.

```kotlin
@Composable
fun AccountsList(accounts: List<AuthAccount>, searchQuery: String) {
    // WRONG — recomputes on every recomposition
    val filtered = accounts.filter { it.serviceName.contains(searchQuery) }

    // RIGHT — only recomputes when accounts or searchQuery changes
    val filtered by remember(accounts, searchQuery) {
        derivedStateOf {
            accounts.filter { it.serviceName.contains(searchQuery, ignoreCase = true) }
        }
    }

    LazyColumn {
        items(filtered, key = { it.id }) { AccountCard(it) }
    }
}
```

### When derivedStateOf Matters

```kotlin
// Show "scroll to top" FAB only when scrolled past threshold
val listState = rememberLazyListState()

// WRONG — rechecks on every scroll pixel, triggers recomposition
val showFab = listState.firstVisibleItemIndex > 0

// RIGHT — only triggers recomposition when crossing threshold
val showFab by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 0 }
}
```

**Rule:** use `derivedStateOf` when:
1. State reads change frequently (scroll position, text input)
2. Derived value changes less frequently than input (boolean threshold from int)
3. Computation is non-trivial (filtering, sorting)

**Skip when:** input changes at same rate as output (simple property access).

## LazyColumn Optimization

### Keys — Always Provide

```kotlin
// WRONG — positional identity, breaks on reorder/delete
LazyColumn {
    items(accounts) { AccountCard(it) }
}

// RIGHT — stable key, correct identity across changes
LazyColumn {
    items(accounts, key = { it.id }) { AccountCard(it) }
}
```

### contentType — Enable Item Reuse

```kotlin
LazyColumn {
    item(contentType = "header") {
        SectionHeader("Active Accounts")
    }
    items(
        items = activeAccounts,
        key = { it.id },
        contentType = { "account_card" }  // Compose reuses composition for same type
    ) { account ->
        AccountCard(account)
    }
    item(contentType = "header") {
        SectionHeader("Archived")
    }
    items(
        items = archivedAccounts,
        key = { it.id },
        contentType = { "account_card" }
    ) { account ->
        AccountCard(account)
    }
}
```

### Avoid Allocations in Item Scope

```kotlin
// WRONG — new lambda every item, every recomposition
items(accounts, key = { it.id }) { account ->
    AccountCard(
        account = account,
        onClick = { viewModel.selectAccount(account.id) }  // new lambda each time
    )
}

// RIGHT — remember lambda with stable key
items(accounts, key = { it.id }) { account ->
    val onClick = remember(account.id) {
        { viewModel.selectAccount(account.id) }
    }
    AccountCard(account = account, onClick = onClick)
}
```

### Avoid Nesting Scrollable Containers

```kotlin
// WRONG — crashes or infinite size
Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
    LazyColumn { /* CRASH */ }
}

// RIGHT — single LazyColumn with mixed content
LazyColumn {
    item { Header() }
    item { SearchBar() }
    items(accounts, key = { it.id }) { AccountCard(it) }
    item { Footer() }
}
```

## Image Loading — Coil 3

```kotlin
// Setup — in Application or DI
val imageLoader = ImageLoader.Builder(context)
    .crossfade(true)
    .memoryCachePolicy(CachePolicy.ENABLED)
    .diskCachePolicy(CachePolicy.ENABLED)
    .build()

// Usage in Composable
AsyncImage(
    model = ImageRequest.Builder(LocalContext.current)
        .data(account.iconUrl)
        .crossfade(300)
        .placeholder(R.drawable.ic_placeholder)
        .error(R.drawable.ic_error)
        .build(),
    contentDescription = "${account.serviceName} icon",
    modifier = Modifier
        .size(48.dp)
        .clip(CircleShape),
    contentScale = ContentScale.Crop
)
```

### Coil in LazyColumn — Avoid Refetching

```kotlin
items(accounts, key = { it.id }) { account ->
    // Coil caches by URL — same URL won't refetch
    // But provide key to LazyColumn so item identity is stable
    AsyncImage(
        model = account.iconUrl,
        contentDescription = null,
        modifier = Modifier.size(40.dp).clip(CircleShape)
    )
}
```

```toml
[dependencies]
coil-compose = { module = "io.coil-kt.coil3:coil-compose", version.ref = "coil" }
coil-network-okhttp = { module = "io.coil-kt.coil3:coil-network-okhttp", version.ref = "coil" }
```

## Baseline Profiles

Precompile critical user paths ahead of time for faster startup and smoother scrolling.

### Generate

```kotlin
// Create benchmark module — app/src/androidTest/
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generateProfile() {
        rule.collect(
            packageName = "com.example.app",
            stableIterations = 3,
            maxIterations = 10
        ) {
            // Critical user journey
            startActivityAndWait()
            device.findObject(By.text("Accounts")).click()
            device.waitForIdle()
            // Scroll the list
            device.findObject(By.res("account_list")).also { list ->
                list.fling(Direction.DOWN)
                list.fling(Direction.UP)
            }
        }
    }
}
```

### Apply

```kotlin
// build.gradle.kts (app)
dependencies {
    implementation("androidx.profileinstaller:profileinstaller:1.4.1")
    baselineProfile(project(":benchmark"))
}

baselineProfile {
    automaticGenerationDuringBuild = true
}
```

### Verify

```bash
# Check if profile is included in APK
unzip -l app-release.apk | grep "baseline"
# Should show: assets/dexopt/baseline.prof
```

**Impact:** 20-40% faster startup, smoother first scroll in LazyColumn. Free performance — no code changes needed.

## Anti-Patterns

- **Not providing keys in LazyColumn** → item identity by position breaks on reorder/delete
- **`@Stable` on class with plain `var`** → lie to compiler. Use `mutableStateOf` for observable state
- **`derivedStateOf` for everything** → adds overhead for simple pass-through. Only when input changes faster than output
- **`remember {}` without keys** → stale value when params change. Add dependencies as keys
- **Loading full-resolution images in list** → OOM. Use Coil with size constraints, or thumbnail URLs
- **Skipping baseline profiles** → free 20-40% startup improvement. Generate and ship
