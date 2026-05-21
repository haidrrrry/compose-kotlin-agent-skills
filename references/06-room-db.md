# Room Database — Entities, DAOs, Migrations, Offline-First

## Contents

- Entity design — domain models vs entities
- DAO patterns — Flow, suspend, transactions
- TypeConverters
- Database migrations
- Offline-first architecture
- Repository pattern
- Anti-patterns

## Entity Design

### Separate Entity from Domain Model

```kotlin
// domain/ — pure, no Room annotations
data class AuthAccount(
    val id: String,
    val serviceName: String,
    val accountName: String,
    val secretKey: String,
    val iconEmoji: String
)

// data/ — Room entity
@Entity(tableName = "auth_accounts")
data class AuthAccountEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "service_name") val serviceName: String,
    @ColumnInfo(name = "account_name") val accountName: String,
    @ColumnInfo(name = "secret_key") val secretKey: String,
    @ColumnInfo(name = "icon_emoji") val iconEmoji: String
)

// Mappers
fun AuthAccountEntity.toDomain() = AuthAccount(
    id = id,
    serviceName = serviceName,
    accountName = accountName,
    secretKey = secretKey,
    iconEmoji = iconEmoji
)

fun AuthAccount.toEntity() = AuthAccountEntity(
    id = id,
    serviceName = serviceName,
    accountName = accountName,
    secretKey = secretKey,
    iconEmoji = iconEmoji
)
```

**When single model is OK:** small app, no network layer, entity IS the domain model. Split when Room annotations would leak into shared KMP modules or when DTO shapes differ.

### Composite Primary Keys

```kotlin
@Entity(
    tableName = "workout_records",
    primaryKeys = ["date", "workoutType"]
)
data class WorkoutRecordEntity(
    val date: String,           // "2026-05-21"
    val workoutType: String,    // "pushups"
    val repCount: Int,
    val durationMs: Long
)
```

### Indices for Query Performance

```kotlin
@Entity(
    tableName = "auth_accounts",
    indices = [
        Index(value = ["service_name"]),
        Index(value = ["account_name", "service_name"], unique = true)
    ]
)
data class AuthAccountEntity(/* ... */)
```

Add indices on columns used in `WHERE`, `ORDER BY`, and `JOIN`. Don't index everything — each index costs write performance.

## DAO Patterns

From Authenticator:

```kotlin
@Dao
interface AuthAccountDao {
    // Reactive query — returns Flow, auto-emits on data change
    @Query("SELECT * FROM auth_accounts ORDER BY serviceName ASC")
    fun getAllAccounts(): Flow<List<AuthAccountEntity>>

    // Search with LIKE — Flow for reactive search results
    @Query("""
        SELECT * FROM auth_accounts 
        WHERE service_name LIKE '%' || :query || '%' 
           OR account_name LIKE '%' || :query || '%'
    """)
    fun searchAccounts(query: String): Flow<List<AuthAccountEntity>>

    // Single item — suspend for one-shot
    @Query("SELECT * FROM auth_accounts WHERE id = :id")
    suspend fun getAccountById(id: String): AuthAccountEntity?

    // Count — suspend
    @Query("SELECT COUNT(*) FROM auth_accounts")
    suspend fun getAccountCount(): Int

    // Insert — REPLACE strategy for upsert
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAccount(account: AuthAccountEntity)

    // Batch insert
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAccounts(accounts: List<AuthAccountEntity>)

    // Update
    @Update
    suspend fun updateAccount(account: AuthAccountEntity)

    // Delete by object
    @Delete
    suspend fun deleteAccount(account: AuthAccountEntity)

    // Delete by ID — more practical from UI
    @Query("DELETE FROM auth_accounts WHERE id = :id")
    suspend fun deleteAccountById(id: String)

    // Delete all
    @Query("DELETE FROM auth_accounts")
    suspend fun deleteAllAccounts()
}
```

### DAO Rules

