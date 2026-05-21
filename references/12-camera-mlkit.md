# Camera & ML Kit — CameraX, Pose Detection, Angle Calculation

## Contents

- CameraX setup with Compose
- ML Kit pose detection
- Angle calculation from landmarks
- 1€ filter for smoothing
- 2D projection vs 3D angles
- Production patterns from RepLock

## CameraX Setup with Compose

```kotlin
@Composable
fun CameraPreview(
    modifier: Modifier = Modifier,
    onPoseDetected: (Pose) -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    val previewView = remember { PreviewView(context) }

    LaunchedEffect(Unit) {
        val cameraProvider = ProcessCameraProvider.getInstance(context).await()

        val preview = Preview.Builder().build().also {
            it.surfaceProvider = previewView.surfaceProvider
        }

        val imageAnalysis = ImageAnalysis.Builder()
            .setTargetResolution(Size(640, 480))
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
            .also { analysis ->
                analysis.setAnalyzer(
                    MoreExecutors.directExecutor(),
                    PoseAnalyzer(onPoseDetected)
                )
            }

        val cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA

        cameraProvider.unbindAll()
        cameraProvider.bindToLifecycle(
            lifecycleOwner,
            cameraSelector,
            preview,
            imageAnalysis
        )
    }

    AndroidView(
        factory = { previewView },
        modifier = modifier
    )
}
```

```toml
[dependencies]
camerax-core = { module = "androidx.camera:camera-core", version.ref = "camerax" }
camerax-camera2 = { module = "androidx.camera:camera-camera2", version.ref = "camerax" }
camerax-lifecycle = { module = "androidx.camera:camera-lifecycle", version.ref = "camerax" }
camerax-view = { module = "androidx.camera:camera-view", version.ref = "camerax" }
mlkit-pose = { module = "com.google.mlkit:pose-detection", version = "18.0.0-beta5" }
```

### Key CameraX Rules

1. **Bind to lifecycle** — CameraX auto-starts/stops with lifecycle owner
2. **`STRATEGY_KEEP_ONLY_LATEST`** — drops frames if analyzer is slow. Essential for ML Kit
3. **`unbindAll()` before binding** — prevents duplicate use case errors
4. **Resolution 640x480** — sufficient for pose detection, saves battery
5. **Front camera for workouts** — user faces the screen

## ML Kit Pose Detection

### Pose Analyzer

```kotlin
class PoseAnalyzer(
    private val onPoseDetected: (Pose) -> Unit
) : ImageAnalysis.Analyzer {

    private val poseDetector = PoseDetection.getClient(
        PoseDetectorOptions.Builder()
            .setDetectorMode(PoseDetectorOptions.STREAM_MODE)
            .build()
    )

    @androidx.camera.core.ExperimentalGetImage
    override fun analyze(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image ?: run {
            imageProxy.close()
            return
        }

        val inputImage = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees
        )

        poseDetector.process(inputImage)
            .addOnSuccessListener { pose ->
                onPoseDetected(pose)
            }
            .addOnCompleteListener {
                imageProxy.close()  // ALWAYS close — blocks next frame otherwise
            }
    }
}
```

**Critical:** always close `ImageProxy` in `addOnCompleteListener`, not `addOnSuccessListener`. If detection fails, proxy must still close.

### STREAM_MODE vs SINGLE_IMAGE_MODE

| Mode | Use for | FPS |
|------|---------|-----|
| `STREAM_MODE` | Real-time rep counting | ~15-30fps |
| `SINGLE_IMAGE_MODE` | Single photo analysis | N/A |

Always STREAM_MODE for workout tracking.

## Angle Calculation from Landmarks

### 2D Angle Between Three Points

```kotlin
fun calculateAngle(
    first: PoseLandmark,   // e.g., shoulder
    middle: PoseLandmark,  // e.g., elbow (vertex)
    last: PoseLandmark     // e.g., wrist
): Float {
    val dx1 = first.position.x - middle.position.x
    val dy1 = first.position.y - middle.position.y
    val dx2 = last.position.x - middle.position.x
    val dy2 = last.position.y - middle.position.y

    val angle = atan2(dy2, dx2) - atan2(dy1, dx1)
    var degrees = Math.toDegrees(angle.toDouble()).toFloat()

    if (degrees < 0) degrees += 360f
    if (degrees > 180) degrees = 360f - degrees

    return degrees  // 0-180 range
}
```

### Pushup Detection State Machine

