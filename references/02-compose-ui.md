# Compose UI — Composition, Recomposition, Material 3, Theming

## Contents

- Composition and recomposition deep dive
- Stability — @Stable, @Immutable, why it matters
- Modifier chain best practices
- Slot APIs and component design
- Material 3 — proper usage and tokens
- Dark/Light mode — custom color token architecture
- Premium UI systems — typography scale
- Adaptive layouts — WindowSizeClass, foldables

## Composition and Recomposition

### The Three Phases

```
Composition → Layout → Drawing
(WHAT to show)  (WHERE to place)  (HOW to render)
```

State reads in each phase only trigger work for that phase onward:
- State read in Composition → recomposition → relayout → redraw
- State read in Layout (via `Modifier.layout {}`) → relayout → redraw
- State read in Drawing (via `Modifier.drawBehind {}`) → redraw only

**Performance insight:** defer state reads to the latest possible phase.

```kotlin
// BAD — triggers full recomposition on every scroll offset change
@Composable
fun ParallaxHeader(scrollState: ScrollState) {
    val offset = scrollState.value  // read in Composition phase
    Image(
        modifier = Modifier.offset(y = (-offset / 2).dp)
    )
}

// GOOD — offset read deferred to Layout phase, skips recomposition
@Composable
fun ParallaxHeader(scrollState: ScrollState) {
    Image(
        modifier = Modifier.offset {
            IntOffset(0, -scrollState.value / 2)  // read in Layout phase
        }
    )
}
```

### Recomposition Scope

Compose recomposes the nearest restartable scope. A scope = a non-inline `@Composable` function that returns `Unit`.

```kotlin
// BAD — entire Column recomposes when name changes
@Composable
fun Profile(name: String, avatarUrl: String) {
    Column {
        Text(name)           // name changed
        Avatar(avatarUrl)    // recomposes unnecessarily
        SettingsButton()     // recomposes unnecessarily
    }
}

// GOOD — extract into separate composables = separate scopes
@Composable
fun Profile(name: String, avatarUrl: String) {
    Column {
        NameText(name)       // own scope — only this recomposes
        Avatar(avatarUrl)    // skipped if avatarUrl unchanged
        SettingsButton()     // skipped — no params changed
    }
}

@Composable
private fun NameText(name: String) {
    Text(name)
}
```

### What Triggers Recomposition

| Trigger | Example |
|---------|---------|
| `mutableStateOf` value changes | `var count by mutableStateOf(0); count++` |
| `StateFlow` emits new value | `_state.update { it.copy(name = "new") }` |
| Parent recomposes with new params | `ChildComposable(newParam)` |
| `CompositionLocal` value changes | `LocalAppTheme provides newTheme` |

What does NOT trigger recomposition:
- Reading a non-state variable
- A `remember`ed value (unless its key changes)
- A stable parameter that equals the previous value (skipping)

## Stability

Compose compiler determines if parameters changed by checking **stability**. Stable types enable skipping — unstable types always recompose.

### Automatically Stable
- Primitives (`Int`, `Float`, `Boolean`, `String`)
- `enum class`
- `@Immutable` annotated classes
- `@Stable` annotated classes
- Function types (lambdas) — but only if captured values are stable

### Automatically Unstable
- `List`, `Map`, `Set` (mutable collection interfaces)
- Classes from external modules without Compose compiler
- Classes with `var` properties

```kotlin
// UNSTABLE — List is a mutable interface, Compose can't prove immutability
data class AccountsUiState(
    val accounts: List<AuthAccount> = emptyList()  // unstable!
)

// Fix 1: @Immutable annotation (promise to Compose compiler)
@Immutable
data class AccountsUiState(
    val accounts: List<AuthAccount> = emptyList()
)

// Fix 2: Use kotlinx.collections.immutable
data class AccountsUiState(
    val accounts: ImmutableList<AuthAccount> = persistentListOf()
)
```

**When to annotate:**
- `@Immutable` — value NEVER changes after construction. All properties `val`. Use for UiState.
- `@Stable` — value CAN change, but Compose is notified via snapshot system. Use for wrapper classes with `mutableStateOf` inside.

**Strong skipping mode** (Compose compiler 2.0+): enabled by default. Lambdas auto-remembered, unstable params compared by `equals`. Reduces need for manual `@Stable` annotations but doesn't eliminate it for collection-heavy states.

## Modifier Chain Best Practices

### Order Matters — Mental Model

Read modifiers outside → inside. Each modifier wraps the next one:

