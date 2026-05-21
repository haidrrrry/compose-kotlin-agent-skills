# AnimatedClockJetpacl — Example Patterns

Source: https://github.com/haidrrrry/AnimatedClockJetpacl

Winter-themed analog clock built with Compose Multiplatform. Demonstrates:

## Key Patterns Used

### 1. Canvas Custom Drawing (`AnimatedClockApp.kt`)
- `DrawScope.drawWinterClockFace()` — full analog clock face with hour markers, hands, center dot
- `rotate(degrees, pivot)` for clock hands — no manual sin/cos per hand
- `Brush.linearGradient` for ice-textured hands
- `Brush.radialGradient` for layered background

### 2. Infinite Transitions
- `rememberInfiniteTransition` for ice glow pulse (3s reverse loop)
- Crystal rotation (60s continuous spin)
- Snowflake particle progress (20s restart loop)

### 3. Particle System
- `Snowflake` data class with randomized initial state
- 150 particles rendered in single `Canvas`
- Sine-wave horizontal drift: `x + sin(y * 0.01 + phase) * amplitude`
- Modulo wrapping for infinite vertical loop

### 4. Spring Animations
- `DampingRatioMediumBouncy` + `StiffnessLow` on seconds counter
- `graphicsLayer(scaleX, scaleY)` for scale animation
- `DampingRatioLowBouncy` for ice glow intensity

### 5. CMP Structure
- `commonMain` — all UI code (`AnimatedClockApp.kt`)
- `androidMain` — `MainActivity` with `setContent { App() }`
- `iosMain` — `MainViewController` via `ComposeUIViewController`
- Single `App.kt` entry point shared across platforms

### 6. Time Handling
- `TimeData` data class with hour/minute/second
- `LaunchedEffect(Unit)` with `while(true) { delay(1000) }` for clock tick
- Platform `expect/actual` for `getCurrentTime()` if needed

## File Map

| File | Demonstrates |
|------|-------------|
| `AnimatedClockApp.kt` | Canvas drawing, animations, particle system, spring physics |
| `App.kt` | CMP entry point |
| `Platform.kt` | expect/actual platform abstraction |
