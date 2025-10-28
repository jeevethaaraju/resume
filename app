from flask import Flask, request, jsonify
from pdfminer.high_level import extract_text
from docx import Document
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # ✅ create folder if not exists

def extract_resume_text(filepath):
    """Extract text from PDF or DOCX file"""
    text = ""
    if filepath.endswith(".pdf"):
        text = extract_text(filepath)
    elif filepath.endswith(".docx"):
        doc = Document(filepath)
        text = "\n".join([p.text for p in doc.paragraphs])
    return text


def score_resume(text):
    """Score resume based on keywords"""
    score = 0
    text_lower = text.lower()

    # ✅ Skill keywords
    skills = ['python', 'java', 'sql', 'teamwork', 'communication', 'leadership']
    for skill in skills:
        if skill in text_lower:
            score += 10

    # ✅ Education
    if re.search(r"degree|bachelor|diploma|university", text_lower):
        score += 10

    # ✅ Experience
    if "experience" in text_lower:
        score += 20

    # ✅ Projects
    if "project" in text_lower:
        score += 10

    remarks = "Strong resume" if score >= 60 else "Needs improvement"
    return score, remarks


@app.route("/upload", methods=["POST"])
def upload_resume():
    """Handle uploaded resume"""
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # ✅ Save file to uploads folder
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # ✅ Extract and score text
    text = extract_resume_text(filepath)
    score, remarks = score_resume(text)

    # ✅ Optionally delete file after reading
    # os.remove(filepath)

    return jsonify({"score": score, "remarks": remarks})


if __name__ == "__main__":
    app.run(debug=True)
