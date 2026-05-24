---
name: datastore
description: >
  Preferences DataStore vs Proto DataStore, SharedPreferences migration, typed keys,
  coroutine-safe reads/writes, security-crypto encryption. Use when replacing
  SharedPreferences or persisting user settings.
version: "2.2.0"
updated: "2026-05-21"
---

# DataStore — Preferences, Proto, Migration, Encryption

## Pinned versions (2026)

```toml
datastore = "1.1.7"
security-crypto = "1.1.0"
```

```kotlin
implementation("androidx.datastore:datastore-preferences:1.1.7")
implementation("androidx.datastore:datastore:1.1.7")
implementation("androidx.security:security-crypto:1.1.0")
```

## Preferences DataStore vs Proto DataStore

| | Preferences DataStore | Proto DataStore |
|---|---|---|
| Schema | Key-value (`booleanPreferencesKey`, etc.) | Protobuf message |
| Use when | Settings, flags, simple prefs | Typed structured config |
| Type safety | Keys are typed | Full proto schema |

---

## WRONG / RIGHT 1 — SharedPreferences.apply() on main thread

```kotlin
// WRONG — apply() is async but still blocks binder; commit() blocks main thread
fun saveTheme(context: Context, dark: Boolean) {
    context.getSharedPreferences("settings", Context.MODE_PRIVATE)
        .edit()
        .putBoolean("dark_mode", dark)
        .apply()
}

// RIGHT — suspend edit on DataStore IO dispatcher
private val Context.dataStore by preferencesDataStore(name = "settings")

suspend fun saveTheme(context: Context, dark: Boolean) {
    context.dataStore.edit { prefs ->
        prefs[booleanPreferencesKey("dark_mode")] = dark
    }
}
```

---

## WRONG / RIGHT 2 — Reading prefs synchronously in Composable

```kotlin
// WRONG — blocks composition; SharedPreferences on main thread
@Composable
fun ThemeToggle() {
    val context = LocalContext.current
    val dark = context.getSharedPreferences("settings", MODE_PRIVATE)
        .getBoolean("dark_mode", false)
    Switch(checked = dark, onCheckedChange = { /* ... */ })
}

// RIGHT — Flow from DataStore, collect with lifecycle
@Composable
fun ThemeToggle(vm: SettingsViewModel = hiltViewModel()) {
    val dark by vm.isDarkMode.collectAsStateWithLifecycle(initialValue = false)
    Switch(
        checked = dark,
        onCheckedChange = { vm.onEvent(SettingsEvent.DarkModeChanged(it)) }
    )
}

class SettingsViewModel @Inject constructor(
    private val settingsRepo: SettingsRepository
) : ViewModel() {
    val isDarkMode: StateFlow<Boolean> = settingsRepo.isDarkMode
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), false)
}
```

---

## WRONG / RIGHT 3 — Untyped string keys everywhere

```kotlin
// WRONG — typo-prone magic strings
dataStore.edit { it["dark_mode"] = true }  // won't compile on Preferences — good
// but agents write:
prefs.edit().putString("user_id", id).apply()

// RIGHT — typed keys in one object
object SettingsKeys {
    val DARK_MODE = booleanPreferencesKey("dark_mode")
    val USER_ID = stringPreferencesKey("user_id")
}

suspend fun DataStore<Preferences>.setDarkMode(enabled: Boolean) {
    edit { it[SettingsKeys.DARK_MODE] = enabled }
}

val DataStore<Preferences>.darkModeFlow: Flow<Boolean> =
    data.map { it[SettingsKeys.DARK_MODE] ?: false }
```

---

## WRONG / RIGHT 4 — SharedPreferences migration without handler

```kotlin
// WRONG — dual writes, race on first launch
fun migrate(context: Context) {
    val sp = context.getSharedPreferences("legacy", MODE_PRIVATE)
    val dark = sp.getBoolean("dark", false)
    context.dataStore.edit { it[SettingsKeys.DARK_MODE] = dark }
}

// RIGHT — produceMigrations on DataStore builder
private val Context.dataStore by preferencesDataStore(
    name = "settings",
    produceMigrations = { context ->
        listOf(
            object : DataMigration<Preferences> {
                override suspend fun cleanUp() {
                    context.deleteSharedPreferences("legacy")
                }
                override suspend fun shouldMigrate(currentData: Preferences): Boolean =
                    !currentData.contains(SettingsKeys.DARK_MODE)

                override suspend fun migrate(currentData: Preferences): Preferences {
                    val legacy = context.getSharedPreferences("legacy", MODE_PRIVATE)
                    return currentData.toMutablePreferences().apply {
                        this[SettingsKeys.DARK_MODE] = legacy.getBoolean("dark", false)
                    }
                }
            }
        )
    }
)
```

---

## WRONG / RIGHT 5 — Storing secrets in plain Preferences DataStore

```kotlin
// WRONG — token in unencrypted Preferences DataStore
dataStore.edit { it[stringPreferencesKey("auth_token")] = token }

// RIGHT — EncryptedSharedPreferences for legacy OR encrypt value before Proto store
// For tokens prefer EncryptedSharedPreferences migration path or Android Keystore + Proto

val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
// Migrate to DataStore only after encrypting at rest or use hardware-backed keys
```

---

## Decision matrix

| Need | Choice |
|---|---|
| Boolean / String / Int settings | Preferences DataStore |
| Structured config with schema | Proto DataStore |
| Legacy SharedPreferences | `produceMigrations` + delete SP after |
| Auth tokens | Keystore + EncryptedSharedPreferences or encrypted Proto |
| Read in UI | `Flow` → `stateIn` in VM → `collectAsStateWithLifecycle` |

## Anti-patterns summary

- Never `commit()` or `apply()` in new code — migrate to DataStore.
- Never read DataStore synchronously in `@Composable` — always Flow.
- Never duplicate writes to both SP and DataStore after migration completes.
