#!/usr/bin/env python3
"""
Validate all SKILL.md files in the compose-kotlin-agent-skills repository.

Checks:
  - YAML frontmatter exists with required keys: name, description
  - name field constraints (kebab-case, max 64 chars, no reserved words)
  - description constraints (non-empty, max 1024 chars, no XML tags)
  - Internal markdown links resolve to existing files
  - SKILL.md body line count warning if > 500 lines
  - Optional: lock-file parity (--lock-check api/skills.lock)
  - Optional: JUnit XML report (--junit results.xml)

Exit code 0 = pass, 1 = failure (for CI).
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
LINK_RE = re.compile(r"\]\(([^)]+)\)")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_NAME_SUBSTRINGS = ("anthropic", "claude")
MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024
MAX_BODY_LINES = 500
SKIP_LINK_PREFIXES = ("http://", "https://", "mailto:", "#")


@dataclass
class Issue:
    path: Path
    message: str
    severity: str = "error"  # error | warning


@dataclass
class ValidationResult:
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "warning"]

    def ok(self, strict: bool) -> bool:
        if self.errors:
            return False
        if strict and self.warnings:
            return False
        return True


def parse_simple_yaml(block: str) -> dict[str, str]:
    """Parse minimal YAML frontmatter (key: value and multiline > descriptions)."""
    data: dict[str, str] = {}
    current_key: str | None = None
    multiline_buffer: list[str] = []

    for line in block.splitlines():
        if line.strip().startswith("#"):
            continue
        if re.match(r"^[A-Za-z0-9_-]+:\s*>", line):
            current_key = line.split(":", 1)[0].strip()
            multiline_buffer = []
            continue
        if current_key and (line.startswith(" ") or line.startswith("\t")):
            multiline_buffer.append(line.strip())
            continue
        if current_key and multiline_buffer:
            data[current_key] = " ".join(multiline_buffer).strip()
            current_key = None
            multiline_buffer = []
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            key, value = match.group(1), match.group(2).strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            data[key] = value
    if current_key and multiline_buffer:
        data[current_key] = " ".join(multiline_buffer).strip()
    return data


def validate_frontmatter(path: Path, content: str, result: ValidationResult) -> str | None:
    match = FRONTMATTER_RE.match(content)
    if not match:
        result.issues.append(Issue(path, "Missing YAML frontmatter (must start with ---)"))
        return None

    fm = parse_simple_yaml(match.group(1))
    body = content[match.end() :]

    if "name" not in fm or not fm["name"].strip():
        result.issues.append(Issue(path, "Frontmatter missing required field: name"))
    else:
        name = fm["name"].strip()
        if len(name) > MAX_NAME_LEN:
            result.issues.append(Issue(path, f"name exceeds {MAX_NAME_LEN} chars: {len(name)}"))
        if not NAME_RE.match(name):
            result.issues.append(
                Issue(path, f"name must be kebab-case lowercase: '{name}'")
            )
        for reserved in RESERVED_NAME_SUBSTRINGS:
            if reserved in name:
                result.issues.append(Issue(path, f"name must not contain '{reserved}'"))

    if "description" not in fm or not fm["description"].strip():
        result.issues.append(Issue(path, "Frontmatter missing required field: description"))
    else:
        desc = fm["description"].strip()
        if len(desc) > MAX_DESC_LEN:
            result.issues.append(
                Issue(path, f"description exceeds {MAX_DESC_LEN} chars: {len(desc)}")
            )
        if "<" in desc or ">" in desc:
            result.issues.append(Issue(path, "description must not contain XML tags"))
        if "Use when" not in desc and "use when" not in desc.lower():
            result.issues.append(
                Issue(
                    path,
                    "description should include 'Use when...' trigger phrases",
                    severity="warning",
                )
            )

    body_lines = body.count("\n") + (1 if body.strip() else 0)
    if body_lines > MAX_BODY_LINES:
        result.issues.append(
            Issue(
                path,
                f"SKILL.md body has {body_lines} lines (max recommended {MAX_BODY_LINES})",
                severity="warning",
            )
        )

    return body


def resolve_link(skill_path: Path, repo_root: Path, target: str) -> Path | None:
    target = target.strip()
    if not target or any(target.startswith(p) for p in SKIP_LINK_PREFIXES):
        return None
    if target.startswith("/"):
        candidate = repo_root / target.lstrip("/")
    else:
        candidate = (skill_path.parent / target).resolve()
    return candidate


def validate_links(skill_path: Path, body: str, repo_root: Path, result: ValidationResult) -> None:
    for raw_target in LINK_RE.findall(body):
        target = raw_target.split("#", 1)[0].strip()
        if not target:
            continue
        resolved = resolve_link(skill_path, repo_root, target)
        if resolved is None:
            continue
        try:
            resolved.relative_to(repo_root.resolve())
        except ValueError:
            result.issues.append(
                Issue(skill_path, f"Link escapes repo: {raw_target}", severity="warning")
            )
            continue
        if not resolved.exists():
            result.issues.append(Issue(skill_path, f"Broken link: {raw_target}"))


def find_skill_files(repo_root: Path) -> list[Path]:
    skills: list[Path] = []
    root_skill = repo_root / "SKILL.md"
    if root_skill.is_file():
        skills.append(root_skill)
    for path in repo_root.rglob("SKILL.md"):
        if path == root_skill:
            continue
        if ".git" in path.parts:
            continue
        skills.append(path)
    return sorted(skills)


def compute_lock_entries(repo_root: Path, skill_files: list[Path]) -> dict[str, str]:
    """Return { relative_skill_path: md5 } for every SKILL.md."""
    entries: dict[str, str] = {}
    for path in skill_files:
        rel = path.relative_to(repo_root).as_posix()
        digest = hashlib.md5(path.read_bytes()).hexdigest()
        entries[rel] = digest
    return entries


def parse_lock_file(lock_path: Path) -> dict[str, str]:
    """Parse api/skills.lock lines of the form: <md5>  <relative/path>"""
    entries: dict[str, str] = {}
    if not lock_path.is_file():
        return entries
    for raw in lock_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        digest, rel = parts
        entries[rel.strip()] = digest.strip()
    return entries


def validate_lock(
    repo_root: Path,
    skill_files: list[Path],
    lock_path: Path,
    result: ValidationResult,
) -> None:
    actual = compute_lock_entries(repo_root, skill_files)
    expected = parse_lock_file(lock_path)

    if not expected:
        result.issues.append(
            Issue(lock_path, f"Lock file is empty or missing: {lock_path}", severity="error")
        )
        return

    actual_keys = set(actual.keys())
    expected_keys = set(expected.keys())

    for missing in sorted(expected_keys - actual_keys):
        result.issues.append(
            Issue(lock_path, f"Lock entry references missing skill: {missing}")
        )
    for added in sorted(actual_keys - expected_keys):
        result.issues.append(
            Issue(
                lock_path,
                f"New skill not registered in lock file: {added} — run scripts/update_lock.sh or bump api/skills.lock",
            )
        )
    for shared in sorted(actual_keys & expected_keys):
        if actual[shared] != expected[shared]:
            result.issues.append(
                Issue(
                    lock_path,
                    f"Skill content changed — bump lock entry for {shared}",
                    severity="warning",
                )
            )


def validate_repo(repo_root: Path, strict: bool) -> tuple[ValidationResult, list[Path]]:
    result = ValidationResult()
    skill_files = find_skill_files(repo_root)

    if not skill_files:
        result.issues.append(Issue(repo_root, "No SKILL.md files found"))
        return result, skill_files

    for skill_path in skill_files:
        try:
            content = skill_path.read_text(encoding="utf-8")
        except OSError as exc:
            result.issues.append(Issue(skill_path, f"Cannot read file: {exc}"))
            continue
        body = validate_frontmatter(skill_path, content, result)
        if body is not None:
            validate_links(skill_path, body, repo_root, result)

    # Folder name should match frontmatter name when skill is in skills/<name>/
    for skill_path in skill_files:
        if skill_path.parent.parent.name != "skills":
            continue
        match = FRONTMATTER_RE.match(skill_path.read_text(encoding="utf-8"))
        if not match:
            continue
        fm = parse_simple_yaml(match.group(1))
        expected_dir = fm.get("name", "").strip()
        if expected_dir and skill_path.parent.name != expected_dir:
            result.issues.append(
                Issue(
                    skill_path,
                    f"Folder '{skill_path.parent.name}' must match frontmatter name '{expected_dir}'",
                    severity="warning",
                )
            )

    return result, skill_files


def print_report(result: ValidationResult, repo_root: Path) -> None:
    print(f"Validating skills in: {repo_root.resolve()}")
    print("-" * 60)
    if not result.issues:
        print("OK — all checks passed.")
        return
    for issue in result.issues:
        prefix = "ERROR" if issue.severity == "error" else "WARN "
        try:
            rel = issue.path.relative_to(repo_root)
        except ValueError:
            rel = issue.path
        print(f"{prefix} {rel}: {issue.message}")
    print("-" * 60)
    print(f"Errors: {len(result.errors)}  Warnings: {len(result.warnings)}")


def write_junit(result: ValidationResult, skill_files: list[Path], repo_root: Path, junit_path: Path) -> None:
    suite = ET.Element(
        "testsuite",
        attrib={
            "name": "skill-lint",
            "tests": str(max(len(skill_files), 1)),
            "failures": str(len(result.errors)),
            "errors": "0",
            "skipped": "0",
        },
    )
    issues_by_path: dict[str, list[Issue]] = {}
    for issue in result.issues:
        try:
            key = issue.path.relative_to(repo_root).as_posix()
        except ValueError:
            key = str(issue.path)
        issues_by_path.setdefault(key, []).append(issue)

    targets = [p.relative_to(repo_root).as_posix() for p in skill_files] or ["repo"]
    for target in targets:
        case = ET.SubElement(suite, "testcase", attrib={"classname": "skill-lint", "name": target})
        for issue in issues_by_path.get(target, []):
            tag = "failure" if issue.severity == "error" else "system-out"
            node = ET.SubElement(case, tag, attrib={"message": issue.message[:200]})
            node.text = issue.message

    junit_path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(suite)
    tree.write(junit_path, encoding="utf-8", xml_declaration=True)


def write_lock(skill_files: list[Path], repo_root: Path, lock_path: Path) -> None:
    entries = compute_lock_entries(repo_root, skill_files)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# compose-kotlin-agent-skills — skill registry", "# Format: <md5>  <relative path>", ""]
    for rel in sorted(entries):
        lines.append(f"{entries[rel]}  {rel}")
    lock_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent SKILL.md files")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: parent of scripts/)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures",
    )
    parser.add_argument(
        "--lock-check",
        type=Path,
        default=None,
        help="Verify skill set matches the given api/skills.lock file",
    )
    parser.add_argument(
        "--write-lock",
        type=Path,
        default=None,
        help="(Re)generate the lock file at the given path and exit 0",
    )
    parser.add_argument(
        "--junit",
        type=Path,
        default=None,
        help="Write JUnit XML report to the given path",
    )
    args = parser.parse_args()

    repo_root = args.root or Path(__file__).resolve().parent.parent
    if not (repo_root / "SKILL.md").is_file() and not list(repo_root.rglob("SKILL.md")):
        print(f"No SKILL.md under {repo_root}", file=sys.stderr)
        return 1

    result, skill_files = validate_repo(repo_root, args.strict)

    if args.write_lock is not None:
        write_lock(skill_files, repo_root, args.write_lock)
        print(f"Wrote lock file: {args.write_lock}")

    if args.lock_check is not None:
        validate_lock(repo_root, skill_files, args.lock_check, result)

    print_report(result, repo_root)

    if args.junit is not None:
        write_junit(result, skill_files, repo_root, args.junit)
        print(f"Wrote JUnit report: {args.junit}")

    return 0 if result.ok(args.strict) else 1


if __name__ == "__main__":
    sys.exit(main())
