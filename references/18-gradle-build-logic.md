---
name: gradle-build-logic
description: >
  Gradle convention plugins, Version Catalogs, composite builds, AGP 9, build variants,
  R8/ProGuard, baseline profiles, KSP migration from KAPT. Use when setting up Android builds.
version: "2.2.0"
updated: "2026-05-21"
---

# Gradle Build Logic — AGP 9, Catalogs, KSP, R8

## Pinned versions (2026)

```toml
# gradle/libs.versions.toml
[versions]
kotlin = "2.1.20"
agp = "9.0.0"
ksp = "2.1.20-2.0.1"
compose-bom = "2025.05.00"
hilt = "2.56.2"
room = "2.7.1"
```

---

## WRONG / RIGHT 1 — Hardcoded deps in every module

```kotlin
// WRONG — version drift across modules
// app/build.gradle.kts
dependencies {
    implementation("androidx.compose.ui:ui:1.7.0")
    implementation("com.google.dagger:hilt-android:2.50")
}

// RIGHT — Version Catalog (libs.versions.toml) + type-safe accessors
// app/build.gradle.kts
dependencies {
    implementation(platform(libs.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)
}
```

---

## WRONG / RIGHT 2 — kapt for Hilt/Room on K2 new project

```kotlin
// WRONG — kapt blocks K2 performance gains
plugins {
    id("kotlin-kapt")
}
dependencies {
    kapt("com.google.dagger:hilt-compiler:2.56.2")
    kapt("androidx.room:room-compiler:2.7.1")
}

// RIGHT — KSP
plugins {
    alias(libs.plugins.ksp)
}
dependencies {
    ksp(libs.hilt.compiler)
    ksp(libs.room.compiler)
}
```

---

## WRONG / RIGHT 3 — Duplicate Android config in every module

```kotlin
// WRONG — copy-paste compileSdk in 12 modules
android {
    compileSdk = 35
    defaultConfig { minSdk = 26; targetSdk = 35 }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

// RIGHT — convention plugin in build-logic/
// build-logic/convention/src/main/kotlin/AndroidApplicationConventionPlugin.kt
class AndroidApplicationConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("com.android.application")
            pluginManager.apply("org.jetbrains.kotlin.android")
            extensions.configure<ApplicationExtension> {
                compileSdk = 35
                defaultConfig {
                    minSdk = 26
                    targetSdk = 35
                }
                compileOptions {
                    sourceCompatibility = JavaVersion.VERSION_17
                    targetCompatibility = JavaVersion.VERSION_17
                }
            }
        }
    }
}

// app/build.gradle.kts
plugins {
    id("app.android.application")
}
```

---

## WRONG / RIGHT 4 — AGP 8 namespace / compileSdk mistakes

```kotlin
// WRONG — missing namespace (AGP 8+), compileSdk 34 on new 2026 app
android {
    compileSdk = 34
    defaultConfig {
        applicationId = "com.example.app"
    }
}

// RIGHT — AGP 9 defaults
android {
    namespace = "com.example.app"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.example.app"
        targetSdk = 35
    }
    buildFeatures {
        compose = true
        buildConfig = false  // prefer BuildConfig only when needed
    }
}
```

---

## WRONG / RIGHT 5 — R8 strips Hilt/Room/Serializable models

```kotlin
// WRONG — no keep rules; crash only in release
// (empty proguard-rules.pro)

// RIGHT — consumer rules + model keeps
# proguard-rules.pro
-keepattributes *Annotation*
-keep class dagger.hilt.** { *; }
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.annotation.Keep class *
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

# Keep Nav 3 @Serializable routes
-keep @kotlinx.serialization.Serializable class ** { *; }
```

---

## WRONG / RIGHT 6 — Baseline profile not wired

```kotlin
// WRONG — no profile; cold start slow in production
dependencies {
    implementation("androidx.profileinstaller:profileinstaller:1.4.1")
}
// no baseline-profile module

// RIGHT — baseline-profile module + generate on CI
// baseline-profile/build.gradle.kts
plugins {
    id("com.android.test")
    alias(libs.plugins.baselineprofile)
}
dependencies {
    implementation(project(":app"))
    implementation(libs.benchmark.macro.junit4)
}

// Generate locally:
// ./gradlew :app:generateReleaseBaselineProfile
```

---

## Composite builds (optional)

```kotlin
// settings.gradle.kts — include build-logic as composite
pluginManagement {
    includeBuild("build-logic")
}
```

## Decision matrix

| Need | Solution |
|---|---|
| Shared Android/Kotlin config | Convention plugin in `build-logic/` |
| Centralized versions | `gradle/libs.versions.toml` |
| Annotation processing | KSP not kapt |
| Release crashes from R8 | Keep rules for Hilt, Room, Serialization |
| Startup perf | Baseline profile module + Macrobenchmark |
| Debug vs release secrets | `buildTypes` + manifest placeholders |
