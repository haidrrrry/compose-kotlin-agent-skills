---
name: paging3
description: >
  Paging 3 with Compose — PagingSource, RemoteMediator, LazyPagingItems, LoadState UI,
  2026 asState() presenter pattern, append/prepend triggers. Use when building paginated lists.
version: "2.2.0"
updated: "2026-05-21"
---

# Paging 3 — Compose, RemoteMediator, 2026 Presenter APIs

## Pinned versions (2026)

```toml
paging = "3.3.6"
```

```kotlin
implementation("androidx.paging:paging-runtime:3.3.6")
implementation("androidx.paging:paging-compose:3.3.6")
```

---

## WRONG / RIGHT 1 — PagingSource blocking network on main

```kotlin
// WRONG — blocking call inside load()
class BadPagingSource(private val api: Api) : PagingSource<Int, Item>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Item> {
        val page = params.key ?: 0
        val response = api.fetchSync(page)  // blocking retrofit call
        return LoadResult.Page(response.items, prevKey = page - 1, nextKey = page + 1)
    }
    override fun getRefreshKey(state: PagingState<Int, Item>): Int? =
        state.anchorPosition?.let { state.closestPageToPosition(it)?.prevKey?.plus(1) }
}

// RIGHT — suspend API, map errors to LoadResult.Error
class ItemPagingSource(
    private val api: Api,
    private val query: String
) : PagingSource<Int, ItemDto>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, ItemDto> = try {
        val page = params.key ?: 0
        val response = api.search(query, page, params.loadSize)
        LoadResult.Page(
            data = response.items,
            prevKey = if (page == 0) null else page - 1,
            nextKey = if (response.items.isEmpty()) null else page + 1
        )
    } catch (e: Exception) {
        LoadResult.Error(e)
    }

    override fun getRefreshKey(state: PagingState<Int, ItemDto>): Int? =
        state.anchorPosition?.let { anchor ->
            state.closestPageToPosition(anchor)?.let { page ->
                page.prevKey?.plus(1) ?: page.nextKey?.minus(1)
            }
        }
}
```

---

## WRONG / RIGHT 2 — collectAsLazyPagingItems() in ViewModel (deprecated pattern)

```kotlin
// WRONG — Compose collector belongs in UI layer, not ViewModel
@HiltViewModel
class BadListViewModel @Inject constructor(repo: ItemRepository) : ViewModel() {
    val lazyItems = repo.pager.flow.collectAsLazyPagingItems()  // Compose API in VM
}

// RIGHT (2026) — expose PagingData Flow; presenter collects as State in UI
@HiltViewModel
class ItemListViewModel @Inject constructor(
    private val repository: ItemRepository
) : ViewModel() {
    private val _query = MutableStateFlow("")
    val query: StateFlow<String> = _query.asStateFlow()

    val pagingFlow: Flow<PagingData<ItemUi>> = _query
        .flatMapLatest { repository.pagerFor(it).flow }
        .map { pagingData -> pagingData.map { dto -> dto.toUi() } }
        .cachedIn(viewModelScope)

    fun onQueryChanged(value: String) {
        _query.update { value }
    }
}
```

---

## WRONG / RIGHT 3 — 2026 presenter: pager.flow.asState() + collectAsStateWithLifecycle

```kotlin
// WRONG — old collectAsLazyPagingItems only in Composable without initial snapshot
@Composable
fun ItemListScreen(vm: ItemListViewModel = hiltViewModel()) {
    val lazyItems = vm.pagingFlow.collectAsLazyPagingItems()
    // no placeholder during first load — flicker
}

// RIGHT (2026) — asState() in presenter layer with initialList for stable first frame
@Composable
fun ItemListScreen(vm: ItemListViewModel = hiltViewModel()) {
    val pagingState by vm.pagingFlow
        .asState(initialList = emptyList())  // paging-compose 2026 extension
        .collectAsStateWithLifecycle()

    ItemListContent(
        items = pagingState.items,
        loadState = pagingState.loadState,
        onRetry = { vm.retry() }
    )
}
```

