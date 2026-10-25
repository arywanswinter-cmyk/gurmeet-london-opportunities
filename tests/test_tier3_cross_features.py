"""
Tier 3: Cross-Feature Combinations & State Consistency Tests
Verifies:
- Haversine distance parity between calculated distance from Imperial Wharf (51.4752, -0.1831) and distance_miles
- Modal tab content parity: index.html cover_letter and email_body match gurmeet-london-application-pack.md
- Category counter badges in index.html match actual dataset counts (8/8/8/8 and 32 total)
- Job ID schema consistency (mus-01..08, art-01..08, sch-01..08, tut-01..08) and uniqueness
"""

import re
import unittest
from tests.test_utils import (
    load_jobs_from_index,
    load_application_pack,
    load_html_soup,
    haversine_distance_miles,
    IMPERIAL_WHARF,
    EXPECTED_CATEGORIES,
    TOTAL_EXPECTED_JOBS,
)


class TestTier3CrossFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = load_jobs_from_index()
        cls.dossier = load_application_pack()
        cls.soup = load_html_soup()

    def test_imperial_wharf_haversine_distance_parity(self):
        """Tier 3.1: Verify distance_miles matches mathematical Haversine distance from Imperial Wharf (tolerance 0.25 mi)."""
        iw_lat = IMPERIAL_WHARF["lat"]
        iw_lng = IMPERIAL_WHARF["lng"]
        discrepancies = []

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            lat = job.get("lat")
            lng = job.get("lng")
            recorded_dist = job.get("distance_miles")

            if recorded_dist is None or not isinstance(recorded_dist, (int, float)):
                discrepancies.append(f"[{jid}] Missing or non-numeric distance_miles: {recorded_dist}")
                continue

            calc_dist = haversine_distance_miles(iw_lat, iw_lng, lat, lng)
            diff = abs(calc_dist - recorded_dist)

            if diff > 0.25:
                discrepancies.append(
                    f"[{jid}] Recorded distance {recorded_dist} mi differs from Haversine {calc_dist:.2f} mi by {diff:.3f} mi"
                )

        self.assertFalse(
            discrepancies,
            f"Found {len(discrepancies)} distance calculation discrepancies:\n  "
            + "\n  ".join(discrepancies),
        )

    def test_modal_cover_letter_dossier_parity(self):
        """Tier 3.2: Verify modal cover_letter in index.html exactly matches markdown application pack."""
        mismatches = []

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN").lower()
            html_letter = job.get("cover_letter", "").strip()

            if jid not in self.dossier:
                mismatches.append(f"[{jid}] Job ID not found in markdown application pack")
                continue

            md_letter = self.dossier[jid].get("cover_letter", "").strip()

            # Normalize line endings and whitespace for cross-platform comparison
            norm_html = re.sub(r"\r\n", "\n", html_letter).strip()
            norm_md = re.sub(r"\r\n", "\n", md_letter).strip()

            if norm_html != norm_md:
                mismatches.append(
                    f"[{jid}] Cover letter mismatch between index.html ({len(norm_html)} chars) and dossier ({len(norm_md)} chars)"
                )

        self.assertFalse(
            mismatches,
            f"Found {len(mismatches)} cover letter parity mismatches:\n  " + "\n  ".join(mismatches),
        )

    def test_modal_email_body_dossier_parity(self):
        """Tier 3.3: Verify modal email_body in index.html exactly matches markdown application pack."""
        mismatches = []

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN").lower()
            html_email = job.get("email_body", "").strip()

            if jid not in self.dossier:
                mismatches.append(f"[{jid}] Job ID not found in markdown application pack")
                continue

            md_email = self.dossier[jid].get("email_body", "").strip()

            norm_html = re.sub(r"\r\n", "\n", html_email).strip()
            norm_md = re.sub(r"\r\n", "\n", md_email).strip()

            if norm_html != norm_md:
                mismatches.append(
                    f"[{jid}] Email body mismatch between index.html ({len(norm_html)} chars) and dossier ({len(norm_md)} chars)"
                )

        self.assertFalse(
            mismatches,
            f"Found {len(mismatches)} email body parity mismatches:\n  " + "\n  ".join(mismatches),
        )

    def test_category_counter_badges_in_html(self):
        """Tier 3.4: Verify category count badges in index.html DOM match actual job distribution."""
        badge_ids = {
            "museum": "count-museum",
            "arts": "count-arts",
            "school": "count-school",
            "tutor": "count-tutor",
            "policy": "count-policy",
            "uni": "count-uni",
        }

        # Calculate actual counts from JOBS
        actual_counts = {}
        for job in self.jobs:
            c = job.get("category", "")
            actual_counts[c] = actual_counts.get(c, 0) + 1

        badge_mismatches = []

        # Check total count badge
        all_badge = self.soup.find(id="count-all")
        if not all_badge:
            badge_mismatches.append("Missing element #count-all in index.html")
        else:
            text = all_badge.text.strip()
            if text != str(TOTAL_EXPECTED_JOBS):
                badge_mismatches.append(
                    f"#count-all badge shows '{text}', expected '{TOTAL_EXPECTED_JOBS}'"
                )

        # Check sector badges
        for cat, badge_id in badge_ids.items():
            elem = self.soup.find(id=badge_id)
            expected = EXPECTED_CATEGORIES[cat]
            if not elem:
                badge_mismatches.append(f"Missing element #{badge_id} in index.html")
            else:
                text = elem.text.strip()
                if text != str(expected):
                    badge_mismatches.append(
                        f"#{badge_id} badge shows '{text}', expected '{expected}'"
                    )

        self.assertFalse(
            badge_mismatches,
            f"Category counter badge errors in index.html DOM:\n  " + "\n  ".join(badge_mismatches),
        )

    def test_job_id_schema_and_uniqueness(self):
        """Tier 3.5: Verify 50 unique job IDs following strict schema prefix format."""
        ids = [j.get("id") for j in self.jobs]
        self.assertEqual(len(ids), len(set(ids)), f"Duplicate job IDs detected: {ids}")

        id_pattern = re.compile(r"^(mus|art|sch|tut|gov|uni)-\d{2}$")
        invalid_ids = [jid for jid in ids if not jid or not id_pattern.match(jid)]

        self.assertFalse(
            invalid_ids,
            f"Job IDs not matching schema (mus-01..08, art-01..08, sch-01..08, tut-01..08, gov-01..09, uni-01..09): {invalid_ids}",
        )


if __name__ == "__main__":
    unittest.main()
