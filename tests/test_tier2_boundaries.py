"""
Tier 2: Boundary & Corner Cases Tests
Verifies:
- Geolocation coordinates strictly within Greater London bounds (lat 51.28–51.69, lng -0.51–0.33)
- London postcode format validity
- Commute format strictly matches `<X> min — <route description>`
- Application dossier text boundary limits (cover letter >= 300 chars, email 50–1500 chars)
- Tailoring integrity (references to Gurmeet Kaur's background, no placeholder tokens)
- Text escaping and special character preservation (£, —, smart quotes)
"""

import re
import unittest
from typing import List
from tests.test_utils import (
    load_jobs_from_index,
    GREATER_LONDON_BOUNDS,
)

LONDON_POSTCODE_PREFIXES = (
    "SW", "W", "WC", "EC", "NW", "N", "E", "SE",
    "KT", "TW", "CR", "BR", "HA", "UB", "EN", "IG", "RM", "DA"
)

BACKGROUND_KEYWORDS = (
    "GURMEET", "MUSEUMS VICTORIA", "LSE", "LONDON SCHOOL OF ECONOMICS",
    "POETRY", "CREATIVE WRITING", "HISTORY", "INTERNATIONAL RELATIONS",
    "TEACHING", "EDUCATION", "CURATORIAL", "THREADS", "CULTURE MAKERS"
)

PLACEHOLDER_TOKENS = (
    "[TODO]", "[INSERT", "[TBD]", "TBD", "XXX", "YOUR COMPANY",
    "[NAME]", "[ORGANIZATION]", "<INSERT"
)


