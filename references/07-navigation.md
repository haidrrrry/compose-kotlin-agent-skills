# Navigation — Nav 3, Type-Safe Routes, Deep Links

## Contents

- Navigation 3 overview
- Type-safe routes with @Serializable
- Deep links
- Back stack management
- Shared element transitions
- Bottom nav + nested graphs
- Migration from Nav 2

## Navigation 3 Overview

Nav 3 (androidx.navigation 2.9+) uses `@Serializable` data classes as routes instead of string paths.

```toml
[dependencies]
navigation-compose = { module = "androidx.navigation:navigation-compose", version = "2.9.0" }
kotlinx-serialization-json = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version = "1.8.1" }
```

## Type-Safe Routes

```kotlin
// Define routes as @Serializable classes
@Serializable
object Home

@Serializable
object Settings

@Serializable
data class AccountDetail(val accountId: String)

@Serializable
data class Workout(val type: String, val difficulty: String = "standard")

// NavHost setup
@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = Home) {

        composable<Home> {
            HomeScreen(
                onAccountClick = { id ->
                    navController.navigate(AccountDetail(accountId = id))
                },
                onSettingsClick = { navController.navigate(Settings) }
            )
        }

        composable<AccountDetail> { backStackEntry ->
            val route = backStackEntry.toRoute<AccountDetail>()
            AccountDetailScreen(
                accountId = route.accountId,
                onBack = { navController.popBackStack() }
            )
        }

        composable<Settings> {
            SettingsScreen(onBack = { navController.popBackStack() })
        }

        composable<Workout> { backStackEntry ->
            val route = backStackEntry.toRoute<Workout>()
            WorkoutScreen(
                workoutType = route.type,
                difficulty = route.difficulty
            )
        }
    }
}
```

**Why @Serializable routes:** compile-time type safety. String routes like `"detail/$id"` crash at runtime if you typo the arg name. Serializable routes fail at compile time.

## Deep Links

### Implicit Deep Links

```kotlin
composable<AccountDetail>(
    deepLinks = listOf(
        navDeepLink<AccountDetail>(
            basePath = "https://myapp.com/account"
        )
    )
) { backStackEntry ->
    val route = backStackEntry.toRoute<AccountDetail>()
    AccountDetailScreen(accountId = route.accountId)
}
```

```xml
<!-- AndroidManifest.xml -->
<activity android:name=".MainActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="https" android:host="myapp.com" />
    </intent-filter>
</activity>
```

### Explicit Deep Links (Internal Navigation)

```kotlin
// From notification or accessibility service
val intent = Intent(context, MainActivity::class.java).apply {
    data = "https://myapp.com/account?accountId=abc123".toUri()
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
}
context.startActivity(intent)
```

## Back Stack Management

### Pop to Specific Destination

```kotlin
// Pop back to Home, removing everything above it
navController.popBackStack(route = Home, inclusive = false)

// Navigate and clear back stack (login → home)
navController.navigate(Home) {
    popUpTo(navController.graph.startDestinationId) { inclusive = true }
    launchSingleTop = true
}
```

### Single Top — Prevent Duplicate Destinations

```kotlin
navController.navigate(Settings) {
    launchSingleTop = true  // reuse existing instance instead of creating new
}
```

### Save and Restore State (Tab Navigation)

```kotlin
fun NavHostController.navigateToTab(route: Any) {
    navigate(route) {
        popUpTo(graph.startDestinationId) {
            saveState = true     // save state of popped destinations
        }
        launchSingleTop = true
        restoreState = true      // restore state when re-selecting tab
    }
}
```

## Bottom Navigation + Nested Graphs

