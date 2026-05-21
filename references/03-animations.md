# Animations — Springs, Canvas, Gestures, Shared Elements

## Contents

- Animation decision tree
- AnimatedVisibility, AnimatedContent, Crossfade
- animate*AsState — float, dp, color
- Spring physics — dampingRatio, stiffness tuning
- rememberInfiniteTransition — shimmer, pulse, breathing
- Canvas-based custom animations
- Gesture-driven animations
- Shared element transitions (Navigation 3)

## Animation Decision Tree

```
Need to show/hide content?
  → AnimatedVisibility (enter/exit transitions)

Need to swap between states?
  → AnimatedContent (with transitionSpec)
  → Crossfade (simple fade between states)

Need to animate a single value?
  → animate*AsState (fire-and-forget)
  → Animatable (coroutine-driven, full control)

Need continuous animation?
  → rememberInfiniteTransition (loop forever)

Need gesture-driven?
  → Animatable + pointerInput (drag, fling, snap)

Need Canvas-level custom?
  → DrawScope + rotate/translate + animated values
```

## AnimatedVisibility

```kotlin
var isVisible by remember { mutableStateOf(false) }

AnimatedVisibility(
    visible = isVisible,
    enter = fadeIn(animationSpec = tween(300)) +
            slideInVertically(initialOffsetY = { -it / 2 }),
    exit = fadeOut(animationSpec = tween(200)) +
           slideOutVertically(targetOffsetY = { -it / 2 })
) {
    AccountCard(account)
}
```

**Gotcha:** `AnimatedVisibility` keeps content in composition during exit animation. Don't null-check inside.

## AnimatedContent

```kotlin
AnimatedContent(
    targetState = selectedTab,
    transitionSpec = {
        // Slide in from right + fade in, slide out to left + fade out
        (slideInHorizontally { it } + fadeIn()) togetherWith
            (slideOutHorizontally { -it } + fadeOut()) using
            SizeTransform(clip = false)
    },
    label = "tab_content"
) { tab ->
    when (tab) {
        Tab.Home -> HomeScreen()
        Tab.Settings -> SettingsScreen()
    }
}
```

## animate*AsState — Fire and Forget

```kotlin
// Float — alpha, scale, rotation
val alpha by animateFloatAsState(
    targetValue = if (isSelected) 1f else 0.5f,
    animationSpec = tween(300),
    label = "alpha"
)

// Dp — size, offset, padding
val elevation by animateDpAsState(
    targetValue = if (isPressed) 2.dp else 8.dp,
    animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy),
    label = "elevation"
)

// Color — smooth theme transitions
val backgroundColor by animateColorAsState(
    targetValue = if (isDark) Color(0xFF1E293B) else Color(0xFFFFFFFF),
    animationSpec = tween(500),
    label = "bg_color"
)
```

**Always provide `label`** — shows in Layout Inspector animation preview.

## Spring Physics

Springs feel natural because they don't have fixed duration. They respond to velocity.

### Tuning Guide

| dampingRatio | Behavior | Use for |
|-------------|----------|---------|
| `DampingRatioHighBouncy` (0.2) | Very bouncy, multiple oscillations | Playful UI, game-like |
| `DampingRatioMediumBouncy` (0.5) | Moderate bounce, 1-2 overshoots | Buttons, cards, toggles |
| `DampingRatioLowBouncy` (0.75) | Slight bounce, settles fast | Subtle feedback |
| `DampingRatioNoBouncy` (1.0) | No bounce, smooth settle | Professional, subtle |

| stiffness | Behavior | Use for |
|-----------|----------|---------|
| `StiffnessHigh` (10000) | Snappy, fast | Button press, quick feedback |
| `StiffnessMedium` (1500) | Balanced | General transitions |
| `StiffnessMediumLow` (400) | Relaxed | Page transitions, large elements |
| `StiffnessLow` (200) | Slow, gentle | Ambient animations |
| `StiffnessVeryLow` (1) | Very slow | Background effects |

From AnimatedClock — bouncy seconds unit:

