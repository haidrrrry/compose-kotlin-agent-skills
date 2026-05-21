# Networking — Ktor, Auth Flows, DTO Mappers, Offline-First

## Contents

- Ktor client setup
- Auth flows — JWT, token refresh, interceptors
- DTO → domain mapper pattern
- Offline-first — local cache + remote sync
- Error handling — network → domain errors

## Ktor Client Setup

```kotlin
fun createHttpClient(tokenProvider: TokenProvider): HttpClient {
    return HttpClient {
        // JSON serialization
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true    // API adds fields, don't crash
                isLenient = true            // tolerate minor JSON issues
                encodeDefaults = false      // skip null/default in requests
            })
        }

        // Logging (debug only)
        install(Logging) {
            level = LogLevel.HEADERS  // BODY for full debug, HEADERS for prod
        }

        // Timeout
        install(HttpTimeout) {
            requestTimeoutMillis = 30_000
            connectTimeoutMillis = 10_000
        }

        // Default request config
        defaultRequest {
            url("https://api.example.com/v1/")
            contentType(ContentType.Application.Json)
        }
    }
}
```

```toml
[dependencies]
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-okhttp = { module = "io.ktor:ktor-client-okhttp", version.ref = "ktor" }
ktor-client-darwin = { module = "io.ktor:ktor-client-darwin", version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation", version.ref = "ktor" }
ktor-serialization-kotlinx-json = { module = "io.ktor:ktor-serialization-kotlinx-json", version.ref = "ktor" }
ktor-client-logging = { module = "io.ktor:ktor-client-logging", version.ref = "ktor" }
```

## Auth — JWT Token Refresh

```kotlin
class AuthInterceptor(
    private val tokenStore: TokenStore,
    private val authApi: AuthApi
) {
    fun install(config: HttpClientConfig<*>) {
        config.install(HttpSend) {
            intercept { request ->
                // Attach token
                val token = tokenStore.getAccessToken()
                if (token != null) {
                    request.headers.append("Authorization", "Bearer $token")
                }

                val response = execute(request)

                // If 401, refresh token and retry once
                if (response.response.status == HttpStatusCode.Unauthorized) {
                    val refreshed = refreshToken()
                    if (refreshed) {
                        request.headers.remove("Authorization")
                        request.headers.append(
                            "Authorization",
                            "Bearer ${tokenStore.getAccessToken()}"
                        )
                        execute(request)
                    } else {
                        response  // refresh failed, return 401
                    }
                } else {
                    response
                }
            }
        }
    }

    private suspend fun refreshToken(): Boolean {
        return try {
            val refreshToken = tokenStore.getRefreshToken() ?: return false
            val response = authApi.refreshToken(refreshToken)
            tokenStore.saveTokens(response.accessToken, response.refreshToken)
            true
        } catch (e: Exception) {
            tokenStore.clearTokens()
            false
        }
    }
}
```

### Token Storage

```kotlin
class TokenStore(private val dataStore: DataStore<Preferences>) {
    private val ACCESS_TOKEN = stringPreferencesKey("access_token")
    private val REFRESH_TOKEN = stringPreferencesKey("refresh_token")

    suspend fun getAccessToken(): String? =
        dataStore.data.first()[ACCESS_TOKEN]

    suspend fun saveTokens(access: String, refresh: String) {
        dataStore.edit { prefs ->
            prefs[ACCESS_TOKEN] = access
            prefs[REFRESH_TOKEN] = refresh
        }
    }

    suspend fun clearTokens() {
        dataStore.edit { it.clear() }
    }
}
```

## DTO → Domain Mapper Pattern

```kotlin
// Network DTO — matches API JSON shape
@Serializable
data class AccountDto(
    val id: String,
    @SerialName("service_name") val serviceName: String,
    @SerialName("account_name") val accountName: String,
    @SerialName("secret_key") val secretKey: String,
    @SerialName("icon_url") val iconUrl: String?,
    @SerialName("created_at") val createdAt: String  // ISO 8601
)

// Domain model — what the app actually uses
data class AuthAccount(
    val id: String,
    val serviceName: String,
    val accountName: String,
    val secretKey: String,
    val iconUrl: String?,
    val createdAt: LocalDateTime
)

// Mapper
fun AccountDto.toDomain() = AuthAccount(
    id = id,
    serviceName = serviceName,
    accountName = accountName,
    secretKey = secretKey,
    iconUrl = iconUrl,
    createdAt = LocalDateTime.parse(createdAt)
)

fun AuthAccount.toDto() = AccountDto(
    id = id,
    serviceName = serviceName,
    accountName = accountName,
    secretKey = secretKey,
    iconUrl = iconUrl,
    createdAt = createdAt.toString()
)
```

