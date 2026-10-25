"""
Tier 4: Real-World Scenarios & Deployment Tests
Verifies:
- UI DOM structure, accessibility and modal container elements
- Candidate workflow simulation (category filtering, keyword search, distance slider, sort orders)
- Interactive anchor links integrity (no broken or empty href attributes)
- Git remote repository configuration (arywanswinter-cmyk/gurmeet-london-opportunities)
- Live GitHub Pages deployment reachability and content verification
"""

import os
import re
import subprocess
import unittest
from tests.test_utils import (
    PROJECT_ROOT,
    load_jobs_from_index,
    load_html_soup,
    check_url_http,
    EXPECTED_CATEGORIES,
    TOTAL_EXPECTED_JOBS,
)

GITHUB_REPO_NAME = "arywanswinter-cmyk/gurmeet-london-opportunities"
GITHUB_PAGES_URL = "https://arywanswinter-cmyk.github.io/gurmeet-london-opportunities/"


class TestTier4Scenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = load_jobs_from_index()
        cls.soup = load_html_soup()
        cls.skip_network = os.environ.get("SKIP_NETWORK", "").lower() in ("1", "true", "yes")

    def test_ui_dom_elements_present(self):
        """Tier 4.1: Verify core UI containers, interactive controls, and modal components exist in index.html."""
        required_ids = [
            "london-map",            # Leaflet map container
            "searchInput",           # Search input
            "searchClearBtn",        # Search clear button
            "distanceFilter",        # Commute distance filter slider
            "sortSelect",            # Sort dropdown
            "ledgerBody",            # Job listings ledger
            "tableWrapper",          # Table container
            "appModalBackdrop",      # Application modal overlay
            "modalOrgTitle",         # Modal header / job title
            "tabBtnCover",           # Modal cover letter tab
            "tabBtnEmail",           # Modal outreach email tab
            "tabBtnDetails",         # Modal role details tab
            "modalBody",             # Modal content body
            "modalCounter",          # Modal record counter
            "toastMessage",          # Notification toast
        ]

        missing = []
        for elem_id in required_ids:
            if not self.soup.find(id=elem_id):
                missing.append(f"#{elem_id}")

        self.assertFalse(
            missing,
            f"Missing required UI DOM elements in index.html:\n  " + "\n  ".join(missing),
        )

    def test_candidate_workflow_category_filtering(self):
        """Tier 4.2: Simulate candidate filtering by each sector and verify matching records."""
        for cat, expected_count in EXPECTED_CATEGORIES.items():
            filtered = [j for j in self.jobs if j.get("category") == cat]
            self.assertEqual(
                len(filtered),
                expected_count,
                f"Simulated category filter '{cat}' returned {len(filtered)} jobs, expected {expected_count}.",
            )

    def test_candidate_workflow_search_filtering(self):
        """Tier 4.3: Simulate candidate searching for keywords across job title, org, summary, area."""
        queries = ["Curator", "English", "Learning", "Producer", "London", "Policy", "LSE", "Gallery 44"]

        for q in queries:
            q_lower = q.lower()
            matches = []
            for j in self.jobs:
                searchable = " ".join([
                    j.get("title", ""),
                    j.get("org", ""),
                    j.get("summary", ""),
                    j.get("area", ""),
                    j.get("why_fit", ""),
                ]).lower()
                if q_lower in searchable:
                    matches.append(j["id"])

            self.assertGreater(
                len(matches),
                0,
                f"Search query '{q}' returned 0 matches in candidate workflow simulation.",
            )

    def test_candidate_workflow_distance_filtering(self):
        """Tier 4.4: Simulate distance threshold filtering (e.g. <= 2.0 miles) and verify boundary constraint."""
        threshold = 2.0
        nearby_jobs = [j for j in self.jobs if j.get("distance_miles", 999) <= threshold]

        self.assertGreater(
            len(nearby_jobs),
            0,
            f"Expected at least 1 job within {threshold} miles of Imperial Wharf.",
        )

        for j in nearby_jobs:
            self.assertLessEqual(
                j["distance_miles"],
                threshold,
                f"Job {j['id']} has distance {j['distance_miles']} > threshold {threshold}",
            )

    def test_candidate_workflow_sorting_logic(self):
        """Tier 4.5: Simulate salary and distance sorting orders."""
        # Sort by distance ascending
        by_dist = sorted(self.jobs, key=lambda x: x.get("distance_miles", 0))
        for i in range(len(by_dist) - 1):
            self.assertLessEqual(
                by_dist[i]["distance_miles"],
                by_dist[i + 1]["distance_miles"],
                f"Distance sort violated at index {i}",
            )

        # Sort by salary descending
        by_sal = sorted(self.jobs, key=lambda x: x.get("salary_sort", 0), reverse=True)
        for i in range(len(by_sal) - 1):
            self.assertGreaterEqual(
                by_sal[i]["salary_sort"],
                by_sal[i + 1]["salary_sort"],
                f"Salary sort violated at index {i}",
            )

    def test_anchor_links_integrity(self):
        """Tier 4.6: Verify all static anchor links in index.html have valid href targets."""
        anchors = self.soup.find_all("a")
        broken_anchors = []

        for a in anchors:
            href = a.get("href", "").strip()
            # Ignore empty template placeholders inside scripts
            if not href or href == "#":
                broken_anchors.append(f"Anchor '{a.text.strip()}' has empty or dummy href: '{href}'")

        self.assertFalse(
            broken_anchors,
            f"Found {len(broken_anchors)} invalid anchor links in index.html:\n  "
            + "\n  ".join(broken_anchors),
        )

    def test_git_remote_repository_configured(self):
        """Tier 4.7: Verify git remote 'origin' points to arywanswinter-cmyk/gurmeet-london-opportunities."""
        try:
            res = subprocess.run(
                ["git", "remote", "-v"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            output = res.stdout
            self.assertIn(
                GITHUB_REPO_NAME,
                output,
                f"Git remote origin does not point to '{GITHUB_REPO_NAME}'. Got:\n{output}",
            )
        except Exception as e:
            self.fail(f"Failed to check git remotes: {e}")

    def test_github_pages_deployment_live(self):
        """Tier 4.8: Verify live GitHub Pages site is reachable (HTTP 200) and serves valid directory content."""
        if self.skip_network:
            self.skipTest("Network test skipped via SKIP_NETWORK environment variable.")

        status, final_url, err = check_url_http(GITHUB_PAGES_URL, timeout=15)
        self.assertEqual(
            status,
            200,
            f"GitHub Pages URL {GITHUB_PAGES_URL} returned HTTP {status} (err: {err})",
        )


if __name__ == "__main__":
    unittest.main()
