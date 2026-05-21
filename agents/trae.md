# Trae (ByteDance) Setup

Trae IDE AI uses project rules and SOLO builder context.

## Install

```bash
cd your-android-project
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git .trae/skills/compose-kotlin-agent-skills
```

## Trae Rules

Trae → Settings → Rules for AI → add:

```markdown
# compose-kotlin-agent-skills

Base path: `.trae/skills/compose-kotlin-agent-skills/`
Always read SKILL.md for Kotlin/Compose/Android.
Use references/ for: 架构, Compose UI, 动画, Room, 网络, 性能, 测试, 发布.

Mandatory: 字符串资源化, ViewModel 持有状态, LazyColumn key.
```

## SOLO Mode

When building Android app in SOLO, attach SKILL.md as spec document in builder input.

## Verification

Trae: "按 compose-kotlin-agent-skills 创建 Compose 主题系统 CompositionLocal"

Should mirror ProvideAppTheme + LocalAppTheme pattern from references/02-compose-ui.md.
