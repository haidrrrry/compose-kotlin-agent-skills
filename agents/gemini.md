# Gemini CLI Setup

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .gemini/skills/compose-kotlin-agent-skills
```

## GEMINI.md Integration

Add to your project root `GEMINI.md`:

```markdown
## Android/Kotlin Engineering Skill

For all Kotlin and Jetpack Compose development, read and follow
`.gemini/skills/compose-kotlin-agent-skills/SKILL.md`.

This skill contains:
- Architecture patterns (MVVM, MVI, Clean Architecture)
- Compose UI patterns (recomposition, stability, Modifier ordering)
- Animation recipes (springs, Canvas, gestures)
- Coroutines & Flow guidance (StateFlow vs SharedFlow, error handling)
- DI patterns (Hilt and Koin)
- Room database patterns (DAOs, migrations, offline-first)
- Navigation 3 patterns
- KMP/CMP multiplatform patterns
- Performance optimization
- Testing patterns
- CameraX/ML Kit patterns
- Play Store release checklist

Load the matching reference file from `references/` for deep-dive content.
```

## Verification

Ask Gemini: "How do I build a custom Canvas animation in Compose?"

Should reference `DrawScope`, `rotate()`, `rememberInfiniteTransition` patterns from the skill.
