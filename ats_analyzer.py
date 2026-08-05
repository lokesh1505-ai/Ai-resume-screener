import re
from experience_parser import extract_years_experience as _extract_years_experience


ACTION_VERBS = [
    "achieved", "built", "created", "designed", "developed", "engineered",
    "implemented", "improved", "increased", "reduced", "launched", "led",
    "managed", "optimized", "resolved", "streamlined", "delivered",
    "automated", "architected", "spearheaded", "generated", "cut",
    "raised", "shipped", "drove", "collaborated", "maintained", "solved",
]

SECTION_HEADERS = {
    "experience": ["experience", "work history", "employment"],
    "education": ["education", "academic"],
    "skills": ["skills", "technical skills", "core competencies"],
    "projects": ["projects", "personal projects"],
    "summary": ["summary", "objective", "profile"],
}

BUZZWORDS = [
    "team player", "hard worker", "go-getter", "results-driven",
    "detail-oriented", "self-starter", "think outside the box",
    "synergy", "dynamic", "passionate", "guru", "ninja", "rockstar",
]


def has_contact_info(text):
    email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))
    phone = bool(re.search(r"(\+?\d[\d\-\s()]{8,}\d)", text))
    linkedin = "linkedin.com" in text.lower()
    return {"email": email, "phone": phone, "linkedin": linkedin}


def detect_sections(text):
    text_lower = text.lower()
    found = {}
    for section, keywords in SECTION_HEADERS.items():
        found[section] = any(kw in text_lower for kw in keywords)
    return found


def count_quantified_achievements(text):
    # numbers, percentages, currency, multipliers (e.g. "2x", "50%", "$10k")
    matches = re.findall(r"(\d+%|\$\d+[kKmM]?|\d+x\b|\b\d{2,}\+?\b)", text)
    return len(matches)


def count_action_verbs(text):
    text_lower = text.lower()
    found = [v for v in ACTION_VERBS if re.search(rf"\b{v}\b", text_lower)]
    return found


def count_buzzwords(text):
    text_lower = text.lower()
    return [b for b in BUZZWORDS if b in text_lower]


def word_count(text):
    return len(text.split())


def analyze_resume(text, skill_list=None):
    contact = has_contact_info(text)
    sections = detect_sections(text)
    quantified = count_quantified_achievements(text)
    action_verbs_found = count_action_verbs(text)
    buzzwords_found = count_buzzwords(text)
    wc = word_count(text)

    score = 0
    max_score = 100
    strengths = []
    weaknesses = []

    # Contact info (15 pts)
    contact_score = sum(contact.values()) / 3 * 15
    score += contact_score
    if contact["email"] and contact["phone"]:
        strengths.append("Contact info (email + phone) is present and easy for recruiters/ATS to find.")
    else:
        weaknesses.append("Missing email or phone number — make sure both are clearly visible near the top.")
    if not contact["linkedin"]:
        weaknesses.append("No LinkedIn URL detected — adding one gives recruiters an easy way to learn more about you.")

    # Section structure (20 pts)
    section_score = sum(sections.values()) / len(sections) * 20
    score += section_score
    missing_sections = [s for s, present in sections.items() if not present]
    if not missing_sections:
        strengths.append("All standard resume sections (summary, experience, education, skills, projects) are present.")
    else:
        weaknesses.append(f"Missing or unclear section(s): {', '.join(missing_sections)}. Use clear headers so ATS parsers can categorize your content correctly.")

    # Quantified achievements (20 pts)
    quant_score = min(quantified / 8, 1) * 20
    score += quant_score
    if quantified >= 5:
        strengths.append(f"Strong use of quantified results ({quantified} numbers/metrics found) — this makes impact concrete and credible.")
    elif quantified >= 2:
        weaknesses.append("Some quantified achievements present, but adding more (%, counts, time saved, revenue impact) would strengthen your bullet points.")
    else:
        weaknesses.append("Very few numbers or metrics found. Recruiters and ATS scoring favor quantified impact — e.g. 'reduced processing time by 40%' instead of 'improved processing time'.")

    # Action verbs (20 pts)
    verb_score = min(len(action_verbs_found) / 8, 1) * 20
    score += verb_score
    if len(action_verbs_found) >= 6:
        strengths.append(f"Good variety of strong action verbs used ({len(action_verbs_found)} found), making bullet points feel active and outcome-focused.")
    else:
        weaknesses.append("Limited variety of action verbs. Start bullet points with strong verbs like 'built', 'led', 'optimized', 'automated' instead of passive phrasing.")

    # Length check (10 pts)
    if 350 <= wc <= 900:
        score += 10
        strengths.append(f"Resume length ({wc} words) is in a good range — concise but detailed enough for ATS and human readers.")
    elif wc < 350:
        score += 5
        weaknesses.append(f"Resume seems short ({wc} words). Consider adding more detail to experience or projects if you're leaving out relevant work.")
    else:
        score += 5
        weaknesses.append(f"Resume is on the longer side ({wc} words). Consider trimming to the most relevant, high-impact points — aim for 1 page early career, up to 2 pages max.")

    # Buzzwords (10 pts, deduct if present)
    if buzzwords_found:
        score += max(10 - len(buzzwords_found) * 3, 0)
        weaknesses.append(f"Contains generic buzzwords ({', '.join(buzzwords_found)}) that add little value — replace with specific, evidence-backed statements.")
    else:
        score += 10
        strengths.append("No generic buzzwords/filler phrases detected — language stays specific and evidence-based.")

    # Skill match bonus (5 pts, only if skill_list given)
    if skill_list:
        text_lower = text.lower()
        matched = [s for s in skill_list if s.lower() in text_lower]
        skill_pct = len(matched) / len(skill_list) if skill_list else 0
        score += skill_pct * 5
        if skill_pct >= 0.7:
            strengths.append(f"Strong keyword coverage for target role ({len(matched)}/{len(skill_list)} required skills found).")
        elif skill_pct > 0:
            weaknesses.append(f"Only {len(matched)}/{len(skill_list)} target skills found in the resume — consider adding missing ones if you have that experience.")
        else:
            weaknesses.append("None of the target skills were found as exact keyword matches — this could hurt ATS keyword matching even if you have the underlying experience.")

    score = round(min(score, max_score), 1)

    return {
        "ats_score": score,
        "word_count": wc,
        "contact_info": contact,
        "sections_found": sections,
        "quantified_achievements": quantified,
        "action_verbs_found": action_verbs_found,
        "buzzwords_found": buzzwords_found,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }
