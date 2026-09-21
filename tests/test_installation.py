"""Offline regression tests. Does not call Claude, Codex, or any model API."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

KIT = Path(__file__).resolve().parents[1]
INSTALL = KIT / "install.py"
INIT = KIT / "venture-evaluator" / "scripts" / "init_workspace.py"


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="venture-skill-test-")
        self.base = Path(self.temp.name)
        self.home = self.base / "test home 한글"
        self.home.mkdir()
        self.project = self.base / "사업 프로젝트"
        self.project.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def run_installer(self, *args, expected=0):
        cmd = [sys.executable, str(INSTALL), "--home", str(self.home), *args]
        result = subprocess.run(cmd, text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def dest(self, host):
        return self.home / (".claude" if host == "claude" else ".agents") / "skills" / "venture-evaluator"

    def test_dry_run_writes_nothing(self):
        self.run_installer("--dry-run")
        self.assertEqual(list(self.home.iterdir()), [])

    def test_both_install_and_check(self):
        self.run_installer()
        for host in ("claude", "codex"):
            self.assertTrue((self.dest(host) / "SKILL.md").is_file())
        self.run_installer("--action", "check")

    def test_single_target(self):
        self.run_installer("--target", "codex")
        self.assertTrue(self.dest("codex").exists())
        self.assertFalse(self.dest("claude").exists())

    def test_repeat_is_idempotent(self):
        self.run_installer()
        marker = self.dest("claude") / ".venture-evaluator-install.json"
        before = marker.read_bytes()
        result = self.run_installer()
        self.assertIn("unchanged", result.stdout)
        self.assertEqual(marker.read_bytes(), before)
        self.assertFalse((self.home / ".claude" / "skill-backups").exists())

    def test_conflict_refuses_all_targets_before_writing(self):
        d = self.dest("codex")
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: venture-evaluator\ndescription: local\n---\nlocal changes\n")
        self.run_installer(expected=1)
        self.assertFalse(self.dest("claude").exists())
        self.assertIn("local changes", (d / "SKILL.md").read_text())

    def test_replace_preserves_old_version(self):
        self.run_installer()
        old = self.dest("claude") / "my-private-note.txt"
        old.write_text("preserve this", encoding="utf-8")
        self.run_installer("--replace")
        backups = list((self.home / ".claude" / "skill-backups").glob("venture-evaluator-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "my-private-note.txt").read_text(), "preserve this")
        self.assertFalse(old.exists())
        self.run_installer("--action", "check")

    def test_uninstall_is_reversible(self):
        self.run_installer()
        self.run_installer("--action", "uninstall")
        for host in ("claude", "codex"):
            self.assertFalse(self.dest(host).exists())
            backups = list((self.dest(host).parent.parent / "skill-backups").glob("venture-evaluator-*"))
            self.assertEqual(len(backups), 1)
            self.assertTrue((backups[0] / "SKILL.md").is_file())

    def test_integrity_check_detects_edits(self):
        self.run_installer()
        path = self.dest("claude") / "references" / "rubric.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
        self.run_installer("--action", "check", expected=1)

    def test_unrelated_folder_not_replaced(self):
        d = self.dest("claude")
        d.mkdir(parents=True)
        (d / "not-a-skill.txt").write_text("important")
        self.run_installer("--replace", expected=1)
        self.assertEqual((d / "not-a-skill.txt").read_text(), "important")

    def test_manual_copy_not_removed(self):
        d = self.dest("claude")
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: venture-evaluator\n---\nmanual")
        self.run_installer("--action", "uninstall", "--target", "claude", expected=1)
        self.assertTrue(d.exists())

    def test_project_scope_with_unicode_and_spaces(self):
        result = subprocess.run([sys.executable, str(INSTALL), "--scope", "project", "--project", str(self.project)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / ".agents/skills/venture-evaluator/SKILL.md").is_file())
        self.assertTrue((self.project / ".claude/skills/venture-evaluator/SKILL.md").is_file())

    def test_destination_symlink_rejected(self):
        if os.name == "nt":
            self.skipTest("Symlink setup may require Windows privileges")
        d = self.dest("claude")
        d.parent.mkdir(parents=True)
        d.symlink_to(self.project, target_is_directory=True)
        self.run_installer("--replace", expected=1)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_missing_project_is_not_created(self):
        missing = self.base / "missing"
        result = subprocess.run([sys.executable, str(INSTALL), "--scope", "project", "--project", str(missing)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(missing.exists())

    def test_workspace_non_overwrite(self):
        for _ in range(2):
            result = subprocess.run([sys.executable, str(INIT), "--project", str(self.project)],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            p = self.project / ".venture/venture-context.md"
            if _ == 0:
                p.write_text("private business context", encoding="utf-8")
        self.assertEqual(p.read_text(), "private business context")
        self.assertTrue((self.project / ".venture/.gitignore").is_file())

    def test_workspace_dry_run(self):
        result = subprocess.run([sys.executable, str(INIT), "--project", str(self.project), "--dry-run"],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / ".venture").exists())

    def test_all_skill_links_resolve(self):
        skill = KIT / "venture-evaluator"
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+)\)", text)
        self.assertGreater(len(links), 5)
        for link in links:
            self.assertTrue((skill / link).is_file(), link)

    def test_model_eval_cases_are_valid_json(self):
        obj = json.loads((KIT / "venture-evaluator/evals/evals.json").read_text(encoding="utf-8"))
        self.assertEqual(obj["skill_name"], "venture-evaluator")
        self.assertEqual(len(obj["evals"]), 12)
        self.assertEqual(len({case["id"] for case in obj["evals"]}), 12)

    def test_shell_wrapper_runs_from_another_directory(self):
        if os.name == "nt":
            self.skipTest("POSIX wrapper")
        result = subprocess.run(["bash", str(KIT / "install.sh"), "--home", str(self.home), "--dry-run"],
                                cwd=self.project, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
