"""
Utility functions and data loaders for Gurmeet London Opportunities E2E Test Suite.
"""

import json
import math
import os
import re
import ssl
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INDEX_HTML_PATH = os.path.join(PROJECT_ROOT, "index.html")
DOSSIER_MD_PATH = os.path.join(PROJECT_ROOT, "gurmeet-london-application-pack.md")

IMPERIAL_WHARF = {
    "name": "Imperial Wharf (Home Base)",
    "postcode": "SW6 2ZH",
    "lat": 51.4752,
    "lng": -0.1831,
}

GREATER_LONDON_BOUNDS = {
    "lat_min": 51.28,
    "lat_max": 51.69,
    "lng_min": -0.51,
    "lng_max": 0.33,
}

EXPECTED_CATEGORIES = {
    "museum": 8,
    "arts": 8,
    "school": 8,
    "tutor": 8,
}
TOTAL_EXPECTED_JOBS = 32

COMMON_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

GENERIC_PATH_ENDINGS = {
    "careers",
    "careers/",
    "vacancies",
    "vacancies/",
    "jobs",
    "jobs/",
    "work-with-us",
    "work-with-us/",
    "work-at-the-museum",
    "work-at-the-museum/",
    "opportunities",
    "opportunities/",
    "work-for-us",
    "work-for-us/",
    "recruitment",
    "recruitment/",
    "info/careers",
    "info/careers/",
}


def load_jobs_from_index(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Extracts and parses the `const JOBS = [...]` array from index.html.
    """
    target = path or INDEX_HTML_PATH
    if not os.path.exists(target):
        raise FileNotFoundError(f"index.html not found at: {target}")

    with open(target, "r", encoding="utf-8") as f:
        content = f.read()

    # Look for const JOBS = [...]
    match = re.search(r"const\s+JOBS\s*=\s*(\[\s*\{.*?\}\s*\])\s*;", content, re.DOTALL)
    if not match:
        # Fallback broader search
        match = re.search(r"const\s+JOBS\s*=\s*(\[.*?\])\s*;", content, re.DOTALL)
    if not match:
        raise ValueError("Could not find `const JOBS = [...]` in index.html")

    raw_json = match.group(1)
    try:
        jobs = json.loads(raw_json)
        return jobs
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON in const JOBS: {e}")


def load_html_soup(path: Optional[str] = None) -> BeautifulSoup:
    """Loads index.html into a BeautifulSoup DOM tree."""
    target = path or INDEX_HTML_PATH
    with open(target, "r", encoding="utf-8") as f:
        return BeautifulSoup(f.read(), "html.parser")


def load_application_pack(path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Parses gurmeet-london-application-pack.md into structured sections per job ID.
    Returns:
        dict: {
            'mus-01': {
                'id': 'mus-01',
                'title': '...',
                'email_to': '...',
                'email_subject': '...',
                'email_body': '...',
                'cover_letter': '...',
                'raw_section': '...'
            }, ...
        }
    """
    target = path or DOSSIER_MD_PATH
    if not os.path.exists(target):
        raise FileNotFoundError(f"Dossier markdown file not found at: {target}")

    with open(target, "r", encoding="utf-8") as f:
        text = f.read()

    sections = re.split(r"\n###\s+\[([A-Za-z0-9_-]+)\]\s+", text)
    result = {}

    for i in range(1, len(sections), 2):
        item_id = sections[i].lower().strip()
        body = sections[i + 1]

        # Extract title line from first line of body
        first_line = body.split("\n", 1)[0].strip()
        title = first_line.lstrip("— ").strip()

        # Extract email draft fields
        email_to_match = re.search(r"\*\*To\*\*:\s*`([^`]+)`", body)
        email_to = email_to_match.group(1).strip() if email_to_match else ""

        email_sub_match = re.search(r"\*\*Subject\*\*:\s*`([^`]+)`", body)
        email_subject = email_sub_match.group(1).strip() if email_sub_match else ""

        # Extract text code blocks (first is email body, second is cover letter)
        code_blocks = re.findall(r"```text\s*\n(.*?)\n```", body, re.DOTALL)
        email_body = code_blocks[0].strip() if len(code_blocks) >= 1 else ""
        cover_letter = code_blocks[1].strip() if len(code_blocks) >= 2 else ""

        result[item_id] = {
            "id": item_id,
            "title": title,
            "email_to": email_to,
            "email_subject": email_subject,
            "email_body": email_body,
            "cover_letter": cover_letter,
            "raw_section": body,
        }

    return result


def haversine_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes Great Circle Distance in statute miles using standard Haversine formula.
    Radius of Earth = 3958.8 miles.
    """
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def is_generic_careers_url(url: str) -> bool:
    """
    Detects whether a URL points to a generic careers landing page or home page
    rather than a specific vacancy deep-link.
    """
    if not url:
        return True
    clean = url.strip()
    if clean.startswith("http://"):
        clean_path = clean[7:]
    elif clean.startswith("https://"):
        clean_path = clean[8:]
    else:
        return True

    # Strip domain
    parts = clean_path.split("/", 1)
    if len(parts) == 1 or not parts[1].strip() or parts[1].strip() == "/":
        return True  # Root domain only

    path_and_query = parts[1].lower().rstrip("/")
    path_only = path_and_query.split("?")[0]

    for generic in GENERIC_PATH_ENDINGS:
        generic_clean = generic.rstrip("/")
        if path_only == generic_clean or path_only.endswith("/" + generic_clean):
            return True

    return False


def check_url_http(url: str, timeout: int = 12) -> Tuple[int, str, Optional[str]]:
    """
    Performs HTTP GET on a URL with browser User-Agent and redirect following.
    Returns (status_code, final_url, error_message).
    """
    # Create unverified SSL context to avoid false failures on legacy root certs
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": COMMON_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return (resp.status, resp.geturl(), None)
    except urllib.error.HTTPError as e:
        return (e.code, url, str(e))
    except urllib.error.URLError as e:
        return (0, url, str(e.reason))
    except Exception as e:
        return (0, url, str(e))


def check_urls_concurrently(urls: List[str], max_workers: int = 8, timeout: int = 12) -> Dict[str, Tuple[int, str, Optional[str]]]:
    """
    Checks multiple URLs concurrently using a thread pool.
    Returns dict: url -> (status_code, final_url, error_message)
    """
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(check_url_http, u, timeout): u for u in urls}
        for future in as_completed(future_to_url):
            u = future_to_url[future]
            try:
                res = future.result()
                results[u] = res
            except Exception as e:
                results[u] = (0, u, str(e))
    return results
