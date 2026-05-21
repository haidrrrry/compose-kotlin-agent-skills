# Release Checklist — Signing, R8, Baseline Profiles, Play Store

## Contents

- Signing config
- ProGuard/R8 rules
- Baseline profiles
- Release build config
- Play Store checklist

## Signing Config

### Generate Keystore

```bash
keytool -genkeypair \
    -v \
    -keystore release.keystore \
    -alias release \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -storepass <password> \
    -keypass <password>
```

### Gradle Config (CI-safe)

```kotlin
// build.gradle.kts (app)
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: "release"
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

**Never commit keystore or passwords to git.** Use environment variables or GitHub Secrets.

### GitHub Actions Secrets

```yaml
# .github/workflows/release.yml
env:
  KEYSTORE_PATH: ${{ runner.temp }}/release.keystore
  KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
  KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
  KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}

steps:
  - name: Decode keystore
    run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > ${{ runner.temp }}/release.keystore
```

## ProGuard/R8 Rules

### What R8 Does

1. **Shrinking** — removes unused code
2. **Obfuscation** — renames classes/methods to short names
3. **Optimization** — inlines methods, removes dead branches

### What Breaks Without Rules

| Library | What breaks | Rule needed |
|---------|------------|-------------|
| **Kotlin serialization** | Serialized class names stripped | Keep `@Serializable` classes |
| **Room** | Entity/DAO reflection fails | Keep `@Entity`, `@Dao` |
| **Hilt** | Injection fails | Auto-handled by Hilt plugin |
| **Retrofit/Ktor** | DTO deserialization fails | Keep DTO classes |
| **ML Kit** | Model loading fails | Keep ML Kit classes |
| **Compose** | Generally fine | Compose compiler handles it |

### proguard-rules.pro

```proguard
# Kotlin Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** { *** Companion; }
-keepclasseswithmembers class kotlinx.serialization.json.** {
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class com.example.app.data.dto.**$$serializer { *; }
-keepclassmembers class com.example.app.data.dto.** {
    *** Companion;
    *** serializer(...);
}

# Room
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
-dontwarn androidx.room.paging.**

# Ktor
-keep class io.ktor.** { *; }
-dontwarn io.ktor.**

# ML Kit
-keep class com.google.mlkit.** { *; }
-dontwarn com.google.mlkit.**

# Keep enums used in serialization
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

### Testing R8

```bash
# Build release APK
./gradlew assembleRelease

# Test release APK thoroughly — R8 bugs only appear in release builds
# Install on device and test ALL features
adb install app/build/outputs/apk/release/app-release.apk
```

**Always test the release build.** Debug works ≠ Release works. R8 can strip code that debug builds keep.

## Baseline Profiles

See `10-performance.md` for generation. Here's the release integration:

```kotlin
// build.gradle.kts (app)
dependencies {
    implementation("androidx.profileinstaller:profileinstaller:1.4.1")
    baselineProfile(project(":benchmark"))
}

android {
    buildTypes {
        release {
            baselineProfile.automaticGenerationDuringBuild = true
        }
    }
}
```

Verify in APK:
```bash
unzip -l app-release.apk | grep baseline
# Expected: assets/dexopt/baseline.prof
# Expected: assets/dexopt/baseline.profm
```

## Release Build Config

```kotlin
android {
    defaultConfig {
        applicationId = "com.example.app"
        versionCode = 12
        versionName = "1.2.0"
        targetSdk = 35
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
        debug {
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
    }

    buildFeatures {
        buildConfig = true
    }
}
```

### Version Code Strategy

```
versionCode = major * 10000 + minor * 100 + patch
// 1.2.3 → 10203
// 2.0.0 → 20000
```

Or auto-increment from git:
```kotlin
val versionCode = providers.exec {
    commandLine("git", "rev-list", "--count", "HEAD")
}.standardOutput.asText.get().trim().toInt()
```

## Play Store Checklist

### Before First Upload

- [ ] App signing — enrolled in Play App Signing (Google manages key)
- [ ] Privacy policy URL — required for any app requesting permissions
- [ ] Content rating — complete questionnaire
- [ ] Target audience — declare age group
- [ ] Data safety form — declare what data you collect

### Before Every Release

- [ ] `versionCode` incremented (Play Store rejects same or lower)
- [ ] `versionName` updated for users
- [ ] Release build tested on physical device
- [ ] All features work with R8 enabled
- [ ] Baseline profile included in APK
- [ ] Crash-free in Firebase Crashlytics (if integrated)
- [ ] Screenshot updated if UI changed
- [ ] Release notes written (max 500 chars per language)

### Accessibility Service (Special Review)

If your app uses `AccessibilityService`:

- [ ] Service description in XML matches actual usage
- [ ] Only requested event types are declared
- [ ] Prominent disclosure shown to user before enabling
- [ ] YouTube video demonstrating the accessibility feature
- [ ] Detailed justification in Play Console review notes

**Play Store will reject** vague accessibility service descriptions. Be specific: "This service monitors which app is in the foreground to determine if a blocked app has been opened."

### App Bundle vs APK

```bash
# Always use App Bundle for Play Store
./gradlew bundleRelease
# Output: app/build/outputs/bundle/release/app-release.aab

# APK only for sideloading or testing
./gradlew assembleRelease
```

App Bundles are ~15% smaller than APKs. Play Store requires bundles for new apps.

## CI/CD — GitHub Actions

```yaml
name: Release Build

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Decode keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > ${{ runner.temp }}/release.keystore

      - name: Build release bundle
        env:
          KEYSTORE_PATH: ${{ runner.temp }}/release.keystore
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      - name: Upload AAB
        uses: actions/upload-artifact@v4
        with:
          name: release-aab
          path: app/build/outputs/bundle/release/app-release.aab
```

## Anti-Patterns

- **Committing keystore to git** → anyone with repo access can sign as you
- **`isMinifyEnabled = false` in release** → APK 2-3x larger, all code visible
- **No R8 testing** → crashes in production that debug never catches
- **`fallbackToDestructiveMigration()` in release** → deletes all user data on schema change
- **Same `applicationId` for debug and release** → can't install both simultaneously for testing
- **Forgetting `isShrinkResources = true`** → unused drawables/layouts stay in APK
- **Manual version code management** → forgetting to increment rejects Play Store upload
