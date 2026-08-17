#!/usr/bin/env python3
"""Regression battery for secret_scan.py. Run it after touching the patterns.

    python3 tools/test_secret_scan.py

Every "secret" here is fake and built by concatenation so that no realistic
credential literal ever sits in this repository.

The false-negative half (should NOT fire) matters as much as the other one. A
scanner that flags `token = makeTestToken(...)` in a note about a test helper
gets bypassed within a week, and then it protects nothing.
"""
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ss", HERE / "secret_scan.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)

CASES = [
    # (text, should_fire, label)
    ("AKIA" + "1234567890ABCDEF",              True,  "AWS access key id"),
    ("sk_live_" + "abcdefghij0123456789",      True,  "Stripe live key"),
    ("ghp_" + "a" * 36,                        True,  "GitHub token"),
    ("AIza" + "b" * 35,                        True,  "Google API key"),
    ("xoxb-" + "1234567890-abcdef",            True,  "Slack token"),
    ("-----BEGIN RSA PRIVATE KEY-----",        True,  "private key block"),
    ("api_key = '" + "R7fQ2mZk91xLpW4v" + "'", True,  "real assignment"),
    ("password=" + "Tr0ub4dor&3xyz",           True,  "real password"),

    ("`token = makeTestToken(...)`",            False, "function call, not a value"),
    ("const token = process.env.API_TOKEN",     False, "env reference"),
    ("API_KEY=${MY_KEY}",                       False, "shell variable"),
    ("password: <your-password>",               False, "angle-bracket placeholder"),
    ("api_key = {{API_KEY}}",                   False, "template placeholder"),
    ("token: changeme",                         False, "changeme"),
    ("secret: xxxxxx",                          False, "xxx filler"),
    ("password = password",                     False, "anchored placeholder"),
    ("The token expired and had to be renewed", False, "prose"),
]


def main():
    failed = 0
    for text, should_fire, label in CASES:
        fired = bool(list(ss.scan_text(text)))
        if fired != should_fire:
            failed += 1
            print(f"  FAIL  expected fire={should_fire}, got {fired}  — {label}")
    total = len(CASES)
    print(f"{total - failed}/{total} cases passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
