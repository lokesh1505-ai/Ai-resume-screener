import re
from datetime import datetime
from dateutil import parser as dateparser

MONTH = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)

DATE_TOKEN = rf"(?:{MONTH}\s+\d{{4}}|\d{{4}})"

DATE_RANGE_PATTERN = re.compile(
    rf"({DATE_TOKEN})\s*(?:-|–|—|to)\s*({DATE_TOKEN}|Present|Current|Now)",
    re.IGNORECASE,
)

EXPLICIT_PATTERN = re.compile(
    r"(\d+)\+?\s*(?:years|yrs)\s*(?:of\s+)?experience", re.IGNORECASE
)

# Section headers used to identify and exclude non-work sections (like Education)
# from the date-range scan, so degree years don't get counted as work experience.
SECTION_KEYWORDS = [
    "experience", "work history", "employment",
    "education", "academic",
    "skills", "technical skills", "core competencies",
    "projects", "personal projects",
    "summary", "objective", "profile",
    "certifications", "certification", "awards", "achievements", "highlights",
]

_HEADING_PATTERN = re.compile(
    r"(?im)^[ \t]*(" + "|".join(re.escape(k) for k in SECTION_KEYWORDS) + r")\b.*$"
)

# Sections whose dates should NOT count toward work experience
_EXCLUDED_SECTIONS = {"education", "academic"}


def _strip_excluded_sections(text):
    """Removes text under headers like 'Education' so degree years aren't
    mistaken for work experience."""
    matches = list(_HEADING_PATTERN.finditer(text))
    if not matches:
        return text

    ranges_to_remove = []
    for i, m in enumerate(matches):
        heading = m.group(1).lower()
        if heading in _EXCLUDED_SECTIONS:
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            ranges_to_remove.append((start, end))

    if not ranges_to_remove:
        return text

    ranges_to_remove.sort()
    kept = []
    last_end = 0
    for start, end in ranges_to_remove:
        if start > last_end:
            kept.append(text[last_end:start])
        last_end = max(last_end, end)
    kept.append(text[last_end:])
    return "".join(kept)


def _parse_token(token):
    token = token.strip()
    if token.lower() in ("present", "current", "now"):
        return datetime.today()
    try:
        return dateparser.parse(token, default=datetime(1900, 1, 1))
    except Exception:
        return None


def extract_years_experience(text):
    """
    Returns total years of work experience as a float.
    Prefers an explicit statement like '3+ years experience' if present,
    otherwise sums up date ranges found in work-related sections only
    (Education dates are excluded so degree duration isn't counted).
    """
    explicit = EXPLICIT_PATTERN.findall(text.lower())
    if explicit:
        return float(max(int(m) for m in explicit))

    work_text = _strip_excluded_sections(text)

    total_months = 0
    seen = set()
    for start_tok, end_tok in DATE_RANGE_PATTERN.findall(work_text):
        key = (start_tok.lower(), end_tok.lower())
        if key in seen:
            continue
        seen.add(key)

        start_date = _parse_token(start_tok)
        end_date = _parse_token(end_tok)
        if not start_date or not end_date or end_date < start_date:
            continue

        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        if 0 < months < 600:  # sanity cap at 50 years for one range
            total_months += months

    return round(total_months / 12, 1)
