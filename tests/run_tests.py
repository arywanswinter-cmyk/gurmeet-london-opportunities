#!/usr/bin/env python3
"""
Master E2E Test Runner for Gurmeet Kaur London Job Directory.
Executes Tiers 1-4 opaque-box verification test suite.

Usage:
  python3 tests/run_tests.py [options]

Options:
  --tier <1|2|3|4>        Run only tests in the specified tier
  --skip-network          Skip external live HTTP checks (faster offline execution)
  --json-report <path>    Output structured test execution results to JSON file
  -v, --verbose           Detailed output per test
  -h, --help              Show this help message
"""

import argparse
import datetime
import json
import os
import sys
import time
import unittest

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.test_tier1_features import TestTier1Features
from tests.test_tier2_boundaries import TestTier2Boundaries
from tests.test_tier3_cross_features import TestTier3CrossFeatures
from tests.test_tier4_scenarios import TestTier4Scenarios

TIER_MAP = {
    1: ("Tier 1 — Feature Coverage & Core Data Contract", TestTier1Features),
    2: ("Tier 2 — Boundary & Corner Cases", TestTier2Boundaries),
    3: ("Tier 3 — Cross-Feature Combinations & State Consistency", TestTier3CrossFeatures),
    4: ("Tier 4 — Real-World Scenarios & Deployment", TestTier4Scenarios),
}


