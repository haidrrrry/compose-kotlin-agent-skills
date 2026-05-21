# Agent Setup Guides

Install [compose-kotlin-agent-skills](https://github.com/haidrrrry/compose-kotlin-agent-skills) for your coding agent. Each file below is copy-paste setup for that platform.

**Universal snippet:** [\_shared-snippet.md](_shared-snippet.md)

## IDE & Desktop Agents

| Agent | Guide |
|-------|-------|
| Cursor | [cursor.md](cursor.md) |
| Windsurf | [windsurf.md](windsurf.md) |
| Zed | [zed.md](zed.md) |
| JetBrains AI / Junie | [jetbrains-ai.md](jetbrains-ai.md) |
| Amazon Q Developer | [amazon-q.md](amazon-q.md) |
| Augment Code | [augment.md](augment.md) |
| Trae | [trae.md](trae.md) |
| Tabnine | [tabnine.md](tabnine.md) |

## CLI & Autonomous Agents

| Agent | Guide |
|-------|-------|
| Claude Code / Claude CLI | [claude.md](claude.md) |
| OpenAI Codex CLI | [codex.md](codex.md) |
| Gemini CLI | [gemini.md](gemini.md) |
| OpenCode | [opencode.md](opencode.md) |
| Aider | [aider.md](aider.md) |
| Goose | [goose.md](goose.md) |
| OpenHands | [openhands.md](openhands.md) |
| Qwen Code | [qwen-code.md](qwen-code.md) |
| Factory Droid | [factory.md](factory.md) |
| Devin | [devin.md](devin.md) |

## VS Code Extensions

| Agent | Guide |
|-------|-------|
| GitHub Copilot | [copilot.md](copilot.md) |
| Cline | [cline.md](cline.md) |
| Continue.dev | [continue.md](continue.md) |
| Roo Code | [roo-code.md](roo-code.md) |
| Sourcegraph Cody | [sourcegraph-cody.md](sourcegraph-cody.md) |

## Model-Backed / Multi-Platform

| Agent | Guide |
|-------|-------|
| Kimi (Moonshot) | [kimi.md](kimi.md) |
| DeepSeek | [deepseek.md](deepseek.md) |
| Replit Agent | [replit.md](replit.md) |
| Bolt.new / StackBlitz | [bolt.md](bolt.md) |

## Quick Install (any agent)

```bash
git clone https://github.com/haidrrrry/compose-kotlin-agent-skills.git <agent-folder>/skills/compose-kotlin-agent-skills
```

Replace `<agent-folder>` with path from your agent's guide (e.g. `.cursor`, `.claude`, `.windsurf`).

Then wire `SKILL.md` into that agent's rules / `AGENTS.md` / instructions — see the matching guide above.

**27 agents total** (5 original + 20 new + Devin + Bolt index extras).
