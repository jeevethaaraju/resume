from flask import Flask, request, jsonify
from flask_cors import CORS
from pdfminer.high_level import extract_text
from docx import Document
import os
import re

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_resume_text(file):
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    if filename.endswith(".pdf"):
        text = extract_text(file_path)
    elif filename.endswith(".docx"):
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        text = ""

    # Delete the file after reading (optional)
    os.remove(file_path)
    return text

def score_resume(text):
    score = 0
    text_lower = text.lower()

    # Skills
    skills = ["python", "java", "sql", "teamwork", "communication", "leadership"]
    for skill in skills:
        if skill in text_lower:
            score += 10

    # Education
    if re.search(r"|spm|master|phd|degree|bachelor|diploma|university", text_lower):
        score += 10

    # Experience
    if "experience" in text_lower:
        score += 20

    # Projects
    if "project" in text_lower:
        score += 10

    remarks = "Strong resume" if score >= 60 else "Needs improvement"
    return score, remarks

@app.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    text = extract_resume_text(file)
    score, remarks = score_resume(text)
    return jsonify({"score": score, "remarks": remarks})

if __name__ == "__main__":
    app.run(debug=True)