```kotlin
Modifier
    .fillMaxWidth()                          // 1. take full width
    .padding(horizontal = 16.dp)             // 2. outer spacing (margin)
    .shadow(4.dp, RoundedCornerShape(12.dp)) // 3. shadow before clip
    .clip(RoundedCornerShape(12.dp))         // 4. clip shape
    .background(MaterialTheme.colorScheme.surface)  // 5. fill color
    .clickable { onClick() }                 // 6. ripple inside clipped area
    .padding(16.dp)                          // 7. inner spacing (padding)
```

### Common Ordering Rules

| Goal | Modifier Order |
|------|---------------|
| Card with shadow | `padding → shadow → clip → background → clickable → padding` |
| Clickable row | `fillMaxWidth → clip → clickable → padding` |
| Icon button | `size → clip(CircleShape) → clickable → padding` |
| Colored badge | `clip → background → padding` |

### Gotcha — Clickable Before vs After Padding

```kotlin
// Clickable BEFORE padding → touch target includes padding (bigger)
Modifier.clickable { }.padding(16.dp)

// Clickable AFTER padding → touch target excludes padding (smaller)
Modifier.padding(16.dp).clickable { }
```

For accessibility, touch targets should be at least 48dp. Put clickable BEFORE inner padding.

## Slot APIs and Component Design

Slot API = composable parameter instead of data parameter. Gives caller control over content.

```kotlin
// BAD — rigid, can only show text
@Composable
fun AppCard(title: String, subtitle: String) {
    Card {
        Text(title)
        Text(subtitle)
    }
}

// GOOD — slot API, caller decides content
@Composable
fun AppCard(
    modifier: Modifier = Modifier,
    header: @Composable () -> Unit = {},
    content: @Composable ColumnScope.() -> Unit,
    footer: @Composable () -> Unit = {}
) {
    Card(modifier = modifier) {
        header()
        Column(content = content)
        footer()
    }
}

// Usage — flexible
AppCard(
    header = { Text("Account Details") },
    content = {
        AccountInfo(account)
        TimerProgress(timeRemaining)
    },
    footer = { CopyButton(onClick = onCopy) }
)
```

**Component contract checklist:**
1. First param: `modifier: Modifier = Modifier` (always)
2. Slot params: `@Composable () -> Unit` with defaults
3. Action params: lambdas (`onClick: () -> Unit`)
4. Data params: domain types, not UI types
5. No ViewModel references

## Material 3 — Tokens and Dynamic Color

### Color Roles (Use These, Not Hardcoded Hex)

```kotlin
MaterialTheme.colorScheme.primary          // brand color
MaterialTheme.colorScheme.onPrimary        // text/icon on primary
MaterialTheme.colorScheme.primaryContainer // lighter brand for containers
MaterialTheme.colorScheme.surface          // card/sheet background
MaterialTheme.colorScheme.onSurface        // text on surface
MaterialTheme.colorScheme.surfaceVariant   // secondary surface
MaterialTheme.colorScheme.error            // error state
MaterialTheme.colorScheme.outline          // borders, dividers
```

### Dynamic Color (Android 12+)

```kotlin
@Composable
fun AppTheme(content: @Composable () -> Unit) {
    val colorScheme = when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (isSystemInDarkTheme()) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }
        isSystemInDarkTheme() -> darkColorScheme(/* custom dark */)
        else -> lightColorScheme(/* custom light */)
    }
    MaterialTheme(colorScheme = colorScheme, content = content)
}
```

## Custom Color Token Architecture

When M3 color roles don't cover your domain (timer colors, workout type colors, semantic states), build a custom token system:

From Authenticator — `AppColors` with Light/Dark variants:

```kotlin
object AppColors {
    object Light {
        val Primary = Color(0xFF6366F1)
        val Background = Color(0xFFF8FAFC)
        val Surface = Color(0xFFFFFFFF)
        val OnSurface = Color(0xFF0F172A)
        val CardBackground = Color(0xFFFFFFFF)
        val Success = Color(0xFF10B981)
        val Warning = Color(0xFFF59E0B)
        val Error = Color(0xFFEF4444)
        val TimerGood = Color(0xFF059669)
        val TimerWarning = Color(0xFFD97706)
        val TimerCritical = Color(0xFFDC2626)
    }
    object Dark {
        val Primary = Color(0xFF818CF8)      // lighter for dark bg
        val Background = Color(0xFF0F172A)
        val Surface = Color(0xFF1E293B)
        val OnSurface = Color(0xFFF8FAFC)
        val CardBackground = Color(0xFF1E293B)
        val Success = Color(0xFF34D399)
        val Warning = Color(0xFFFBBF24)
        val Error = Color(0xFFF87171)
        val TimerGood = Color(0xFF10B981)
        val TimerWarning = Color(0xFFF59E0B)
        val TimerCritical = Color(0xFFEF4444)
    }
}
```

