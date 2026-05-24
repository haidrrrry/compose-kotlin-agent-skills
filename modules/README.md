# Skill Modules — Reference Organization

Logical groupings for `references/` (flat on disk for stable paths; indexed here for discovery).

## Guardrails (load first)

| File | Module |
|------|--------|
| `references/00-banned-antipatterns.md` | Master banned table — WRONG/RIGHT lookup |

## Architecture & Data

| File | Module |
|------|--------|
| `references/01-architecture.md` | Clean Architecture, MVVM, MVI |
| `references/04-coroutines-flow.md` | Coroutines, Flow, errors |
| `references/05-hilt-di.md` | Dependency injection |
| `references/06-room-db.md` | Persistence, offline-first |
| `references/09-networking.md` | Ktor, auth, sync |
| `references/14-datastore.md` | DataStore, SharedPreferences migration |
| `references/15-paging3.md` | Paging 3, RemoteMediator |

## UI & Platform

| File | Module |
|------|--------|
| `references/02-compose-ui.md` | Compose, Material 3, edge-to-edge |
| `references/03-animations.md` | Motion, Canvas |
| `references/07-navigation.md` | Navigation 3 |
| `references/08-kmp-cmp.md` | Kotlin Multiplatform |
| `references/10-performance.md` | Recomposition, LazyColumn |
| `references/16-coil-image.md` | Coil 3.4 image loading |
| `references/17-accessibility.md` | TalkBack, semantics, WCAG |
| `references/19-xml-to-compose-migration.md` | XML Views → Compose |

## Quality & Release

| File | Module |
|------|--------|
| `references/11-testing.md` | Unit + UI tests |
| `references/12-camera-mlkit.md` | CameraX, ML Kit |
| `references/13-release-checklist.md` | Ship checklist |
| `references/18-gradle-build-logic.md` | Gradle, KSP, R8, baseline profiles |

Sub-skills in `skills/` map to these modules — see [`AGENTS.md`](../AGENTS.md).

Examples: [`examples/todo-mvi/`](../examples/todo-mvi/) — MVI reference implementation.