class TestTier2Boundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = load_jobs_from_index()

    def test_geolocation_within_greater_london_bounds(self):
        """Tier 2.1: Verify all 32 coordinates are strictly within Greater London boundary box."""
        out_of_bounds = []
        lat_min = GREATER_LONDON_BOUNDS["lat_min"]
        lat_max = GREATER_LONDON_BOUNDS["lat_max"]
        lng_min = GREATER_LONDON_BOUNDS["lng_min"]
        lng_max = GREATER_LONDON_BOUNDS["lng_max"]

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            lat = job.get("lat")
            lng = job.get("lng")

            if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
                out_of_bounds.append(f"[{jid}] Non-numeric lat/lng: lat={lat}, lng={lng}")
                continue

            if not (lat_min <= lat <= lat_max) or not (lng_min <= lng <= lng_max):
                out_of_bounds.append(
                    f"[{jid}] ({lat}, {lng}) outside Greater London [{lat_min}..{lat_max}, {lng_min}..{lng_max}]"
                )

        self.assertFalse(
            out_of_bounds,
            f"Found {len(out_of_bounds)} out-of-bounds coordinates:\n  " + "\n  ".join(out_of_bounds),
        )

    def test_london_postcode_format(self):
        """Tier 2.2: Verify all venue postcodes are valid Greater London postcodes."""
        invalid_postcodes = []
        postcode_pattern = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$", re.IGNORECASE)

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            pc = job.get("postcode", "").strip().upper()

            if not pc or not postcode_pattern.match(pc):
                invalid_postcodes.append(f"[{jid}] Invalid postcode format: '{pc}'")
                continue

            if not any(pc.startswith(prefix) for prefix in LONDON_POSTCODE_PREFIXES):
                invalid_postcodes.append(f"[{jid}] Postcode '{pc}' does not start with a recognized London outward prefix")

        self.assertFalse(
            invalid_postcodes,
            f"Found {len(invalid_postcodes)} invalid postcodes:\n  " + "\n  ".join(invalid_postcodes),
        )

    def test_commute_format_and_duration_bounds(self):
        """Tier 2.3: Verify transit strictly matches '<X> min — <route description>'."""
        commute_pattern = re.compile(r"^(\d+)\s*min\s*[—–-]\s*(.+)$")
        invalid_commutes = []

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            transit = job.get("transit", "").strip()

            match = commute_pattern.match(transit)
            if not match:
                invalid_commutes.append(f"[{jid}] Does not match '<X> min — <route>': '{transit}'")
                continue

            duration_min = int(match.group(1))
            route_desc = match.group(2).strip()

            # Boundary: commute must be between 4 and 90 minutes
            if not (4 <= duration_min <= 90):
                invalid_commutes.append(
                    f"[{jid}] Commute duration {duration_min} min out of realistic bounds [4..90]: '{transit}'"
                )

            # Check that route description mentions transit mode or lines
            transit_modes = ("overground", "line", "bus", "rail", "walk", "cycle", "train", "underground")
            if not any(mode in route_desc.lower() for mode in transit_modes):
                invalid_commutes.append(
                    f"[{jid}] Commute description lacks recognizable transit mode: '{route_desc}'"
                )

        self.assertFalse(
            invalid_commutes,
            f"Found {len(invalid_commutes)} non-compliant transit routes:\n  " + "\n  ".join(invalid_commutes),
        )

    def test_cover_letter_length_and_tailoring(self):
        """Tier 2.4: Verify cover letters are substantial (>300 chars) and tailored to Gurmeet's background."""
        letter_issues = []

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            letter = job.get("cover_letter", "").strip()

            if len(letter) < 300:
                letter_issues.append(
                    f"[{jid}] Cover letter too short ({len(letter)} chars, minimum 300)"
                )
                continue

            letter_upper = letter.upper()
            matched_keywords = [kw for kw in BACKGROUND_KEYWORDS if kw in letter_upper]
            if len(matched_keywords) < 2:
                letter_issues.append(
                    f"[{jid}] Cover letter lacks sufficient Gurmeet background references (found: {matched_keywords})"
                )

        self.assertFalse(
            letter_issues,
            f"Found {len(letter_issues)} cover letter quality issues:\n  " + "\n  ".join(letter_issues),
        )

    def test_email_body_length_and_contact_format(self):
        """Tier 2.5: Verify outreach email body is concise (50–1500 chars) and email_to is valid."""
        email_issues = []
        email_regex = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            body = job.get("email_body", "").strip()
            to = job.get("email_to", "").strip()
            subject = job.get("email_subject", "").strip()

            if not (50 <= len(body) <= 1500):
                email_issues.append(
                    f"[{jid}] Email body length ({len(body)} chars) out of bounds [50..1500]"
                )

            if not to or (not email_regex.match(to) and not to.startswith("http")):
                email_issues.append(f"[{jid}] Invalid email_to format: '{to}'")

            if len(subject) < 10:
                email_issues.append(f"[{jid}] Subject line too short: '{subject}'")

        self.assertFalse(
            email_issues,
            f"Found {len(email_issues)} email body/contact issues:\n  " + "\n  ".join(email_issues),
        )

    def test_no_placeholder_tokens(self):
        """Tier 2.6: Verify zero unfinished placeholder tokens in any job fields."""
        tokens_found = []

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            for field, val in job.items():
                if isinstance(val, str):
                    val_upper = val.upper()
                    for token in PLACEHOLDER_TOKENS:
                        if token in val_upper:
                            tokens_found.append(f"[{jid}] Field '{field}' contains placeholder token '{token}'")

        self.assertFalse(
            tokens_found,
            f"Found {len(tokens_found)} placeholder tokens:\n  " + "\n  ".join(tokens_found),
        )

    def test_text_encoding_and_character_fidelity(self):
        """Tier 2.7: Verify currency symbols (£), em-dashes (—), and quotes are intact without encoding corruption."""
        encoding_issues = []
        corrupt_patterns = ("&amp;amp;", "&quot;", "\\u00", "â\x80\x94", "Â£", "Ã©")

        for job in self.jobs:
            jid = job.get("id", "UNKNOWN")
            for field in ("title", "org", "salary_display", "transit", "cover_letter", "email_body"):
                val = str(job.get(field, ""))
                for pat in corrupt_patterns:
                    if pat in val:
                        encoding_issues.append(f"[{jid}] Field '{field}' contains double-encoded or corrupted sequence '{pat}'")

        self.assertFalse(
            encoding_issues,
            f"Found {len(encoding_issues)} text encoding fidelity issues:\n  " + "\n  ".join(encoding_issues),
        )


if __name__ == "__main__":
    unittest.main()
