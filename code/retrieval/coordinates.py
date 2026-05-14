"""
Extract geographic coordinate references from Dutch engineering document text.

Handles:
- Road + hectometer references  (e.g. "N338 hm 15.3", "N338 15+300")
- RD coordinate pairs           (Rijksdriehoek, e.g. X: 195430  Y: 431820)
"""

import math
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import json as _json

# ── Road + hectometer ────────────────────────────────────────────────────────

# Dutch road designations: N338, A2, S101, R4, etc.
_ROAD = r"([NASRB]\d{1,4})"

# Hectometer expressed as:
#   hm 15.3  |  km 15,3  |  15+300  |  15.300  |  15,300
_HM_PATTERNS = [
    r"(?:hm|km)[\s:]*(\d{1,3})[.,](\d{1,3})",   # hm 15.3
    r"(\d{1,3})\+(\d{3})\b",                      # 15+300
]

_ROAD_HM_RE = re.compile(
    _ROAD + r"[\s,;/\\-]*(?:" + "|".join(_HM_PATTERNS) + r")",
    re.IGNORECASE,
)


def _hm_to_float(groups: tuple) -> float | None:
    """Convert regex groups to a single hectometer float."""
    # groups depends on which alternative matched; filter out None
    parts = [g for g in groups if g is not None]
    if len(parts) >= 2:
        try:
            return float(parts[0]) + float(parts[1]) / 1000.0
        except ValueError:
            pass
    return None


def extract_road_refs(text: str) -> list[dict]:
    """Return list of {road, hm} dicts found in text."""
    refs: list[dict] = []
    for m in _ROAD_HM_RE.finditer(text):
        road = m.group(1).upper()
        hm = _hm_to_float(m.groups()[1:])
        if hm is not None:
            refs.append({"road": road, "hm": round(hm, 3)})
    return refs


# ── RD coordinates ───────────────────────────────────────────────────────────

# RD valid ranges: X 0–300 000, Y 289 000–629 000
# Accept numbers with optional thousands-dot (Dutch notation): 195.430 → 195430
_RD_RE = re.compile(
    r"\bX[=:\s]+(\d{1,3}(?:[.,]\d{3})?)\b"
    r"[\s,;]*"
    r"\bY[=:\s]+(\d{1,3}(?:[.,]\d{3})?)\b",
    re.IGNORECASE,
)


def _rd_int(s: str) -> int:
    """Parse '195.430' or '195430' to 195430."""
    return int(s.replace(".", "").replace(",", ""))


def _valid_rd(x: int, y: int) -> bool:
    return 0 <= x <= 300_000 and 289_000 <= y <= 629_000


def extract_rd_coords(text: str) -> list[dict]:
    """Return list of {x, y} RD coordinate dicts found in text."""
    coords: list[dict] = []
    for m in _RD_RE.finditer(text):
        x = _rd_int(m.group(1))
        y = _rd_int(m.group(2))
        if _valid_rd(x, y):
            coords.append({"x": x, "y": y})
    return coords


# ── Combined ─────────────────────────────────────────────────────────────────

def extract_coordinates(text: str) -> dict:
    return {
        "road_refs": extract_road_refs(text),
        "rd_coords": extract_rd_coords(text),
    }


# ── Place name geocoding via PDOK Locatieserver ───────────────────────────────

_PDOK_URL = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"


def geocode_place(name: str) -> tuple[int, int] | None:
    """
    Resolve a Dutch place name to RD coordinates using the PDOK Locatieserver.

    Returns (x, y) in RD metres, or None if nothing was found.
    """
    params = urllib.parse.urlencode({"q": name, "rows": 1, "fl": "centroide_rd"})
    url = f"{_PDOK_URL}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = _json.loads(resp.read())
        docs = data.get("response", {}).get("docs", [])
        if not docs:
            return None
        centroid = docs[0].get("centroide_rd", "")
        # Format: "POINT(195430.123 431820.456)"
        m = re.match(r"POINT\(([0-9.]+)\s+([0-9.]+)\)", centroid)
        if not m:
            return None
        x, y = int(float(m.group(1))), int(float(m.group(2)))
        if _valid_rd(x, y):
            return x, y
    except (urllib.error.URLError, KeyError, ValueError) as exc:
        print(f"[WARN] Geocoding failed for '{name}': {exc}", file=sys.stderr)
    return None


def rd_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """Euclidean distance in metres between two RD points."""
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
