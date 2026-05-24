---
name: coil-image
description: >
  Coil 3 image loading in Compose — AsyncImage, SubcomposeAsyncImage, cache config,
  network dependency, AsyncImagePainter StateFlow, LocalAsyncImageModelEqualityDelegate.
  Use when loading images in Jetpack Compose.
version: "2.2.0"
updated: "2026-05-21"
---

# Coil 3 — Compose Image Loading (2026)

## Pinned versions (2026) — both required

```kotlin
implementation("io.coil-kt.coil3:coil-compose:3.4.0")
implementation("io.coil-kt.coil3:coil-network-okhttp:3.4.0")  // REQUIRED separate artifact
```

`coil-network-okhttp` is **not** transitive — network images fail silently without it.

---

## WRONG / RIGHT 1 — Missing network dependency

```kotlin
// WRONG — only coil-compose; URLs never load
dependencies {
    implementation("io.coil-kt.coil3:coil-compose:3.4.0")
}

// RIGHT — explicit network engine
dependencies {
    implementation("io.coil-kt.coil3:coil-compose:3.4.0")
    implementation("io.coil-kt.coil3:coil-network-okhttp:3.4.0")
}
```

---

## WRONG / RIGHT 2 — AsyncImage without placeholder/error

```kotlin
// WRONG — layout jump + no error state
@Composable
fun Avatar(url: String) {
    AsyncImage(
        model = url,
        contentDescription = null,
        modifier = Modifier.size(48.dp)
    )
}

// RIGHT — SubcomposeAsyncImage for loading/error slots
@Composable
fun Avatar(url: String, modifier: Modifier = Modifier) {
    SubcomposeAsyncImage(
        model = url,
        contentDescription = stringResource(R.string.avatar_content_description),
        modifier = modifier
            .size(48.dp)
            .clip(CircleShape),
        loading = {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                strokeWidth = 2.dp
            )
        },
        error = {
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = null,
                modifier = Modifier.size(32.dp)
            )
        }
    )
}
```

---

## WRONG / RIGHT 3 — Reading AsyncImagePainter.state via .value (2026 breaking change)

```kotlin
// WRONG — .value is not observable; UI won't recompose on state change
@Composable
fun ImageWithOverlay(model: Any) {
    val painter = rememberAsyncImagePainter(model = model)
    val state = painter.state.value  // BANNED in Coil 3.4+
    if (state is AsyncImagePainter.State.Success) {
        Image(painter = painter, contentDescription = null)
    }
}

// RIGHT — observe StateFlow
@Composable
fun ImageWithOverlay(model: Any) {
    val painter = rememberAsyncImagePainter(model = model)
    val state by painter.state.collectAsState()
    when (state) {
        is AsyncImagePainter.State.Loading -> LoadingPlaceholder()
        is AsyncImagePainter.State.Success -> Image(
            painter = painter,
            contentDescription = stringResource(R.string.image_loaded)
        )
        is AsyncImagePainter.State.Error -> ErrorPlaceholder()
        AsyncImagePainter.State.Empty -> Unit
    }
}
```

---

## WRONG / RIGHT 4 — EqualityDelegate as AsyncImage parameter (removed in 3.x)

```kotlin
// WRONG — EqualityDelegate parameter removed from AsyncImage
AsyncImage(
    model = url,
    contentDescription = null,
    equalityDelegate = DefaultModelEqualityDelegate()  // compile error
)

// RIGHT — provide via CompositionLocal
@Composable
fun AppImageHost(content: @Composable () -> Unit) {
    CompositionLocalProvider(
        LocalAsyncImageModelEqualityDelegate provides DefaultModelEqualityDelegate()
    ) {
        content()
    }
}

@Composable
fun ProductImage(url: String) {
    AsyncImage(
        model = url,
        contentDescription = stringResource(R.string.product_image)
    )
}
```

---

## WRONG / RIGHT 5 — Default ImageLoader per screen (cache thrash)

```kotlin
// WRONG — new loader every composition
@Composable
fun Banner(url: String) {
    val loader = ImageLoader.Builder(LocalContext.current).build()
    AsyncImage(model = url, imageLoader = loader, contentDescription = null)
}

// RIGHT — singleton via Coil.setImageLoader or Hilt @Singleton
@Module
@InstallIn(SingletonComponent::class)
object CoilModule {
    @Provides
    @Singleton
    fun imageLoader(@ApplicationContext context: Context): ImageLoader =
        ImageLoader.Builder(context)
            .memoryCache {
                MemoryCache.Builder()
                    .maxSizePercent(context, 0.25)
                    .build()
            }
            .diskCache {
                DiskCache.Builder()
                    .directory(context.cacheDir.resolve("image_cache"))
                    .maxSizeBytes(50L * 1024 * 1024)
                    .build()
            }
            .build()
}

@Composable
fun Banner(url: String, loader: ImageLoader = LocalContext.current.imageLoader) {
    AsyncImage(
        model = url,
        imageLoader = loader,
        contentDescription = stringResource(R.string.banner_image)
    )
}
```

---

## AsyncImage vs SubcomposeAsyncImage

| | AsyncImage | SubcomposeAsyncImage |
|---|---|---|
| API | Simple one-liner | Slot-based loading/error |
| Use when | Icons, known-size assets | Hero images, need skeleton UI |
| Recomposition | Crossfade built-in | Full control per state |

## Checklist

- [ ] `coil-network-okhttp:3.4.0` on classpath
- [ ] `contentDescription` set (or explicitly decorative)
- [ ] `painter.state.collectAsState()` not `.value`
- [ ] `LocalAsyncImageModelEqualityDelegate` for custom equality
- [ ] Singleton `ImageLoader` with memory + disk cache limits