> **Note:** `Flow<PagingData<T>>.asState(initialList)` caches the latest `LazyPagingItems`-equivalent snapshot for lifecycle-aware collection. Check `androidx.paging:paging-compose` release notes for your BOM pin.

---

## WRONG / RIGHT 4 — Ignoring LoadState in Compose UI

```kotlin
// WRONG — crash on empty/error; no retry
@Composable
fun ItemList(lazyItems: LazyPagingItems<ItemUi>) {
    LazyColumn {
        items(lazyItems.itemCount) { index ->
            Text(lazyItems[index]!!.title)
        }
    }
}

// RIGHT — handle refresh/append LoadState + placeholders
@Composable
fun ItemListContent(
    items: List<ItemUi?>,
    loadState: CombinedLoadStates,
    onRetry: () -> Unit
) {
    LazyColumn {
        if (loadState.refresh is LoadState.Loading && items.isEmpty()) {
            item(key = "loading") { CircularProgressIndicator(Modifier.fillMaxWidth()) }
        }
        items(
            count = items.size,
            key = { index -> items[index]?.id ?: "placeholder-$index" },
            contentType = { "item" }
        ) { index ->
            val item = items[index]
            if (item != null) {
                ItemRow(item)
            } else {
                ItemPlaceholder()
            }
        }
        if (loadState.append is LoadState.Loading) {
            item(key = "append_loading") { LinearProgressIndicator(Modifier.fillMaxWidth()) }
        }
        if (loadState.refresh is LoadState.Error) {
            item(key = "error") {
                ErrorRow(message = stringResource(R.string.error_load), onRetry = onRetry)
            }
        }
    }
}
```

---

## WRONG / RIGHT 5 — Manual append/prepend triggers (2026 Pager API)

```kotlin
// WRONG — hack refresh by recreating entire Pager on every scroll edge
fun loadMore() {
    pager = Pager(config) { ItemPagingSource(api, query) }  // new instance, lost scroll
}

// RIGHT — Pager.append / Pager.prepend for explicit load triggers
@HiltViewModel
class ItemListViewModel @Inject constructor(
    private val repository: ItemRepository
) : ViewModel() {
    private var pager: Pager<Int, ItemDto>? = null

    fun bindPager(query: String): Flow<PagingData<ItemUi>> {
        val p = repository.buildPager(query).also { pager = it }
        return p.flow.map { data -> data.map { it.toUi() } }.cachedIn(viewModelScope)
    }

    fun appendNextPage() {
        viewModelScope.launch {
            pager?.append()  // paging-runtime 2026 — triggers append LoadType
        }
    }

    fun prependPreviousPage() {
        viewModelScope.launch {
            pager?.prepend()
        }
    }
}
```

---

## RemoteMediator — offline-first

```kotlin
@OptIn(ExperimentalPagingApi::class)
class ItemRemoteMediator(
    private val db: AppDatabase,
    private val api: Api
) : RemoteMediator<Int, ItemEntity>() {
    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, ItemEntity>
    ): MediatorResult {
        return try {
            val page = when (loadType) {
                LoadType.REFRESH -> 0
                LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)
                LoadType.APPEND -> {
                    val last = db.itemDao().lastRemoteKey()
                        ?: return MediatorResult.Success(endOfPaginationReached = true)
                    last + 1
                }
            }
            val response = api.fetch(page)
            db.withTransaction {
                if (loadType == LoadType.REFRESH) {
                    db.itemDao().clearAll()
                }
                db.itemDao().insertAll(response.items.map { it.toEntity() })
            }
            MediatorResult.Success(endOfPaginationReached = response.items.isEmpty())
        } catch (e: Exception) {
            MediatorResult.Error(e)
        }
    }
}
```

## Decision matrix

| Scenario | Pattern |
|---|---|
| Network-only list | `PagingSource` |
| Room + network sync | `RemoteMediator` + Room DAO `PagingSource` |
| Search query changes | `flatMapLatest` on query → new `Pager` |
| UI collection | `asState(initialList)` + `collectAsStateWithLifecycle` |
| User taps "Load more" | `pager.append()` |
| Pull-to-refresh | `LazyPagingItems.refresh()` or new refresh trigger |