**Why separate DTO from domain:**
1. API shape changes don't cascade through your app
2. `@SerialName` annotations don't pollute domain
3. Date parsing happens once in mapper, not throughout codebase
4. Null handling and defaults isolated in mapper

## API Service Layer

```kotlin
class AuthApiService(private val client: HttpClient) {

    suspend fun getAccounts(): List<AccountDto> {
        return client.get("accounts").body()
    }

    suspend fun getAccountById(id: String): AccountDto {
        return client.get("accounts/$id").body()
    }

    suspend fun createAccount(request: CreateAccountRequest): AccountDto {
        return client.post("accounts") {
            setBody(request)
        }.body()
    }

    suspend fun deleteAccount(id: String) {
        client.delete("accounts/$id")
    }

    suspend fun refreshToken(refreshToken: String): TokenResponse {
        return client.post("auth/refresh") {
            setBody(RefreshRequest(refreshToken))
        }.body()
    }
}
```

## Offline-First Pattern

```kotlin
class AuthRepositoryImpl(
    private val dao: AuthAccountDao,
    private val api: AuthApiService
) : AuthRepository {

    // UI always reads from local DB
    override fun getAllAccounts(): Flow<List<AuthAccount>> =
        dao.getAllAccounts().map { entities -> entities.map { it.toDomain() } }

    // Sync: remote → local, UI auto-updates via Flow
    override suspend fun sync(): Result<Unit> {
        return safeApiCall {
            val remoteDtos = api.getAccounts()
            val entities = remoteDtos.map { it.toDomain().toEntity() }
            dao.replaceAllAccounts(entities)
        }
    }

    // Write: local first, then remote
    override suspend fun addAccount(account: AuthAccount): Result<Unit> {
        // Always write locally first — instant UI update
        dao.insertAccount(account.toEntity())

        // Then sync to remote
        return safeApiCall {
            api.createAccount(account.toCreateRequest())
        }
    }
}
```

### Sync Strategy

```kotlin
class SyncManager(
    private val repository: AuthRepository,
    private val connectivityMonitor: ConnectivityMonitor
) {
    // Sync on app start
    suspend fun syncOnStart() {
        if (connectivityMonitor.isOnline()) {
            repository.sync()
        }
    }

    // Observe connectivity and sync when back online
    fun observeConnectivity(): Flow<Boolean> =
        connectivityMonitor.isOnlineFlow
            .distinctUntilChanged()
            .filter { it }  // only when transitioning to online
            .onEach { repository.sync() }
}
```

## Error Handling — Network to Domain

```kotlin
sealed interface NetworkError {
    data class Http(val code: Int, val message: String) : NetworkError
    data object NoConnection : NetworkError
    data object Timeout : NetworkError
    data class Unknown(val cause: Throwable) : NetworkError
}

suspend fun <T> safeApiCall(block: suspend () -> T): Result<T> {
    return try {
        Result.success(block())
    } catch (e: CancellationException) {
        throw e  // never swallow cancellation
    } catch (e: ClientRequestException) {  // 4xx
        Result.failure(NetworkError.Http(e.response.status.value, e.message))
    } catch (e: ServerResponseException) {  // 5xx
        Result.failure(NetworkError.Http(e.response.status.value, e.message))
    } catch (e: HttpRequestTimeoutException) {
        Result.failure(NetworkError.Timeout)
    } catch (e: IOException) {
        Result.failure(NetworkError.NoConnection)
    } catch (e: Throwable) {
        Result.failure(NetworkError.Unknown(e))
    }
}
```

### Map to UI-Friendly Message

```kotlin
fun NetworkError.toUserMessage(): String = when (this) {
    is NetworkError.Http -> when (code) {
        401 -> "Session expired. Please sign in again."
        403 -> "You don't have permission for this action."
        404 -> "Not found."
        429 -> "Too many requests. Please wait a moment."
        in 500..599 -> "Server error. Please try again later."
        else -> "Something went wrong (Error $code)."
    }
    NetworkError.NoConnection -> "No internet connection."
    NetworkError.Timeout -> "Request timed out. Check your connection."
    is NetworkError.Unknown -> "Unexpected error occurred."
}
```

## Anti-Patterns

- **Catching `Exception` instead of specific types** → catches `CancellationException`, breaks coroutines
- **Parsing JSON in composable** → CPU-heavy. Parse in repository/ViewModel on background dispatcher
- **Hardcoded base URL** → use BuildConfig or dependency injection for different environments
- **No timeout** → default Ktor has no timeout. Set explicit `HttpTimeout`
- **Logging `LogLevel.BODY` in production** → leaks sensitive data to logcat. Use `HEADERS` or `INFO`
- **Token in URL query param** → visible in logs, server access logs, browser history. Always use Authorization header
