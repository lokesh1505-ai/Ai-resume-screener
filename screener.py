import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.experience_parser import extract_years_experience


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text, skill_list):
    text_lower = text.lower()
    return [skill for skill in skill_list if skill.lower() in text_lower]


def score_resume(resume_text, jd_text, skill_list=None):
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([jd_clean, resume_clean])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    result = {
        "similarity_score": round(similarity * 100, 2),
        "years_experience": extract_years_experience(resume_text),
    }

    if skill_list:
        matched = extract_skills(resume_text, skill_list)
        result["matched_skills"] = matched
        result["skill_match_pct"] = round(len(matched) / len(skill_list) * 100, 2)

    return result


def rank_resumes(resumes_dict, jd_text, skill_list=None):
    """resumes_dict: {filename: resume_text}"""
    results = []
    for filename, text in resumes_dict.items():
        score = score_resume(text, jd_text, skill_list)
        score["filename"] = filename
        results.append(score)

    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results