```kotlin
val scale by animateFloatAsState(
    targetValue = if (value == 0) 1.3f else 1f,
    animationSpec = spring(
        dampingRatio = Spring.DampingRatioMediumBouncy,
        stiffness = Spring.StiffnessLow
    ),
    label = "scale"
)

Column(modifier = Modifier.graphicsLayer(scaleX = scale, scaleY = scale)) {
    Text(text = formatted, fontSize = 32.sp, fontWeight = FontWeight.Bold)
}
```

**Gotcha:** `stiffness = 0f` crashes. Minimum is `Spring.StiffnessVeryLow` (1f).

## rememberInfiniteTransition

For animations that loop forever — shimmer, pulse, breathing, rotation.

From AnimatedClock — ice glow pulse:

```kotlin
val infiniteTransition = rememberInfiniteTransition(label = "effects")

val glowAlpha by infiniteTransition.animateFloat(
    initialValue = 0.4f,
    targetValue = 0.9f,
    animationSpec = infiniteRepeatable(
        animation = tween(3000, easing = FastOutSlowInEasing),
        repeatMode = RepeatMode.Reverse  // ping-pong
    ),
    label = "glow"
)

val rotation by infiniteTransition.animateFloat(
    initialValue = 0f,
    targetValue = 360f,
    animationSpec = infiniteRepeatable(
        animation = tween(60_000, easing = LinearEasing),
        repeatMode = RepeatMode.Restart  // continuous spin
    ),
    label = "rotation"
)
```

### Shimmer Effect

```kotlin
@Composable
fun ShimmerBox(modifier: Modifier = Modifier) {
    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateX by transition.animateFloat(
        initialValue = -300f,
        targetValue = 300f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer_x"
    )
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color.LightGray.copy(alpha = 0.3f),
                        Color.LightGray.copy(alpha = 0.7f),
                        Color.LightGray.copy(alpha = 0.3f)
                    ),
                    start = Offset(translateX, 0f),
                    end = Offset(translateX + 200f, 0f)
                )
            )
    )
}
```

## Canvas-Based Custom Animations

From AnimatedClock — full analog clock with animated hands:

### Snowflake Particle System

```kotlin
data class Snowflake(
    val startX: Float,
    val startY: Float,
    val size: Float,
    val alpha: Float,
    val amplitude: Float,
    val phase: Float
)

@Composable
fun SnowfallBackground() {
    val snowflakes = remember { List(150) {
        Snowflake(
            startX = Random.nextFloat() * 1000f,
            startY = -Random.nextFloat() * 200f,
            size = Random.nextFloat() * 3f + 1f,
            alpha = Random.nextFloat() * 0.6f + 0.2f,
            amplitude = Random.nextFloat() * 30f + 10f,
            phase = Random.nextFloat() * 2f * PI.toFloat()
        )
    }}

    val infiniteTransition = rememberInfiniteTransition(label = "snowfall")
    val progress by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(20_000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "snow_progress"
    )

    Canvas(modifier = Modifier.fillMaxSize()) {
        snowflakes.forEach { flake ->
            val y = (flake.startY + (size.height + 100) * progress) % (size.height + 200)
            val x = flake.startX + sin(y * 0.01f + flake.phase) * flake.amplitude
            drawCircle(
                color = Color.White.copy(alpha = flake.alpha),
                radius = flake.size,
                center = Offset(x, y)
            )
        }
    }
}
```

**Pattern:** data class for particle state + `remember` for initial state + infinite transition for progress + Canvas for rendering.

### Clock Hands with rotate()

```kotlin
fun DrawScope.drawClockHands(hour: Int, minute: Int, second: Int) {
    val center = size.center
    val radius = size.minDimension / 2 * 0.85f

    val hourAngle = (hour % 12) * 30f + minute * 0.5f
    val minuteAngle = minute * 6f + second * 0.1f
    val secondAngle = second * 6f

    // Hour hand — rotate() handles all trig
    rotate(hourAngle, center) {
        drawLine(
            brush = Brush.linearGradient(
                listOf(Color(0xFF87CEEB), Color.White, Color(0xFF4169E1))
            ),
            start = center,
            end = Offset(center.x, center.y - radius * 0.5f),
            strokeWidth = 12f,
            cap = StrokeCap.Round
        )
    }

    // Minute hand
    rotate(minuteAngle, center) {
        drawLine(
            brush = Brush.linearGradient(
                listOf(Color(0xFF4169E1), Color.White, Color(0xFF87CEEB))
            ),
            start = center,
            end = Offset(center.x, center.y - radius * 0.7f),
            strokeWidth = 8f,
            cap = StrokeCap.Round
        )
    }

    // Second hand with counterweight
    rotate(secondAngle, center) {
        drawLine(
            color = Color(0xFFFF4444),
            start = center,
            end = Offset(center.x, center.y - radius * 0.8f),
            strokeWidth = 3f,
            cap = StrokeCap.Round
        )
        drawLine(
            color = Color(0xFFFF4444),
            start = center,
            end = Offset(center.x, center.y + radius * 0.2f),
            strokeWidth = 6f,
            cap = StrokeCap.Round
        )
    }
}
```

