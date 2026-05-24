---
name: xml-to-compose-migration
description: >
  XML Views to Jetpack Compose migration — mapping table, ComposeView interop,
  ViewBinding removal, RxJava to Coroutines, checklist and pitfalls. Use when migrating legacy UI.
version: "2.2.0"
updated: "2026-05-21"
---

# XML → Compose Migration

## XML → Compose mapping table

| XML / View | Compose equivalent |
|---|---|
| `LinearLayout vertical` | `Column` |
| `LinearLayout horizontal` | `Row` |
| `FrameLayout` | `Box` |
| `ScrollView` | `Column` + `verticalScroll` or `LazyColumn` |
| `RecyclerView` | `LazyColumn` / `LazyRow` / `LazyVerticalGrid` |
| `TextView` | `Text` |
| `EditText` | `TextField` / `OutlinedTextField` |
| `ImageView` | `Image` / `AsyncImage` (Coil) |
| `Button` | `Button` / `TextButton` |
| `Toolbar` / `AppBarLayout` | `TopAppBar` + `Scaffold` |
| `BottomNavigationView` | `NavigationBar` |
| `Fragment` | Composable destination + `NavHost` |
| `ViewModel` + `LiveData` | `ViewModel` + `StateFlow` |
| `findViewById` | State + parameters |
| `Data Binding` | State hoisting + `collectAsStateWithLifecycle` |
| `ViewBinding` | Remove — pass state to Composables |

---

## WRONG / RIGHT 1 — ComposeView without dispose strategy

```kotlin
// WRONG — composition survives after fragment destroy
class LegacyFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, saved: Bundle?) =
        ComposeView(requireContext()).apply {
            setContent { LegacyScreen() }
        }
}

// RIGHT — ViewCompositionStrategy tied to lifecycle
class LegacyFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, saved: Bundle?) =
        ComposeView(requireContext()).apply {
            setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)
            setContent { LegacyScreen() }
        }
}
```

---

## WRONG / RIGHT 2 — Keeping ViewBinding alongside Compose in same screen

```kotlin
// WRONG — dual UI systems, state split
class ProfileActivity : AppCompatActivity() {
    private lateinit var binding: ActivityProfileBinding
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityProfileBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.composeHost.setContent { ProfileHeader() }  // half XML half Compose
        binding.nameText.text = viewModel.name  // duplicate state
    }
}

// RIGHT — full Compose Activity
class ProfileActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContent {
            AppTheme {
                ProfileScreen()
            }
        }
    }
}
```

---

## WRONG / RIGHT 3 — Migrating LiveData observers to Compose

```kotlin
// WRONG — observeAsState() from LiveData in new Compose code
@Composable
fun ProfileScreen(vm: ProfileViewModel) {
    val name by vm.nameLiveData.observeAsState("")
    Text(name)
}

// RIGHT — migrate VM to StateFlow first
@Composable
fun ProfileScreen(vm: ProfileViewModel = hiltViewModel()) {
    val state by vm.state.collectAsStateWithLifecycle()
    ProfileContent(state = state, onEvent = vm::onEvent)
}

class ProfileViewModel @Inject constructor(repo: ProfileRepository) : ViewModel() {
    private val _state = MutableStateFlow(ProfileUiState())
    val state: StateFlow<ProfileUiState> = _state.asStateFlow()
}
```

---

## WRONG / RIGHT 4 — RxJava chain left in repository during UI migration

```kotlin
// WRONG — RxJava in data layer, Compose UI expects coroutines
class UserRepository(private val api: Api) {
    fun loadUser(): Observable<User> =
        api.getUser().subscribeOn(Schedulers.io())
}

// RIGHT — suspend + Flow migration path
interface UserRepository {
    fun observeUser(id: String): Flow<User>
}

class UserRepositoryImpl @Inject constructor(
    private val api: Api,
    private val dao: UserDao
) : UserRepository {
    override fun observeUser(id: String): Flow<User> =
        dao.observeUser(id).map { it.toDomain() }

    suspend fun refresh(id: String) {
        val dto = api.fetchUser(id)
        dao.upsert(dto.toEntity())
    }
}
```

---

## WRONG / RIGHT 5 — RecyclerView.Adapter logic copied into LazyColumn items block

```kotlin
// WRONG — bind logic + click + image load inside item lambda
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(users) { user ->
            val bitmap = loadBitmap(user.avatarUrl)  // IO in composition
            Row(Modifier.clickable { navigate(user) }) {
                Image(bitmap.asImageBitmap(), null)
                Text(user.name)
            }
        }
    }
}

// RIGHT — stateless item composable, events up, Coil for images
@Composable
fun UserList(
    users: List<UserUi>,
    onUserClick: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(modifier = modifier) {
        items(
            items = users,
            key = { it.id },
            contentType = { "user" }
        ) { user ->
            UserRow(user = user, onClick = { onUserClick(user.id) })
        }
    }
}
```

---

## Migration checklist

- [ ] Inventory screens — prioritize leaf screens (settings, about) before root nav
- [ ] Replace `Fragment` + XML with Composable destinations one at a time
- [ ] Migrate `LiveData` → `StateFlow` in ViewModel before touching UI
- [ ] Migrate RxJava → suspend/Flow in repositories
- [ ] Remove ViewBinding/DataBinding generated code per migrated screen
- [ ] Add `enableEdgeToEdge()` when converting Activities
- [ ] Replace `RecyclerView` diff logic with stable `key` + immutable lists
- [ ] Run Compose UI tests for migrated screens
- [ ] Delete unused XML layouts + drawables after each screen lands

## Interop strategy (strangler fig)

1. **Phase A** — `ComposeView` in XML host for one component (toolbar, bottom sheet)
2. **Phase B** — Full screen Compose inside existing Activity
3. **Phase C** — Single `ComponentActivity` + Navigation Compose; delete XML nav graphs
4. **Phase D** — Remove AppCompat theme XML where Material3 Compose theme replaces it

## Common pitfalls

| Pitfall | Fix |
|---|---|
| State in XML and Compose | Single source in ViewModel `StateFlow` |
| `remember` for screen state | Hoist to ViewModel |
| Missing `key` after RecyclerView migration | `items(list, key = { it.id })` |
| Config change loses state | ViewModel + `rememberSaveable` only for UI-local state |
| Custom Views without Compose equivalent | `AndroidView` factory — migrate last |
