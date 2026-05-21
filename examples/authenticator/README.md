# Authenticator — Example Patterns

Source: https://github.com/haidrrrry/Authenticator

Cross-platform 2FA TOTP app built with Compose Multiplatform. Demonstrates:

## Key Patterns Used

### 1. MVVM with Repository (`repository/AuthViewModel.kt`)
- `MutableStateFlow` for search query state
- `combine()` to merge Room Flow + search query → filtered results
- `viewModelScope.launch` for write operations
- ViewModel accepts `AuthRepository`, not DAO directly

### 2. Repository Pattern (`repository/AuthRepository.kt`)
- Thin wrapper over Room DAO
- Returns `Flow<List<T>>` for reactive queries
- `suspend` functions for writes
- Abstracts data source for testing

### 3. Room with KMP (`dao/`)
- `@Dao` interface with `Flow` queries in `commonMain`
- `DatabaseFactory` as `expect/actual` per platform
- `@Entity` with `@PrimaryKey`, `@ColumnInfo`
- `OnConflictStrategy.REPLACE` for upsert

### 4. Custom Theme System (`utils/AppColors.kt`, `screens/ProvideAppTheme.kt`)
- `AppColors.Light` / `AppColors.Dark` — dual palette objects
- `AppTheme` data class with all custom tokens (timerGood/Warning/Critical)
- `LocalAppTheme` CompositionLocal for tree-wide access
- `ProvideAppTheme` reads `ThemeManager.themeMode` StateFlow
- Supports LIGHT / DARK / SYSTEM modes via `isSystemInDarkTheme()`

### 5. Koin DI (`di/`)
- `sharedModule` in `commonMain` — Repository + ViewModel
- `platformModule()` as `expect/actual` — DB factory per platform
- `initializeKoin()` called from platform entry points
- `koinViewModel()` in composables

### 6. CMP Structure
- `commonMain` — ALL UI, ViewModel, Repository, DAO interface, theme
- `androidMain` — `MainActivity`, `DatabaseFactory.android.kt`, `TOTPGenerator.android.kt`
- `iosMain` — `MainViewController`, `DatabaseFactory.ios.kt`, `TOTPGenerator.ios.kt`
- `desktopMain` — `main.kt`, desktop-specific implementations

### 7. expect/actual Examples
- `DatabaseFactory` — Room builder per platform
- `TOTPGenerator` — HMAC crypto per platform (javax.crypto vs CommonCrypto)
- `getCurrentTimeSeconds()` — System.currentTimeMillis vs NSDate
- `platformModule()` — Koin module per platform

## File Map

| File | Demonstrates |
|------|-------------|
| `repository/AuthViewModel.kt` | MVVM, combine(), StateFlow |
| `repository/AuthRepository.kt` | Repository pattern, Flow queries |
| `dao/AuthAccountDao.kt` | Room DAO, Flow + suspend |
| `classes/AuthAccount.kt` | Room Entity |
| `utils/AppColors.kt` | Dual-palette color tokens |
| `screens/ProvideAppTheme.kt` | CompositionLocal theme delivery |
| `classes/AppTheme.kt` | Custom theme data class |
| `di/initializeKoin.kt` | Koin setup |
| `utils/TOTPGenerator.kt` | expect/actual crypto |
