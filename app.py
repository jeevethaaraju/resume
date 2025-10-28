import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from pdfminer.high_level import extract_text
from docx import Document

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def extract_resume_text(file):
    """
    Save the uploaded file temporarily, extract text, then delete the file.
    Supports PDF and DOCX.
    """
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    text = ""
    if filename.endswith(".pdf"):
        try:
            text = extract_text(file_path)
        except Exception as e:
            print(f"Error extracting PDF: {e}")
    elif filename.endswith(".docx"):
        try:
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print(f"Error extracting DOCX: {e}")

    os.remove(file_path)
    return text


def score_resume(text):
    """
    Score resume based on keywords in different categories.
    Returns total score, remarks, and breakdown.
    """
    text_lower = text.lower()
    breakdown = {
        "Technical Skills": 0,
        "Education": 0,
        "Experience": 0,
        "Projects": 0,
        "Soft Skills": 0
    }

    # Technical Skills
    tech_skills = ["python", "java", "html", "css", "sql", "javascript", "c++", "php"]
    tech_hits = sum(skill in text_lower for skill in tech_skills)
    breakdown["Technical Skills"] = min(tech_hits * 5, 35)

    # Education
    if re.search(r"spm|degree|bachelor|diploma|university|master|phd", text_lower):
        breakdown["Education"] = 15

    # Experience
    if "experience" in text_lower:
        breakdown["Experience"] = 20

    # Projects
    if "project" in text_lower:
        breakdown["Projects"] = 15

    # Soft Skills
    soft_skills = ["teamwork", "communication", "leadership", "creativity", "problem-solving"]
    soft_hits = sum(skill in text_lower for skill in soft_skills)
    breakdown["Soft Skills"] = min(soft_hits * 5, 15)

    total_score = sum(breakdown.values())
    remarks = "Excellent Resume" if total_score >= 70 else "Needs Improvement"

    return total_score, remarks, breakdown


@app.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    text = extract_resume_text(file)
    score, remarks, breakdown = score_resume(text)

    return jsonify({
        "score": score,
        "remarks": remarks,
        "breakdown": breakdown
    })


if __name__ == "__main__":
    # Use Render's port or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

