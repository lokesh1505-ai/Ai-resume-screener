# AI Resume Screening System

Ranks resumes against a job description using TF-IDF + cosine similarity,
plus simple skill and experience extraction.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

This opens a browser UI where you:
1. Paste the job description in the sidebar
2. List required skills (comma-separated)
3. Upload one or more resumes (PDF, DOCX, or TXT)
4. Click "Screen Resumes" to see a ranked list with match %, matched skills,
   and detected years of experience

## How it works

- `utils/parser.py` — extracts raw text from PDF/DOCX/TXT files
- `utils/screener.py` — cleans text, builds TF-IDF vectors for the JD and
  each resume, and scores similarity with cosine similarity. Also does
  regex-based skill matching and experience-year extraction
- `app.py` — Streamlit front end tying it together

## Next steps to level this up

- Swap TF-IDF for embeddings (`sentence-transformers`, e.g. `all-MiniLM-L6-v2`)
  for semantic matching instead of keyword overlap
- Use spaCy NER or a resume-parsing library (e.g. `pyresparser`) to pull out
  structured fields: education, job titles, companies
- Add a weighted scoring formula (e.g. 50% similarity + 30% skills + 20%
  experience) instead of ranking by similarity alone
- Store results in a database and add a "shortlist" / feedback loop so the
  system can learn from recruiter decisions
- Add bias checks — audit whether the model is picking up on
  proxies for age, gender, or name origin