**Key insight:** `rotate(degrees, pivot)` in `DrawScope` handles all trigonometry. Draw the hand pointing up, rotate to the correct angle. Never manually calculate sin/cos for each hand.

## Gesture-Driven Animations

### Drag to Dismiss

```kotlin
@Composable
fun SwipeToDismiss(onDismiss: () -> Unit, content: @Composable () -> Unit) {
    val offsetX = remember { Animatable(0f) }
    val scope = rememberCoroutineScope()

    Box(
        modifier = Modifier
            .offset { IntOffset(offsetX.value.roundToInt(), 0) }
            .pointerInput(Unit) {
                detectHorizontalDragGestures(
                    onDragEnd = {
                        scope.launch {
                            if (abs(offsetX.value) > size.width / 3) {
                                offsetX.animateTo(
                                    targetValue = if (offsetX.value > 0) size.width.toFloat()
                                        else -size.width.toFloat(),
                                    animationSpec = tween(200)
                                )
                                onDismiss()
                            } else {
                                offsetX.animateTo(
                                    targetValue = 0f,
                                    animationSpec = spring(
                                        dampingRatio = Spring.DampingRatioMediumBouncy
                                    )
                                )
                            }
                        }
                    },
                    onHorizontalDrag = { _, dragAmount ->
                        scope.launch { offsetX.snapTo(offsetX.value + dragAmount) }
                    }
                )
            }
    ) {
        content()
    }
}
```

### Press Scale Effect

```kotlin
fun Modifier.pressEffect(targetScale: Float = 0.95f): Modifier = composed {
    var isPressed by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (isPressed) targetScale else 1f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessHigh
        ),
        label = "press_scale"
    )
    this
        .graphicsLayer(scaleX = scale, scaleY = scale)
        .pointerInput(Unit) {
            detectTapGestures(
                onPress = {
                    isPressed = true
                    tryAwaitRelease()
                    isPressed = false
                }
            )
        }
}
```

## Shared Element Transitions (Navigation 3)

```kotlin
// Nav 3 shared element — experimental as of 2025
NavHost(navController = navController, startDestination = "list") {
    composable("list") {
        LazyColumn {
            items(accounts, key = { it.id }) { account ->
                SharedTransitionLayout {
                    AccountCard(
                        account = account,
                        modifier = Modifier.sharedElement(
                            state = rememberSharedContentState(key = "account-${account.id}"),
                            animatedVisibilityScope = this@composable
                        )
                    )
                }
            }
        }
    }
    composable("detail/{id}") { backStackEntry ->
        SharedTransitionLayout {
            AccountDetail(
                modifier = Modifier.sharedElement(
                    state = rememberSharedContentState(
                        key = "account-${backStackEntry.arguments?.getString("id")}"
                    ),
                    animatedVisibilityScope = this@composable
                )
            )
        }
    }
}
```

**Gotcha:** shared element keys must match exactly between source and destination. Use the same key generation logic.

## Anti-Patterns

- **`tween(0)` to skip animation** → use `snap()` spec instead, or don't animate at all
- **Animating in `LaunchedEffect` with `delay`** → use animation APIs. Manual delay = janky, can't be interrupted
- **`animate*AsState` for gesture tracking** → use `Animatable` — it supports `snapTo()` and velocity-aware `animateTo()`
- **Missing `label` on animations** → Layout Inspector can't identify them. Always add labels
- **`rememberInfiniteTransition` for one-shot** → infinite = forever. Use `Animatable.animateTo()` for one-shot
