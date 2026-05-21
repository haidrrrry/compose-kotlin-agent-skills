# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| latest `main` | yes |
| older tags | no |

This repository contains **documentation and agent skill files only** — no runtime application code, no secrets, no network services.

## Reporting a vulnerability

If you find a security issue (e.g. malicious snippet, credential leak in examples, compromised install script):

1. **Do not** open a public issue with exploit details.
2. Email or DM [@haidrrrry](https://github.com/haidrrrry) on GitHub with:
   - File path and line number
   - Description of the risk
   - Suggested fix (if any)
3. Expect a response within **7 days**.

## Scope

In scope: malicious content in `SKILL.md`, `references/`, `agents/`, or `scripts/validate_skills.py`.

Out of scope: vulnerabilities in third-party apps linked as examples (report to those repos directly).