| Return Type | Use for | Thread |
|------------|---------|--------|
| `Flow<List<T>>` | Reactive queries (lists, search) | Background (auto) |
| `Flow<T?>` | Single item observation | Background (auto) |
| `suspend fun` | One-shot reads, all writes | Background (auto) |
| `fun` (no suspend, no Flow) | **WRONG** — blocks main thread | |

### Transactions

```kotlin
@Dao
interface AuthAccountDao {
    // Transaction for multi-statement operations
    @Transaction
    suspend fun replaceAllAccounts(newAccounts: List<AuthAccountEntity>) {
        deleteAllAccounts()
        insertAccounts(newAccounts)
    }

    // NOT needed for single operations
    // @Transaction  ← unnecessary on single @Insert
    @Insert
    suspend fun insertAccount(account: AuthAccountEntity)
}
```

**When to use `@Transaction`:**
- Multiple write operations that must succeed/fail together
- Read that involves multiple tables (relations)
- Batch operations where partial failure is unacceptable

**NOT needed for:** single `@Insert`, single `@Update`, single `@Delete`, single `@Query`.

## TypeConverters

```kotlin
class Converters {
    // Enum
    @TypeConverter
    fun fromWorkoutType(type: WorkoutType): String = type.name

    @TypeConverter
    fun toWorkoutType(value: String): WorkoutType = WorkoutType.valueOf(value)

    // Date (store as epoch millis)
    @TypeConverter
    fun fromDate(date: LocalDate): Long =
        date.atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli()

    @TypeConverter
    fun toDate(millis: Long): LocalDate =
        Instant.ofEpochMilli(millis).atZone(ZoneOffset.UTC).toLocalDate()

    // List<String> (store as JSON)
    @TypeConverter
    fun fromStringList(list: List<String>): String = Json.encodeToString(list)

    @TypeConverter
    fun toStringList(json: String): List<String> = Json.decodeFromString(json)

    // Color (store as Int argb)
    @TypeConverter
    fun fromColor(color: Color): Int = color.toArgb()

    @TypeConverter
    fun toColor(argb: Int): Color = Color(argb)
}

// Register in Database
@Database(entities = [AuthAccountEntity::class], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun authAccountDao(): AuthAccountDao
}
```

**Gotcha:** TypeConverter for `Color` stores as `Int`. Compose `Color` and Android `Color` both have `toArgb()`.

## Database Migrations

### Safe Migration Pattern

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // Add column with default value — safe for existing data
        db.execSQL("ALTER TABLE auth_accounts ADD COLUMN icon_emoji TEXT NOT NULL DEFAULT '🔐'")
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // Create new table for added feature
        db.execSQL("""
            CREATE TABLE IF NOT EXISTS workout_records (
                date TEXT NOT NULL,
                workout_type TEXT NOT NULL,
                rep_count INTEGER NOT NULL,
                duration_ms INTEGER NOT NULL,
                PRIMARY KEY(date, workout_type)
            )
        """)
    }
}

// Build with migrations
Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
    .build()
```

### Auto-Migration (Room 2.4+)

```kotlin
@Database(
    entities = [AuthAccountEntity::class],
    version = 3,
    autoMigrations = [
        AutoMigration(from = 1, to = 2),
        AutoMigration(from = 2, to = 3, spec = Migration2To3Spec::class)
    ]
)
abstract class AppDatabase : RoomDatabase()

@RenameColumn(tableName = "auth_accounts", fromColumnName = "name", toColumnName = "service_name")
class Migration2To3Spec : AutoMigrationSpec
```

Auto-migration handles simple cases (add column, rename). Manual migration for complex changes (data transformation, table restructure).

### Testing Migrations

```kotlin
@RunWith(AndroidJUnit4::class)
class MigrationTest {
    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migrate1To2() {
        // Create DB at version 1
        helper.createDatabase("test_db", 1).apply {
            execSQL("INSERT INTO auth_accounts (id, service_name) VALUES ('1', 'Google')")
            close()
        }

        // Migrate to version 2
        helper.runMigrationsAndValidate("test_db", 2, true, MIGRATION_1_2)

        // Verify data survived
        val db = helper.runMigrationsAndValidate("test_db", 2, true)
        val cursor = db.query("SELECT icon_emoji FROM auth_accounts WHERE id = '1'")
        cursor.moveToFirst()
        assertEquals("🔐", cursor.getString(0))
    }
}
```

## Offline-First Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Composable │────▶│  Repository  │────▶│   Room DAO   │
│   (collect)  │     │  (mediator)  │     │  (source of  │
│              │◀────│              │◀────│   truth)     │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Remote API  │
                     │  (sync only) │
                     └──────────────┘
```

