# AI Resume Analyzer

A Streamlit-based application that analyzes resumes to extract key details
and classify experience levels as **Fresher**, **Intermediate**, or **Experienced**.

---

## 📁 Project Structure

```text
ai_resume_analyzer/
│
├── app/                         # Streamlit UI layer
│   ├── main.py                  # Main Streamlit entry point
│   ├── pages/                   # Multiple Streamlit pages
│   │   ├── user.py
│   │   ├── admin.py
│   │   ├── feedback.py
│   │   └── about.py
│   ├── assets/                  # Logos, images
│   └── components/              # UI helper components
│
├── backend/                     # All backend logic
│   ├── parser/
│   │   ├── resume_parser.py     # NLP resume parsing
│   │   └── pdf_reader.py        # PDF → text extraction
│   │
│   ├── nlp/
│   │   ├── embeddings.py        # SentenceTransformer embeddings
│   │   ├── similarity.py        # Cosine similarity & scoring
│   │   ├── skill_extractor.py   # Skill extraction & cleanup
│   │   └── job_matcher.py       # Job-role compatibility
│   │
│   ├── recommender/
│   │   ├── skill_recommender.py # Missing-skill recommendations
│   │   ├── course_recommender.py# Course mapping from JSON
│   │   └── tips.py              # Resume tips / rewrite logic
│   │
│   ├── analysis/
│   │   ├── resume_score.py      # Heuristic resume scoring
│   │   ├── experience_level.py  # Fresher / Intermediate / Experienced
│   │   └── clustering.py        # Resume clustering (admin analytics)
│   │
│   ├── database/
│   │   ├── db.py                # Database connection
│   │   ├── user_data.py         # User data operations
│   │   └── feedback_data.py     # Feedback handling
│   │
│   └── utils/
│       ├── helpers.py
│       └── constants.py
│
├── data/
│   ├── courses.json             # Course dataset
│   ├── skills.json              # Master skill list
│   └── samples/                 # Sample resumes for testing
│
├── logs/                        # Application logs (optional)
│
├── docs/                        # Documentation & diagrams
│   ├── architecture.png
│   ├── flowchart.png
│   └── final_report.pdf
│
├── Uploaded_Resumes/            # Uploaded resumes (gitignored)
│
├── README.md
├── requirements.txt
└── .gitignore


<p align="center"> <img src="docs/ScreenShots/ProjectStructure.png" alt="Project Structure Diagram" width="850" /> </p>