```kotlin
@Serializable object HomeGraph
@Serializable object ProgressGraph
@Serializable object SettingsGraph

@Serializable object HomeRoot
@Serializable object ProgressRoot
@Serializable object SettingsRoot
@Serializable data class WorkoutDetail(val id: String)

@Composable
fun MainScreen() {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            NavigationBar {
                val currentEntry by navController.currentBackStackEntryAsState()
                val currentRoute = currentEntry?.destination?.route

                NavigationBarItem(
                    selected = currentRoute?.contains("Home") == true,
                    onClick = { navController.navigateToTab(HomeGraph) },
                    icon = { Icon(Icons.Default.Home, "Home") },
                    label = { Text("Home") }
                )
                NavigationBarItem(
                    selected = currentRoute?.contains("Progress") == true,
                    onClick = { navController.navigateToTab(ProgressGraph) },
                    icon = { Icon(Icons.Default.Timeline, "Progress") },
                    label = { Text("Progress") }
                )
                NavigationBarItem(
                    selected = currentRoute?.contains("Settings") == true,
                    onClick = { navController.navigateToTab(SettingsGraph) },
                    icon = { Icon(Icons.Default.Settings, "Settings") },
                    label = { Text("Settings") }
                )
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = HomeGraph,
            modifier = Modifier.padding(padding)
        ) {
            navigation<HomeGraph>(startDestination = HomeRoot) {
                composable<HomeRoot> {
                    HomeScreen(onWorkoutClick = { id ->
                        navController.navigate(WorkoutDetail(id))
                    })
                }
                composable<WorkoutDetail> { /* ... */ }
            }

            navigation<ProgressGraph>(startDestination = ProgressRoot) {
                composable<ProgressRoot> { ProgressScreen() }
            }

            navigation<SettingsGraph>(startDestination = SettingsRoot) {
                composable<SettingsRoot> { SettingsScreen() }
            }
        }
    }
}
```

**Nested graphs** give each tab its own back stack. Navigating between tabs preserves scroll position and state.

## Passing Complex Data

```kotlin
// WRONG — serializing entire object through nav args
navController.navigate(AccountDetail(account = entireAccountObject))

// RIGHT — pass ID, fetch in destination ViewModel
@Serializable
data class AccountDetail(val accountId: String)  // just the ID

@HiltViewModel
class AccountDetailViewModel @Inject constructor(
    private val repo: AuthRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    private val accountId: String = savedStateHandle.toRoute<AccountDetail>().accountId

    val account: StateFlow<AuthAccount?> = repo.getAccountById(accountId)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)
}
```

**Rule:** nav args = IDs and simple primitives. Fetch the full object from ViewModel/Repository on the destination screen.

## Shared Element Transitions

```kotlin
@Composable
fun AppNavHost(navController: NavHostController) {
    SharedTransitionLayout {
        NavHost(navController = navController, startDestination = Home) {
            composable<Home> {
                HomeScreen(
                    onAccountClick = { account ->
                        navController.navigate(AccountDetail(account.id))
                    },
                    animatedVisibilityScope = this
                )
            }
            composable<AccountDetail> {
                AccountDetailScreen(
                    animatedVisibilityScope = this
                )
            }
        }
    }
}

@Composable
fun AccountCard(
    account: AuthAccount,
    onClick: () -> Unit,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Card(
            modifier = Modifier
                .sharedElement(
                    state = rememberSharedContentState(key = "card-${account.id}"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
                .clickable(onClick = onClick)
        ) {
            Text(
                text = account.serviceName,
                modifier = Modifier.sharedElement(
                    state = rememberSharedContentState(key = "name-${account.id}"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
            )
        }
    }
}
```

**Keys must match** between source and destination. Use consistent key generation: `"card-${id}"`, `"name-${id}"`.

## Anti-Patterns

- **String route paths** → use `@Serializable` routes. String typos crash at runtime
- **Passing Parcelable/Serializable objects as nav args** → pass IDs, fetch on destination
- **`navigate()` without `launchSingleTop`** → rapid taps create duplicate destinations
- **Nested `NavHost` for bottom tabs** → use nested `navigation()` graphs in single NavHost
- **ViewModel in nav args** → ViewModels are scoped to lifecycle, not navigation. Use `hiltViewModel()` scoped to back stack entry
- **Forgetting `popUpTo` on login→home** → user presses back from home and sees login again
