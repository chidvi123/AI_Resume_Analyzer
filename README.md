# AI Resume Analyzer

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

▶️ How to Run the Project
# Create virtual environment
python -m venv venv

# Activate environment
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app/main.py