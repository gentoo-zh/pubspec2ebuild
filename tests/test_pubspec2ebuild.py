import io
import pathlib
import unittest
from contextlib import redirect_stdout
from unittest import mock

import yaml

import pubspec2ebuild as p2e

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def run(*argv):
    out = io.StringIO()
    with mock.patch("sys.argv", ["pubspec2ebuild", *argv]), redirect_stdout(out):
        p2e.main()
    return out.getvalue()


class Workspace(unittest.TestCase):
    def test_arrays_match_golden(self):
        got = run(str(FIXTURES / "workspace.lock"))
        self.assertEqual(got, (FIXTURES / "workspace.expected").read_text())

    def test_path_packages_need_no_distfile(self):
        packages = p2e.load_packages(FIXTURES / "workspace.lock")
        self.assertNotIn("localsend_isolates", packages)

    def test_urls(self):
        got = run("--urls", str(FIXTURES / "workspace.lock")).splitlines()
        self.assertEqual(got, [
            "https://pub.dev/api/archives/args-2.6.0.tar.gz",
            "https://pub.dev/api/archives/path-1.9.0.tar.gz",
            "https://github.com/Seidko/flutter-plugins/archive/58748dae405df5e68a131e4905d48e75d0624be2.tar.gz",
            "https://github.com/rustdesk-org/uni_links/archive/f416118d843a7e9ed117c7bb7bdc2deda5a9e86f.tar.gz",
        ])


class Rejections(unittest.TestCase):
    def packages(self, **override):
        packages = p2e.load_packages(FIXTURES / "workspace.lock")
        for name, changes in override.items():
            packages[name]["description"].update(changes)
        return packages

    def test_other_registry_is_rejected(self):
        with self.assertRaises(SystemExit):
            p2e.hosted_packages(self.packages(args={"url": "https://pub.example.org"}))

    def test_missing_sha256_is_rejected(self):
        packages = self.packages()
        del packages["args"]["description"]["sha256"]
        with self.assertRaises(KeyError):
            p2e.hosted_packages(packages)

    def test_non_github_git_is_rejected(self):
        with self.assertRaises(SystemExit):
            p2e.git_packages(self.packages(uni_links={"url": "https://gitlab.com/x/y"}))

    def test_unknown_source_is_ignored(self):
        packages = self.packages()
        packages["args"]["source"] = "sdk"
        self.assertEqual(p2e.hosted_packages(packages), [
            ("path", "1.9.0", "087ce49c3f0dc39180befefc60fdb4acd8f8620e5682fe2476afd0b3688bb4af"),
        ])