```kotlin
class AuthRepositoryImpl(
    private val dao: AuthAccountDao,
    private val api: AuthApi
) : AuthRepository {

    // UI always reads from Room — single source of truth
    override fun getAllAccounts(): Flow<List<AuthAccount>> =
        dao.getAllAccounts().map { entities ->
            entities.map { it.toDomain() }
        }

    // Sync: fetch remote → write to Room → UI auto-updates via Flow
    override suspend fun sync(): Result<Unit> {
        return try {
            val remote = api.getAccounts()
            val entities = remote.map { it.toEntity() }
            dao.replaceAllAccounts(entities)
            Result.success(Unit)
        } catch (e: IOException) {
            Result.failure(e)  // offline — stale local data still shown
        }
    }

    override suspend fun addAccount(account: AuthAccount): Result<Unit> {
        return try {
            dao.insertAccount(account.toEntity())  // write locally first
            api.createAccount(account.toDto())      // sync to remote
            Result.success(Unit)
        } catch (e: IOException) {
            // Local write succeeded, remote failed
            // Queue for later sync or just keep local
            Result.success(Unit)
        }
    }
}
```

**Key principle:** UI reads from Room only. Network writes to Room. Room notifies UI via Flow. User always sees data, even offline.

## Repository Pattern

```kotlin
// domain/ — interface
interface AuthRepository {
    fun getAllAccounts(): Flow<List<AuthAccount>>
    fun searchAccounts(query: String): Flow<List<AuthAccount>>
    suspend fun getAccountById(id: String): AuthAccount?
    suspend fun insertAccount(account: AuthAccount)
    suspend fun deleteAccountById(id: String)
    suspend fun sync(): Result<Unit>
}

// data/ — implementation
class AuthRepositoryImpl(
    private val dao: AuthAccountDao,
    private val api: AuthApi  // optional, for sync
) : AuthRepository {

    override fun getAllAccounts(): Flow<List<AuthAccount>> =
        dao.getAllAccounts().map { list -> list.map { it.toDomain() } }

    override suspend fun insertAccount(account: AuthAccount) {
        dao.insertAccount(account.toEntity())
    }

    // ... other methods
}
```

**Repository value:**
1. Abstracts data source — ViewModel doesn't know about Room/Retrofit
2. Testable — swap with FakeRepository in tests
3. Mapping layer — entity/DTO → domain model conversion
4. Offline-first logic — sync coordination

## Anti-Patterns

- **`@Transaction` on single query** → overhead for nothing. Only for multi-statement operations
- **`OnConflictStrategy.REPLACE` with foreign keys** → REPLACE = DELETE + INSERT. Cascades foreign keys. Use IGNORE + manual UPDATE
- **Returning `LiveData` from DAO** → use `Flow`. LiveData is lifecycle-aware but inflexible for transformation. Flow supports `map`, `combine`, `filter`, `stateIn`
- **`allowMainThreadQueries()`** → jank. Room queries always on background thread via suspend/Flow
- **Storing JSON blobs in single column** → defeats purpose of relational DB. Normalize into proper tables with relations
- **No migration strategy** → `fallbackToDestructiveMigration()` deletes all user data. Users will uninstall your app. Always write migrations
- **Fat entities with UI state** → entity stores persistent data. `isExpanded`, `isSelected` are transient — keep in UiState, not Room