```kotlin
enum class PushupPhase { UP, DOWN }

class PushupRepCounter {
    private var phase = PushupPhase.UP
    private var repCount = 0
    private val elbowAngleFilter = OneEuroFilter(frequency = 15.0)

    fun onPoseUpdate(pose: Pose): Int {
        val leftShoulder = pose.getPoseLandmark(PoseLandmark.LEFT_SHOULDER) ?: return repCount
        val leftElbow = pose.getPoseLandmark(PoseLandmark.LEFT_ELBOW) ?: return repCount
        val leftWrist = pose.getPoseLandmark(PoseLandmark.LEFT_WRIST) ?: return repCount

        val rawAngle = calculateAngle(leftShoulder, leftElbow, leftWrist)
        val smoothedAngle = elbowAngleFilter.filter(rawAngle.toDouble()).toFloat()

        when (phase) {
            PushupPhase.UP -> {
                if (smoothedAngle < 90f) {  // arms bent = down position
                    phase = PushupPhase.DOWN
                }
            }
            PushupPhase.DOWN -> {
                if (smoothedAngle > 150f) {  // arms extended = up position
                    phase = PushupPhase.UP
                    repCount++
                }
            }
        }

        return repCount
    }
}
```

### Squat Detection

```kotlin
class SquatRepCounter {
    private var phase = SquatPhase.STANDING
    private var repCount = 0
    private val kneeAngleFilter = OneEuroFilter(frequency = 15.0)

    fun onPoseUpdate(pose: Pose): Int {
        val hip = pose.getPoseLandmark(PoseLandmark.LEFT_HIP) ?: return repCount
        val knee = pose.getPoseLandmark(PoseLandmark.LEFT_KNEE) ?: return repCount
        val ankle = pose.getPoseLandmark(PoseLandmark.LEFT_ANKLE) ?: return repCount

        val rawAngle = calculateAngle(hip, knee, ankle)
        val smoothed = kneeAngleFilter.filter(rawAngle.toDouble()).toFloat()

        when (phase) {
            SquatPhase.STANDING -> {
                if (smoothed < 110f) phase = SquatPhase.DOWN
            }
            SquatPhase.DOWN -> {
                if (smoothed > 160f) {
                    phase = SquatPhase.STANDING
                    repCount++
                }
            }
        }
        return repCount
    }
}
```

## 1€ Filter for Landmark Smoothing

ML Kit landmarks jitter frame-to-frame. 1€ filter smooths while keeping responsiveness.

```kotlin
class OneEuroFilter(
    private val frequency: Double = 15.0,
    private val minCutoff: Double = 1.0,
    private val beta: Double = 0.007,
    private val dCutoff: Double = 1.0
) {
    private var xPrev: Double? = null
    private var dxPrev: Double = 0.0
    private var lastTime: Long = 0

    fun filter(value: Double): Double {
        val now = System.nanoTime()
        val dt = if (lastTime == 0L) 1.0 / frequency
            else (now - lastTime) / 1_000_000_000.0
        lastTime = now

        val prev = xPrev ?: return value.also { xPrev = it }

        // Derivative
        val dx = (value - prev) / dt
        val edx = exponentialSmoothing(dx, dxPrev, alpha(dt, dCutoff))
        dxPrev = edx

        // Adaptive cutoff
        val cutoff = minCutoff + beta * abs(edx)
        val result = exponentialSmoothing(value, prev, alpha(dt, cutoff))
        xPrev = result
        return result
    }

    private fun alpha(dt: Double, cutoff: Double): Double {
        val tau = 1.0 / (2 * PI * cutoff)
        return 1.0 / (1.0 + tau / dt)
    }

    private fun exponentialSmoothing(
        current: Double, previous: Double, alpha: Double
    ): Double = alpha * current + (1 - alpha) * previous

    fun reset() {
        xPrev = null
        dxPrev = 0.0
        lastTime = 0
    }
}
```

**Tuning:**
- `minCutoff` (1.0) — lower = smoother but more lag
- `beta` (0.007) — higher = less lag during fast movement but more jitter
- `frequency` (15.0) — match your camera frame rate

## 2D Projection vs 3D Angles

ML Kit gives 2D coordinates (screen projection) plus Z values. Why thresholds differ:

| Factor | Effect |
|--------|--------|
| Camera distance | Farther = smaller angles appear in 2D |
| Camera angle | Side view vs front view changes projected angles |
| Body orientation | Rotated body changes landmark positions |
| Z-axis depth | ML Kit Z is relative, not absolute |

**Production approach:** tune thresholds on 2D angles with the specific camera position your app uses. Don't try to reconstruct true 3D angles from ML Kit data — Z accuracy is insufficient.

**Threshold tuning process:**
1. Record 10+ reps at expected camera distance
2. Log raw angles for each frame
3. Find the crossover points (where phase transitions)
4. Set thresholds with 10-15% margin from crossover
5. Apply 1€ filter, re-verify thresholds

## Anti-Patterns

- **Not closing ImageProxy** → blocks entire camera pipeline, no more frames
- **SINGLE_IMAGE_MODE for real-time** → processes one image, ignores stream. Use STREAM_MODE
- **Raw angle without filtering** → jitter causes false rep counts. Always filter
- **Hardcoded angle thresholds without testing** → 90° pushup threshold might be 80° or 100° depending on camera angle
- **Detecting both left and right side** → pick one side (left default). Both sides doubles noise
- **ML Kit on main thread** → `addOnSuccessListener` runs on main by default. Heavy processing should be moved off-main
