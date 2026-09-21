#!/usr/bin/env python3
"""Create an empty, local .venture workspace without reading user documents."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[1]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Create empty venture templates; existing files are never overwritten.")
    parser.add_argument("--project", required=True, type=Path, help="Existing project directory")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if sys.version_info < (3, 9):
        parser.error("Python 3.9 or newer is required")
    try:
        project = args.project.expanduser().resolve()
        if not project.is_dir():
            raise ValueError(f"Project directory does not exist: {project}")
        base = project / ".venture"
        targets = {
            "README.md": "workspace-readme.template.md",
            "venture-context.md": "venture-context.template.md",
            "business-input.md": "business-input.template.md",
        }
        directories = [base, *(base / d for d in ("projects", "sources", "evaluations", "reports"))]
        paths = [*directories,
                 *(base / f for f in targets), base / ".gitignore"]
        for p in paths:
            if p.is_symlink():
                raise ValueError(f"Refusing to follow workspace symlink: {p}")
        for p in directories:
            if p.exists() and not p.is_dir():
                raise ValueError(f"Expected a directory: {p}")
        for p in paths[len(directories):]:
            if p.exists() and not p.is_file():
                raise ValueError(f"Expected a regular file: {p}")
        for template in targets.values():
            if not (ROOT / "assets" / template).is_file():
                raise ValueError(f"Missing template: {template}")
        content = {filename: (ROOT / "assets" / src).read_text(encoding="utf-8")
                   for filename, src in targets.items()}
        content[".gitignore"] = "# Business context is private by default.\n*\n!.gitignore\n!README.md\n"
        for directory in directories:
            print(f"{'[DRY RUN] ' if args.dry_run else ''}directory: {directory}")
            if not args.dry_run:
                directory.mkdir(parents=True, exist_ok=True)
        for filename, text in content.items():
            dest = base / filename
            if dest.exists():
                print(f"preserve: {dest}")
                continue
            print(f"{'[DRY RUN] ' if args.dry_run else ''}create: {dest}")
            if not args.dry_run:
                # Exclusive creation prevents accidental replacement of a concurrent edit.
                with dest.open("x", encoding="utf-8") as stream:
                    stream.write(text)
        print("Empty templates only. No conversations, credentials or business files were read.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
