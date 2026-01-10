<h1 align="center" id="title">Resume-Analyzer</h1>

<p align="center"><img src="https://socialify.git.ci/chidvi123/AI_Resume_Analyzer/image?language=1&amp;name=1&amp;owner=1&amp;theme=Dark" alt="project-image"></p>


### AI Resume Analyzer

AI Resume Analyzer is a production-ready Streamlit application that analyzes resumes using explainable, rule-based logic and semantic similarity techniques. It provides users with structured resume insights such as skill extraction, experience estimation, resume scoring, job-role matching, and learning recommendations, while offering administrators advanced analytics, resume deduplication, similarity search, and clustering powered by persisted embeddings in MongoDB.

## Key Features

### User Features
- Upload resumes in PDF format with in-app preview
- Automatic resume text extraction using PDF parsing
- Dictionary-based skill extraction with normalization and aliases
- Rule-based experience level detection
- Explainable resume quality scoring with detailed breakdown
- Job role selection and semantic job match scoring
- Skill gap analysis against role-specific requirements
- Curated course and interview preparation recommendations
- Duplicate resume detection using semantic hashing
- Resume analysis persisted for analytics
- User feedback submission with rating and comments
- Feedback data persisted in MongoDB for admin analysis
- About page with contact message submission
- Contact messages stored in MongoDB for review


### Admin Features
- Secure admin access with session-based authentication
- Event-based analytics stored in MongoDB
- Experience-level and role-wise performance insights
- Global and role-specific missing skills analysis
- Resume similarity search using stored embeddings
- KMeans-based resume clustering for internal analysis
- Cluster-level insights for grouped resumes
- CSV export of analytics data


## System Architecture

The application follows a strict modular architecture with a clear separation between the frontend, backend logic, and data persistence layers.

- **Frontend (Streamlit)**  
  Handles routing, navigation, and user interaction. Application entry and navigation are centralized in `app/main.py`, while user-facing and admin-facing logic are isolated into dedicated view modules.

- **Backend (Python)**  
  All core logic is implemented in the `backend/` directory and organized by responsibility, including resume parsing, analysis, NLP processing, recommendations, and database access.

- **Database (MongoDB)**  
  MongoDB is used as the primary persistence layer. Resumes are stored as deduplicated entities, while analytics are stored as event-based records linked to resumes. This design enables scalable analytics without duplicating resume data.

- **Intelligence Layer**  
  Lightweight NLP techniques are used for semantic similarity, resume deduplication, and clustering. Sentence embeddings are stored in the database to support similarity search and admin-only clustering workflows.

## Technology Stack

- **Frontend**: Streamlit  
- **Backend**: Python  
- **Database**: MongoDB  
- **NLP**: SentenceTransformers (all-MiniLM-L6-v2)  
- **PDF Parsing**: pdfminer  
- **Similarity & Clustering**: Cosine Similarity, KMeans  
- **Visualization**: Streamlit charts  
- **Environment Management**: Python environment variables  

## Project Structure
<details>
<summary>Click to expand project structure</summary>

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
│   │   ├── resume_parser.py
│   │   └── pdf_reader.py
│   │
│   ├── nlp/
│   │   ├── embeddings.py
│   │   ├── similarity.py
│   │   ├── skill_extractor.py
│   │   └── job_matcher.py
│   │
│   ├── recommender/
│   │   ├── skill_recommender.py
│   │   ├── course_recommender.py
│   │   └── tips.py
│   │
│   ├── analysis/
│   │   ├── resume_score.py
│   │   ├── experience_level.py
│   │   └── clustering.py
│   │
│   ├── database/
│   │   ├── db.py
│   │   ├── user_data.py
│   │   └── feedback_data.py
│   │
│   └── utils/
│       ├── helpers.py
│       └── constants.py
│
├── data/
│   ├── courses.json
│   ├── skills.json
│   └── samples/
│
├── Uploaded_Resumes/
├── README.md
├── requirements.txt
└── .gitignore
```
</details>


## Data Model Overview

<details>
<summary>Model overview</summary>
The system uses a clear separation between core entities and event-based analytics to ensure data integrity, scalability, and meaningful insights.

### Resume (Entity)
- Each resume is stored **once** as a unique entity.
- Duplicate resumes are detected using a semantic hash generated from normalized resume text.
- Resume records store:
  - Parsed resume data
  - Semantic embedding
  - Cluster identifier (admin analytics)
- This prevents redundant storage and enables reuse across analytics and intelligence layers.

### Analytics (Events)
- Analytics are stored as **event-based records**.
- Each resume analysis generates a new analytics event linked via `resume_id`.
- Analytics records include:
  - Experience level
  - Resume score
  - Target role
  - Job match score
  - Skill presence and gaps
  - Timestamp
- This design supports historical tracking and trend analysis without duplicating resume data.

This entity–event separation allows the system to scale analytics independently while keeping resume intelligence centralized and consistent.
</details>

### Installation Steps

1. Clone the repository

   ```bash
   git clone https://github.com/your-username/AI_Resume_Analyzer.git
   cd AI_Resume_Analyzer
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate   # Windows

3. Install dependencies:
    ```bash
    pip install -r requirements.txt

4. Run the application:
    ```bash
    steamlit run app/main.py


## Current Status

- Core user-facing resume analysis is complete and feature-locked.
- Admin analytics, resume similarity, and clustering are fully implemented and stable.
- Resume data is deduplicated and persisted in MongoDB.
- Analytics are stored as event-based records for historical insights.
- The application is deployment-ready and compatible with Streamlit Cloud.


## Future Scope

- MongoDB Atlas integration for cloud deployment.
- Job Description (JD) analysis and resume–JD comparison.
- Cluster-level insights to identify common strengths and gaps across resumes.
- Advanced admin visualizations for long-term trend analysis.
- Optional resume feedback export for users.

### Preview

#### Home Page
<p align="center">
  <img src="docs/screenshots/home1.png" width="900">
  <img src="docs/screenshots/home2.png" width="900">
</p>
