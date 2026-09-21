#!/usr/bin/env python3
"""Install only the bundled venture-evaluator skill. No network or account access."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

NAME = "venture-evaluator"
VERSION = "1.1.2"
MARKER = ".venture-evaluator-install.json"
SOURCE = Path(__file__).resolve().parent / NAME
REQUIRED = (
    "SKILL.md", "references/rubric.md", "references/evidence-policy.md",
    "references/output-format.md", "references/context-workflow.md",
    "references/validation-budget.md", "references/examples.md",
    "assets/venture-context.template.md", "assets/business-input.template.md",
    "assets/workspace-readme.template.md", "agents/openai.yaml",
    "scripts/init_workspace.py", "scripts/render_report.py",
    "references/html-report.md", "assets/report.schema.json",
    "assets/report.template.json", "assets/report.sample.json",
    "assets/report/report.css", "assets/report/report.js",
)


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def validate_package(folder: Path) -> None:
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError(f"Not a regular skill directory: {folder}")
    for p in folder.rglob("*"):
        if p.is_symlink():
            raise ValueError(f"Symlink found; review and install manually: {p}")
    for rel in REQUIRED:
        if not (folder / rel).is_file():
            raise ValueError(f"Missing package file: {folder / rel}")
    text = (folder / "SKILL.md").read_text(encoding="utf-8")
    front = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not front or not re.search(r"^name:\s*venture-evaluator\s*$", front[1], re.M):
        raise ValueError(f"Invalid SKILL.md name/frontmatter: {folder}")
    if not re.search(r"^description:", front[1], re.M):
        raise ValueError("SKILL.md has no description")


def fingerprint(folder: Path) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for p in sorted(folder.rglob("*")):
        if p.is_symlink():
            raise ValueError(f"Refusing to follow symlink: {p}")
        if p.is_file() and p.name != MARKER:
            result[p.relative_to(folder).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def marker_data(dest: Path) -> Optional[dict]:
    p = dest / MARKER
    if not p.exists():
        return None
    if p.is_symlink():
        raise ValueError(f"Refusing marker symlink: {p}")
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or obj.get("skill_name") != NAME:
        raise ValueError(f"Unrecognized installer manifest: {p}")
    return obj


def existing_identity(dest: Path) -> bool:
    p = dest / "SKILL.md"
    if not p.is_file() or p.is_symlink():
        return False
    text = p.read_text(encoding="utf-8")
    front = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    return bool(front and re.search(r"^name:\s*venture-evaluator\s*$", front[1], re.M))


def destinations(args: argparse.Namespace) -> List[Tuple[str, Path]]:
    if args.scope == "project":
        if args.project is None:
            raise ValueError("--scope project requires --project /path/to/project")
        base = args.project.expanduser().resolve()
        if not base.is_dir():
            raise ValueError(f"Project directory does not exist: {base}")
    else:
        if args.project is not None:
            raise ValueError("Use --scope project together with --project")
        base = (args.home or Path.home()).expanduser().resolve()
        if not base.is_dir():
            raise ValueError(f"Home directory does not exist: {base}")
    selected = ("claude", "codex") if args.target == "both" else (args.target,)
    folders = {"claude": ".claude", "codex": ".agents"}
    return [(host, base / folders[host] / "skills" / NAME) for host in selected]


def backup_destination(dest: Path) -> Path:
    base = dest.parent.parent / "skill-backups"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{NAME}-{timestamp()}-{uuid.uuid4().hex[:8]}"


def install_one(dest: Path, hashes: Dict[str, str]) -> Optional[Path]:
    """Stage first, then rename. Roll back the old directory on a rename failure."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".venture-evaluator-stage-", dir=str(dest.parent.parent)))
    stage = temp / NAME
    backup: Optional[Path] = None
    try:
        shutil.copytree(SOURCE, stage)
        manifest = {
            "skill_name": NAME,
            "version": VERSION,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "files": hashes,
        }
        (stage / MARKER).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if dest.exists():
            backup = backup_destination(dest)
            dest.rename(backup)
        try:
            stage.rename(dest)
        except OSError:
            if backup is not None and not dest.exists():
                backup.rename(dest)
            raise
        return backup
    finally:
        # Delete only the temporary directory created by this function.
        shutil.rmtree(temp, ignore_errors=True)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install the bundled skill for Claude Code and/or Codex. No network; no sudo."
    )
    parser.add_argument("--action", choices=("install", "check", "uninstall"), default="install")
    parser.add_argument("--target", choices=("both", "claude", "codex"), default="both")
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project", type=Path, help="Existing project directory for project scope")
    parser.add_argument("--home", type=Path, help="Override home directory (portable setup/testing)")
    parser.add_argument("--replace", action="store_true", help="Back up an existing skill before replacing it")
    parser.add_argument("--dry-run", action="store_true", help="Print intended changes without writing")
    args = parser.parse_args(argv)
    if sys.version_info < (3, 9):
        parser.error("Python 3.9 or newer is required")
    if args.replace and args.action != "install":
        parser.error("--replace applies only to installation")
    if args.home is not None and args.scope != "user":
        parser.error("--home applies only to user scope")

    try:
        targets = destinations(args)
        source_hashes: Dict[str, str] = {}
        if args.action == "install":
            validate_package(SOURCE)
            source_hashes = fingerprint(SOURCE)
        planned = []
        # Preflight every target before mutating either target.
        for host, dest in targets:
            if dest.is_symlink():
                raise ValueError(f"Existing destination is a symlink; review manually: {dest}")
            if dest.resolve() == SOURCE.resolve():
                raise ValueError("Source and destination are the same directory")
            exists = dest.exists()
            if exists and not dest.is_dir():
                raise ValueError(f"Destination is not a directory: {dest}")
            if args.action == "install":
                if exists:
                    if not existing_identity(dest):
                        raise ValueError(f"Refusing to replace an unrelated directory: {dest}")
                    if fingerprint(dest) == source_hashes:
                        planned.append((host, dest, "unchanged"))
                    elif args.replace:
                        planned.append((host, dest, "replace"))
                    else:
                        raise ValueError(
                            f"Existing skill differs: {dest}\n"
                            "Review changes, then use --replace to back it up and install."
                        )
                else:
                    planned.append((host, dest, "install"))
            elif args.action == "check":
                if not exists:
                    raise ValueError(f"Skill not installed: {dest}")
                validate_package(dest)
                manifest = marker_data(dest)
                if manifest and manifest.get("files") != fingerprint(dest):
                    raise ValueError(f"Installed files differ from their installer manifest: {dest}")
                planned.append((host, dest, "valid" if manifest else "valid (manual install)"))
            else:
                if not exists:
                    planned.append((host, dest, "absent"))
                else:
                    if marker_data(dest) is None:
                        raise ValueError(f"No installer manifest; uninstall this manual copy yourself: {dest}")
                    planned.append((host, dest, "uninstall"))

        print(f"Venture Evaluator {VERSION} | action={args.action} | scope={args.scope}")
        for host, dest, action in planned:
            prefix = "[DRY RUN] " if args.dry_run else ""
            print(f"{prefix}{host}: {action} -> {dest}")
            if args.dry_run or action in ("unchanged", "absent") or action.startswith("valid"):
                continue
            if action in ("install", "replace"):
                backup = install_one(dest, source_hashes)
                if backup:
                    print(f"  Previous version preserved: {backup}")
            elif action == "uninstall":
                backup = backup_destination(dest)
                dest.rename(backup)
                print(f"  Reversible removal; files preserved: {backup}")
        if args.action == "install" and not args.dry_run:
            print("Done. Reopen/refresh your host if the skill is not visible.")
            print("Claude Code: /venture-evaluator | Codex: $venture-evaluator")
        if args.action == "check":
            print("Local file checks only; this does not test model behavior or host recognition.")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
