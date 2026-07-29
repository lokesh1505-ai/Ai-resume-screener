from fpdf import FPDF


def _clean(text):
    """FPDF's core fonts can't render some unicode characters (emoji, smart quotes).
    Strip anything outside the safe latin-1 range."""
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_report(
    filename,
    jd_match,
    semantic_match,
    ats_score,
    years_experience,
    matched_skills,
    strengths,
    weaknesses,
):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def write_line(text, size=11, bold=False, gap_before=0, gap_after=0):
        if gap_before:
            pdf.ln(gap_before)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("helvetica", "B" if bold else "", size)
        pdf.multi_cell(pdf.epw, 8, _clean(text))
        if gap_after:
            pdf.ln(gap_after)

    write_line("Resume Screening Report", size=16, bold=True, gap_after=4)

    write_line(f"File: {filename}")
    if jd_match is not None:
        write_line(f"JD Match (keyword-based): {jd_match}%")
    if semantic_match is not None:
        write_line(f"JD Match (AI/meaning-based): {semantic_match}%")
    write_line(f"ATS Score: {ats_score}/100")
    write_line(f"Years of Experience Detected: {years_experience}")
    write_line(f"Matched Skills: {', '.join(matched_skills) if matched_skills else 'None found'}")

    write_line("Strengths", size=13, bold=True, gap_before=4)
    for s in strengths:
        write_line(f"- {s}")

    write_line("Weaknesses", size=13, bold=True, gap_before=4)
    for w in weaknesses:
        write_line(f"- {w}")

    data = pdf.output()
    if isinstance(data, str):
        data = data.encode("latin-1")
    return bytes(data)