class DetailedTestResult(unittest.TestResult):
    def __init__(self, stream=None, descriptions=None, verbosity=1):
        super().__init__(stream, descriptions, verbosity)
        self.verbosity = verbosity
        self.test_records = []

    def startTest(self, test):
        super().startTest(test)
        self._start_time = time.time()
        if self.verbosity > 1:
            desc = test.shortDescription() or test.id().split(".")[-1]
            sys.stdout.write(f"  • {desc} ... ")
            sys.stdout.flush()

    def addSuccess(self, test):
        super().addSuccess(test)
        duration = time.time() - self._start_time
        desc = test.shortDescription() or test.id().split(".")[-1]
        self.test_records.append({
            "id": test.id(),
            "name": desc,
            "status": "PASS",
            "duration": round(duration, 3),
            "message": None,
        })
        if self.verbosity > 1:
            sys.stdout.write(f"\033[92mPASS\033[0m ({duration:.2f}s)\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        duration = time.time() - self._start_time
        desc = test.shortDescription() or test.id().split(".")[-1]
        err_msg = str(err[1])
        self.test_records.append({
            "id": test.id(),
            "name": desc,
            "status": "FAIL",
            "duration": round(duration, 3),
            "message": err_msg,
        })
        if self.verbosity > 1:
            sys.stdout.write(f"\033[91mFAIL\033[0m ({duration:.2f}s)\n")

    def addError(self, test, err):
        super().addError(test, err)
        duration = time.time() - self._start_time
        desc = test.shortDescription() or test.id().split(".")[-1]
        err_msg = str(err[1])
        self.test_records.append({
            "id": test.id(),
            "name": desc,
            "status": "ERROR",
            "duration": round(duration, 3),
            "message": err_msg,
        })
        if self.verbosity > 1:
            sys.stdout.write(f"\033[91mERROR\033[0m ({duration:.2f}s)\n")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        duration = time.time() - self._start_time
        desc = test.shortDescription() or test.id().split(".")[-1]
        self.test_records.append({
            "id": test.id(),
            "name": desc,
            "status": "SKIP",
            "duration": round(duration, 3),
            "message": reason,
        })
        if self.verbosity > 1:
            sys.stdout.write(f"\033[93mSKIP\033[0m ({reason})\n")


def run_tier(tier_num: int, tier_name: str, test_class, verbosity: int = 1) -> DetailedTestResult:
    print(f"\n\033[1m[{tier_name}]\033[0m")
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    result = DetailedTestResult(verbosity=verbosity)
    suite.run(result)
    return result


def main():
    parser = argparse.ArgumentParser(description="Gurmeet London E2E Test Suite Runner")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], help="Run only specified tier (1-4)")
    parser.add_argument("--skip-network", action="store_true", help="Skip live HTTP network checks")
    parser.add_argument("--json-report", type=str, help="Path to write JSON test report")
    parser.add_argument("-v", "--verbose", action="store_true", default=True, help="Verbose test output")
    args = parser.parse_args()

    if args.skip_network:
        os.environ["SKIP_NETWORK"] = "1"

    tiers_to_run = [args.tier] if args.tier else [1, 2, 3, 4]

    print("=" * 72)
    print(" GURMEET KAUR LONDON OPPORTUNITIES DIRECTORY — E2E TEST SUITE")
    print(f" Timestamp: {datetime.datetime.utcnow().isoformat()}Z")
    print(f" Directory: {PROJECT_ROOT}")
    print(f" Tiers:     {tiers_to_run}")
    print(f" Network:   {'Disabled (--skip-network)' if args.skip_network else 'Enabled'}")
    print("=" * 72)

    overall_start = time.time()
    tier_results = {}
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_skipped = 0
    all_failures = []

    for t_num in tiers_to_run:
        name, cls = TIER_MAP[t_num]
        res = run_tier(t_num, name, cls, verbosity=2 if args.verbose else 1)
        tier_results[t_num] = res

        total_passed += (res.testsRun - len(res.failures) - len(res.errors) - len(res.skipped))
        total_failed += len(res.failures)
        total_errors += len(res.errors)
        total_skipped += len(res.skipped)

        for test, msg in res.failures:
            all_failures.append((f"Tier {t_num}", test, "FAIL", msg))
        for test, msg in res.errors:
            all_failures.append((f"Tier {t_num}", test, "ERROR", msg))

    total_time = time.time() - overall_start

    # Summary table
    print("\n" + "=" * 72)
    print(" SUITE EXECUTION SUMMARY")
    print("=" * 72)
    print(f"{'Tier':<10} {'Tests':<8} {'Passed':<8} {'Failed':<8} {'Errors':<8} {'Skipped':<8}")
    print("-" * 72)

    for t_num in tiers_to_run:
        r = tier_results[t_num]
        p = r.testsRun - len(r.failures) - len(r.errors) - len(r.skipped)
        print(f"Tier {t_num:<5} {r.testsRun:<8} {p:<8} {len(r.failures):<8} {len(r.errors):<8} {len(r.skipped):<8}")

    print("-" * 72)
    print(f"TOTAL      {total_passed + total_failed + total_errors + total_skipped:<8} {total_passed:<8} {total_failed:<8} {total_errors:<8} {total_skipped:<8}")
    print(f"Duration:  {total_time:.2f}s")

    # Detailed Failure Diagnostics
    if all_failures:
        print("\n" + "!" * 72)
        print(f" DETAILED FAILURE DIAGNOSTICS ({len(all_failures)} failure(s) detected)")
        print("!" * 72)
        for idx, (tier_label, test, status, msg) in enumerate(all_failures, 1):
            test_id = test.id() if hasattr(test, "id") else str(test)
            desc = test.shortDescription() if hasattr(test, "shortDescription") else ""
            print(f"\n[{idx}] {tier_label} :: {test_id}")
            if desc:
                print(f"    Description: {desc}")
            print(f"    Status: {status}")
            print("    Diagnostic Details:")
            for line in msg.strip().split("\n"):
                print(f"      {line}")
        print("\n" + "!" * 72)

    # Optional JSON report output
    if args.json_report:
        report_data = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "duration_seconds": round(total_time, 3),
            "summary": {
                "total": total_passed + total_failed + total_errors + total_skipped,
                "passed": total_passed,
                "failed": total_failed,
                "errors": total_errors,
                "skipped": total_skipped,
                "status": "PASS" if (total_failed == 0 and total_errors == 0) else "FAIL",
            },
            "tiers": {},
        }
        for t_num in tiers_to_run:
            r = tier_results[t_num]
            report_data["tiers"][f"tier_{t_num}"] = {
                "tests_run": r.testsRun,
                "passed": r.testsRun - len(r.failures) - len(r.errors) - len(r.skipped),
                "failed": len(r.failures),
                "errors": len(r.errors),
                "skipped": len(r.skipped),
                "records": r.test_records,
            }
        try:
            with open(args.json_report, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
            print(f"\nJSON report written to: {args.json_report}")
        except Exception as e:
            print(f"\nFailed to write JSON report: {e}")

    # Final verdict
    if total_failed == 0 and total_errors == 0:
        print("\n\033[92m✔ ALL TESTS PASSED SUCCESSFULLY (Exit code 0)\033[0m\n")
        sys.exit(0)
    else:
        print(f"\n\033[91m✘ SUITE FAILED with {total_failed} failure(s) and {total_errors} error(s) (Exit code 1)\033[0m\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
