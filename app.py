import streamlit as st
import tempfile
import os
fromparser import extract_text
fromscreener import rank_resumes
fromats_analyzer import analyze_resume
fromsemantic_matcher import load_model, semantic_similarity
fromreport_generator import generate_report

st.set_page_config(page_title="AI Resume Screener", layout="wide")
st.title("🤖 AI Resume Screening System")

st.sidebar.header("Job Description")
jd_text = st.sidebar.text_area("Paste the job description here", height=250)

skills_input = st.sidebar.text_input(
    "Required skills (comma-separated)", "Python, SQL, Machine Learning"
)
skill_list = [s.strip() for s in skills_input.split(",") if s.strip()]

use_ai_matching = st.sidebar.checkbox(
    "Use AI meaning-based matching (slower, more accurate)", value=True
)

st.header("Upload Resumes")
uploaded_files = st.file_uploader(
    "Upload resumes (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)


@st.cache_resource
def get_semantic_model():
    return load_model()


if st.button("Screen Resumes"):
    if not jd_text.strip():
        st.warning("Please paste a job description first.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        resumes_dict = {}
        with st.spinner("Extracting text from resumes..."):
            for file in uploaded_files:
                suffix = os.path.splitext(file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(file.read())
                    tmp_path = tmp.name
                try:
                    resumes_dict[file.name] = extract_text(tmp_path)
                except Exception as e:
                    st.error(f"Could not read {file.name}: {e}")
                finally:
                    os.remove(tmp_path)

        with st.spinner("Scoring resumes..."):
            results = rank_resumes(resumes_dict, jd_text, skill_list)

            model = None
            if use_ai_matching:
                with st.spinner("Loading AI matching model (first run only, may take a minute)..."):
                    model = get_semantic_model()

            for r in results:
                if model is not None:
                    r["semantic_score"] = semantic_similarity(
                        jd_text, resumes_dict[r["filename"]], model
                    )
                    r["combined_score"] = round(
                        (r["similarity_score"] + r["semantic_score"]) / 2, 2
                    )
                else:
                    r["semantic_score"] = None
                    r["combined_score"] = r["similarity_score"]

            results.sort(key=lambda x: x["combined_score"], reverse=True)

        st.success(f"Screened {len(results)} resumes")
        st.subheader("Ranked Results")

        for i, r in enumerate(results, 1):
            ats = analyze_resume(resumes_dict[r["filename"]], skill_list)
            header = f"#{i} — {r['filename']} — Match: {r['combined_score']}% — ATS Score: {ats['ats_score']}/100"
            with st.expander(header):
                st.write(f"**Keyword-based JD match:** {r['similarity_score']}%")
                if r["semantic_score"] is not None:
                    st.write(f"**AI meaning-based JD match:** {r['semantic_score']}%")
                    st.write(f"**Combined match score:** {r['combined_score']}%")
                st.write(f"**ATS Score:** {ats['ats_score']}/100")
                st.write(f"**Years of experience detected:** {r['years_experience']}")
                if "matched_skills" in r:
                    matched = ", ".join(r["matched_skills"]) if r["matched_skills"] else "None found"
                    st.write(f"**Matched skills ({r['skill_match_pct']}%):** {matched}")

                st.markdown("**✅ Strengths**")
                for s in ats["strengths"]:
                    st.markdown(f"- {s}")

                st.markdown("**⚠️ Weaknesses**")
                for w in ats["weaknesses"]:
                    st.markdown(f"- {w}")

                with st.expander("Detailed breakdown"):
                    st.write(f"Word count: {ats['word_count']}")
                    st.write(f"Contact info found: {ats['contact_info']}")
                    st.write(f"Sections found: {ats['sections_found']}")
                    st.write(f"Quantified achievements: {ats['quantified_achievements']}")
                    st.write(f"Action verbs used: {', '.join(ats['action_verbs_found']) if ats['action_verbs_found'] else 'None'}")

                pdf_bytes = generate_report(
                    filename=r["filename"],
                    jd_match=r["similarity_score"],
                    semantic_match=r["semantic_score"],
                    ats_score=ats["ats_score"],
                    years_experience=r["years_experience"],
                    matched_skills=r.get("matched_skills", []),
                    strengths=ats["strengths"],
                    weaknesses=ats["weaknesses"],
                )
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"{os.path.splitext(r['filename'])[0]}_report.pdf",
                    mime="application/pdf",
                    key=f"download_{i}",
                )