Deliver via `CompositionLocal`:

```kotlin
data class AppTheme(
    val primary: Color,
    val background: Color,
    val surface: Color,
    val onSurface: Color,
    val cardBackground: Color,
    val success: Color,
    val warning: Color,
    val error: Color,
    val timerGood: Color,
    val timerWarning: Color,
    val timerCritical: Color,
    val isLight: Boolean
)

val LocalAppTheme = compositionLocalOf<AppTheme> {
    error("No AppTheme provided — wrap your content in ProvideAppTheme")
}

@Composable
fun ProvideAppTheme(
    themeManager: ThemeManager,
    content: @Composable () -> Unit
) {
    val themeMode by themeManager.themeMode.collectAsState()
    val isDark = when (themeMode) {
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
        ThemeMode.SYSTEM -> isSystemInDarkTheme()
    }
    val theme = if (isDark) AppTheme(
        primary = AppColors.Dark.Primary,
        background = AppColors.Dark.Background,
        // ... all dark tokens
        isLight = false
    ) else AppTheme(
        primary = AppColors.Light.Primary,
        background = AppColors.Light.Background,
        // ... all light tokens
        isLight = true
    )
    CompositionLocalProvider(LocalAppTheme provides theme, content = content)
}
```

**Access anywhere:**
```kotlin
val theme = LocalAppTheme.current
Box(modifier = Modifier.background(theme.cardBackground))
Text(color = theme.onSurface, text = "Hello")
```

## Typography Scale

```kotlin
val AppTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = FontFamily.SansSerif,
        fontWeight = FontWeight.ExtraBold,
        fontSize = 40.sp,
        lineHeight = 48.sp
    ),
    titleLarge = TextStyle(
        fontFamily = FontFamily.SansSerif,
        fontWeight = FontWeight.Bold,
        fontSize = 26.sp,
        lineHeight = 32.sp
    ),
    bodyLarge = TextStyle(
        fontFamily = FontFamily.SansSerif,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp
    ),
    labelLarge = TextStyle(
        fontFamily = FontFamily.SansSerif,
        fontWeight = FontWeight.Bold,
        fontSize = 15.sp,
        lineHeight = 20.sp
    )
)

// Usage — always through MaterialTheme
Text(
    text = "Account Name",
    style = MaterialTheme.typography.titleLarge
)
```

**Never use raw `fontSize` in composables.** Always reference typography tokens.

## Adaptive Layouts — WindowSizeClass

```kotlin
@Composable
fun AdaptiveApp() {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Phone — single pane, bottom nav
            PhoneLayout()
        }
        WindowWidthSizeClass.Medium -> {
            // Small tablet / foldable — navigation rail
            TabletLayout(showRail = true)
        }
        WindowWidthSizeClass.Expanded -> {
            // Large tablet / desktop — two pane
            TwoPaneLayout()
        }
    }
}
```

### Two-Pane Pattern

```kotlin
@Composable
fun TwoPaneLayout() {
    Row(modifier = Modifier.fillMaxSize()) {
        // List pane — 40% width
        AccountsList(
            modifier = Modifier.weight(0.4f),
            onAccountSelected = { selectedId = it }
        )
        // Detail pane — 60% width
        AccountDetail(
            modifier = Modifier.weight(0.6f),
            accountId = selectedId
        )
    }
}
```

**Foldable support:** use `WindowInfoTracker` from `androidx.window` to detect fold position and avoid placing content across the fold.

## Anti-Patterns

- **Hardcoded colors in composables** → use `MaterialTheme.colorScheme` or custom tokens via `CompositionLocal`
- **Raw `fontSize` / `fontWeight`** → use `MaterialTheme.typography` tokens
- **`remember { mutableStateOf() }` for ViewModel-level state** → survives recomposition, not config change. Use ViewModel + StateFlow
- **Nested scrolling without `nestedScroll`** → `LazyColumn` inside `Column(verticalScroll)` crashes. Use `LazyColumn` with mixed `item {}` blocks instead
- **`Box` with `Modifier.fillMaxSize()` as root** → use `Scaffold` for screens with top bar, bottom bar, FAB, snackbar
- **Ignoring `Modifier` parameter on public composables** → every public composable must accept `modifier: Modifier = Modifier` as first param
