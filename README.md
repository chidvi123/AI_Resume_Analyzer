# AI Resume Analyzer

A Streamlit-based application that analyzes resumes to extract details
and classify experience levels (Fresher / Intermediate / Experienced).

---

## 📁 Project Structure

```text
ai_resume_analyzer/
│
├── app/                    # Streamlit UI
│   └── main.py
│
├── backend/                # Core logic
│   ├── parser/             # PDF & resume parsing
│   ├── analysis/           # Experience detection, scoring
│   └── utils/              # Helper functions
│
├── data/                   # Skills & datasets
│
├── docs/                   # Documentation & screenshots
│
├── Uploaded_Resumes/       # Stored resumes (gitignored)
│
├── README.md
└── requirements.txt
