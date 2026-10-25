"""
Tier 1: Feature Coverage & Core Data Contract Tests
Verifies:
- 32 job records in index.html `const JOBS`
- Exact 8/8/8/8 category distribution (museum, arts, school, tutor)
- Direct vacancy deep-link structure (zero generic homepages or /careers landing hubs)
- Live HTTP 200 deep-link reachability
- Explicit closing dates / deadlines present for all 32 listings
- Verified salary/grade present for all 32 listings
- 32 matching sections in gurmeet-london-application-pack.md
"""

import os
import re
import unittest
from typing import Dict, List, Any
from tests.test_utils import (
    load_jobs_from_index,
    load_application_pack,
    is_generic_careers_url,
    check_urls_concurrently,
    EXPECTED_CATEGORIES,
    TOTAL_EXPECTED_JOBS,
)


class TestTier1Features(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = load_jobs_from_index()
        cls.dossier = load_application_pack()
        cls.skip_network = os.environ.get("SKIP_NETWORK", "").lower() in ("1", "true", "yes")

    def test_total_job_count_is_32(self):
        """Tier 1.1: Verify exactly 32 job records exist in const JOBS."""
        actual_count = len(self.jobs)
        self.assertEqual(
            actual_count,
            TOTAL_EXPECTED_JOBS,
            f"Expected exactly {TOTAL_EXPECTED_JOBS} jobs in const JOBS, but found {actual_count}.",
        )

    def test_exact_category_distribution_8_8_8_8(self):
        """Tier 1.2: Verify exact 8/8/8/8 distribution across 4 core sectors."""
        counts: Dict[str, int] = {}
        for job in self.jobs:
            cat = job.get("category", "MISSING")
            counts[cat] = counts.get(cat, 0) + 1

        mismatches = []
        for cat, expected in EXPECTED_CATEGORIES.items():
            actual = counts.get(cat, 0)
            if actual != expected:
                mismatches.append(f"category '{cat}': expected {expected}, found {actual}")

        # Check for unexpected extra categories
        extra_cats = set(counts.keys()) - set(EXPECTED_CATEGORIES.keys())
        if extra_cats:
            mismatches.append(f"unexpected categories found: {extra_cats}")

        self.assertFalse(
            mismatches,
            "Category distribution mismatch (required 8/8/8/8):\n  " + "\n  ".join(mismatches),
        )

    def test_all_deep_links_structure_non_generic(self):
        """Tier 1.3: Verify all 32 apply_url entries are direct deep-links (no generic careers portals)."""
        generic_links = []
        invalid_urls = []

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            url = job.get("apply_url", "").strip()

            if not url or not (url.startswith("http://") or url.startswith("https://")):
                invalid_urls.append(f"[{jid}] Invalid URL format: '{url}'")
                continue

            if is_generic_careers_url(url):
                generic_links.append(f"[{jid}] Generic career portal detected: {url}")

        errors = invalid_urls + generic_links
        self.assertFalse(
            errors,
            f"Found {len(errors)} non-compliant apply_url entries:\n  " + "\n  ".join(errors),
        )

    def test_all_deep_links_http_200(self):
        """Tier 1.4: Verify all 32 direct vacancy URLs are live and return HTTP 200."""
        if self.skip_network:
            self.skipTest("Network test skipped via SKIP_NETWORK environment variable.")

        urls = [j.get("apply_url") for j in self.jobs if j.get("apply_url")]
        url_to_job = {j.get("apply_url"): j.get("id") for j in self.jobs}

        results = check_urls_concurrently(urls, max_workers=8, timeout=12)

        failures = []
        for url, (status, final_url, err) in results.items():
            jid = url_to_job.get(url, "UNKNOWN")
            # 200 OK is expected.
            # Some ATS portals return 403 to automated scrapers (Cloudflare / bot protections).
            # If 403, we flag it clearly.
            if status != 200:
                failures.append(
                    f"[{jid}] URL {url} returned HTTP {status} (final: {final_url}, err: {err})"
                )

        self.assertFalse(
            failures,
            f"{len(failures)} out of {len(urls)} job URLs failed live HTTP check:\n  "
            + "\n  ".join(failures),
        )

    def test_explicit_deadlines_present_and_valid(self):
        """Tier 1.5: Verify every listing has an explicit closing date / deadline."""
        missing_deadlines = []
        iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            deadline = job.get("deadline")

            if not deadline or str(deadline).strip().upper() in ("", "TBD", "NONE", "NULL", "TODO"):
                missing_deadlines.append(f"[{jid}] Missing or empty deadline field")
                continue

            deadline_str = str(deadline).strip()
            # If formatted as ISO YYYY-MM-DD, verify it is a future/active date (2025+)
            if iso_pattern.match(deadline_str):
                year = int(deadline_str[:4])
                if year < 2025:
                    missing_deadlines.append(
                        f"[{jid}] Deadline '{deadline_str}' has expired year (<2025)"
                    )
            elif len(deadline_str) < 5:
                missing_deadlines.append(
                    f"[{jid}] Deadline '{deadline_str}' is too short or ambiguous"
                )

        self.assertFalse(
            missing_deadlines,
            f"Found {len(missing_deadlines)} listings without verified active deadlines:\n  "
            + "\n  ".join(missing_deadlines),
        )

    def test_verified_salary_and_remuneration_present(self):
        """Tier 1.6: Verify every listing has verified salary_display and positive salary_sort."""
        salary_issues = []

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            sal_disp = job.get("salary_display")
            sal_sort = job.get("salary_sort")

            if not sal_disp or not isinstance(sal_disp, str) or not sal_disp.strip():
                salary_issues.append(f"[{jid}] Missing or empty salary_display")
            elif "£" not in sal_disp and not any(term in sal_disp.upper() for term in ("MPS", "UPS", "GRADE", "SCALE", "COMPETITIVE")):
                salary_issues.append(f"[{jid}] salary_display '{sal_disp}' missing currency or recognized grade")

            if sal_sort is None or not isinstance(sal_sort, (int, float)) or sal_sort <= 0:
                salary_issues.append(f"[{jid}] Invalid salary_sort: {sal_sort} (must be positive number)")

        self.assertFalse(
            salary_issues,
            f"Found {len(salary_issues)} salary formatting or sorting issues:\n  "
            + "\n  ".join(salary_issues),
        )

    def test_application_pack_sections_count(self):
        """Tier 1.7: Verify gurmeet-london-application-pack.md has 32 dossier sections."""
        actual_count = len(self.dossier)
        self.assertEqual(
            actual_count,
            TOTAL_EXPECTED_JOBS,
            f"Expected {TOTAL_EXPECTED_JOBS} dossier sections in markdown pack, found {actual_count}.",
        )


if __name__ == "__main__":
    unittest.main()
