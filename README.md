<h1 align="center" id="title">Resume-Analyzer</h1>

<p align="center"><img src="https://socialify.git.ci/chidvi123/AI_Resume_Analyzer/image?language=1&amp;name=1&amp;owner=1&amp;theme=Dark" alt="project-image"></p>

<p align="center">
  <a href="#project-structure">Project Structure</a> •
  <a href="#preview">Preview</a> •
  <a href="#Author">Contact</a>
</p>


### AI Resume Analyzer

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://ai-resume-analyzer-tgwj3qjq8wnj3rf9dzappua.streamlit.app/)

AI Resume Analyzer is a production-ready Streamlit application that analyzes resumes using explainable, rule-based logic and semantic similarity techniques. It provides users with structured resume insights such as skill extraction, experience estimation, resume scoring, job-role matching, and learning recommendations, while offering administrators advanced analytics, resume deduplication, similarity search, and clustering powered by persisted embeddings in MongoDB.

## Key Features

### User Features
- Upload resumes in PDF format with in-app preview
- Automatic resume text extraction using PDF parsing
- AI-powered skill extraction using Groq (Llama 3) for context-aware parsing
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
- Secure role-based authentication (Login & Register) with bcrypt password hashing
- User and Admin roles — Admin page hidden from regular users
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

<h2 id="project-structure">Project Structure</h2>

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

<h2 id="preview" align="center">Preview</h2>
<hr>

#### Home Page
<p align="center">
  <img src="docs/screenshots/home1.png" width="900">
  <img src="docs/screenshots/home2.png" width="900">
</p>

### User Page
<p align="center">
  <img src="docs/screenshots/navbar_and_user_inf.png" width="900">
  <img src="docs/screenshots/preview.png" width="900">
</p>

## Resume Summary, Score, and Breakdown with Target Role Selection

<p align="center">
  <img src="docs/screenshots/resume_target_job_role.png" width="900">
</p>

## Skill Gap Analysis & Job Match Score

<p align="center">
  <img src="docs/screenshots/skill_gap_resume_score.png" width="900">
</p>


### Skill Development & Career Support

<!-- Overview -->
<p align="center">
  <img src="docs/screenshots/recomendations.png" width="900">
</p>

<!-- Full width -->
<p align="center">
  <img src="docs/screenshots/recom1.png" width="900">
</p>

<!-- Side by side -->
<p align="center">
  <img src="docs/screenshots/recom2.png" width="45%">
  <img src="docs/screenshots/recom3.png" width="45%">
</p>


### Admin Page & Insights

## Admin Login (Password Required)
<p align="center">
  <img src="docs/screenshots/admin_password_inf.png" width="45%">
  <img src="docs/screenshots/incorrect_paddword.png" width="45%">
</p>

## Admin Dashboard Overview
<p align="center">
  <img src="docs/screenshots/system_overview.png" width="900">
</p>

## User Ratings and Rating Distribution

<p align="center">
  <img src="docs/screenshots/rating_chart.png" width="900">
</p>

## Missing Skills (Overall and Role-wise)

<p align="center">
  <img src="docs/screenshots/admin_insights.png" width="900">
</p>

<p align="center">
  <img src="docs/screenshots/ingights.png" width="900">
</p>

## Resume and Role Distributions
<p align="center">
  <img src="docs/screenshots/distributions1.png" width="900">
  <img src="docs/screenshots/distribution2.png" width="900">
</p>

## Resume Similarity Analysis
<p align="center">
  <img src="docs/screenshots/resume_similarity.png" width="900">
</p>

## Resume Clustering Based on Admin-Selected Number of Clusters
<p align="center">
  <img src="docs/screenshots/clustering1.png" width="900">
  <img src="docs/screenshots/clustering2.png" width="900">
</p>

## Download Analytics Data
<p align="center">
  <img src="docs/screenshots/download_analytics.png" width="900">
</p>

### Feedback Page

<p align="center">
  <img src="docs/screenshots/feedback1.png" width="900">
  <img src="docs/screenshots/feedback2.png" width="900">
</p>


###  About and Contact Page

<p align="center">
  <img src="docs/screenshots/contact.png" width="900">
</p>

## Conclusion

AI Resume Analyzer is a fully functional, modular resume analysis system designed with scalability, explainability, and real-world usability in mind.  
The project demonstrates practical applications of NLP, analytics, and system design using Streamlit and MongoDB.

<h2 id="author">Author</h2>

Developed by **Chidvilas**


📧 Email: [palarpachidvilas2419@gmail.com](mailto:palarpachidvilas2419@gmail.com) 

## Contributions

Contributions, suggestions, and feedback are welcome.  
Feel free to open an issue or submit a pull request.

## 📊 System Architecture & Flow Diagrams

# AI Resume Analyzer — Diagrams

---

## 1. Authentication Gate

```mermaid
flowchart TD
    A([User Opens App]) --> B{session_state\nlogged_in?}
    B -- ❌ False --> C[Show Login Page\napp/views/login.py]
    B -- ✅ True --> D[Show Sidebar\n+ Navigation]
    C --> E{Login or Register?}
    E -- Login --> F[verify_user\nauth.py]
    E -- Register --> G[register_user\nauth.py]
    F --> H[(MongoDB\nusers collection)]
    G --> H
    H -- bcrypt match --> I[Set session_state\nlogged_in=True\nrole=user/admin]
    H -- no match --> J[Show Error]
    G -- new user --> K[bcrypt hash\nstore in DB\nAuto-login]
    K --> I
    I --> D
```

---

## 2. Role-Based Navigation

```mermaid
flowchart LR
    A[Logged In User] --> B{role?}
    B -- user --> C[🏠 Home\n👤 User\n💬 Feedback\nℹ️ About]
    B -- admin --> D[🏠 Home\n👤 User\n💬 Feedback\nℹ️ About\n🛠️ Admin]
    C --> E[app/views/home.py\napp/views/user.py\napp/views/feedback.py\napp/views/about.py]
    D --> F[All above +\napp/views/admin.py]
```

---

## 3. Resume Analysis Pipeline

```mermaid
flowchart TD
    A([User Uploads PDF]) --> B[save_uploaded_file\nhelpers.py]
    B --> C[extract_text_from_pdf\npdf_reader.py]
    C --> D[SHA-256 Hash of Text]
    D --> E{get_resume_by_hash\nuser_data.py}
    E -- Already in DB --> F[Load Cached Result\nSkip Re-Analysis]
    E -- New Resume --> G[Run Full Pipeline]

    G --> H[parse_resume\nresume_parser.py]
    H --> H1[Groq API - Llama 3\nname + skills]
    H --> H2[Regex\nemail + phone]

    G --> I[detect_experience_level\nexperience_level.py\nFresher / Intermediate / Experienced]
    G --> J[calculate_resume_score\nresume_score.py\n0-100 + breakdown]
    G --> K[normalize_skills\nnormalizer.py\naliases + lowercase]
    K --> L[analyze_skill_gap\nskill_gap.py\npresent vs missing]

    G --> M[build_semantic_text\nsematic_text_builder.py]
    M --> N[get_embedding\nembeddings.py\nSentenceTransformer\n384-dim vector]
    N --> O[cosine_similarity\nsimilarity.py\nvs JD embedding]
    O --> P[job_match_score\n0.0 to 1.0]

    H1 --> Q[Assemble Full Record]
    H2 --> Q
    I --> Q
    J --> Q
    L --> Q
    P --> Q

    Q --> R[(MongoDB\nresumes collection)]
    Q --> S[(MongoDB\nanalytics collection\nresume_id + role + score)]
    Q --> T[get_recommended_courses\ncourse_recommender.py]
    T --> U[Render Results\nin Streamlit UI]
    F --> U
```

---

## 4. MongoDB ER Diagram

```mermaid
erDiagram
    USERS {
        string username PK
        string password_hash
        string role
    }

    RESUMES {
        ObjectId _id PK
        string name
        string email
        string phone
        array skills
        string experience_level
        int score
        object score_breakdown
        string target_role
        float job_match_score
        array present_skills
        array missing_skills
        array embedding
        string resume_hash
        int cluster_id
        datetime timestamp
    }

    ANALYTICS {
        ObjectId _id PK
        ObjectId resume_id FK
        string target_role
        float job_match_score
        datetime timestamp
    }

    FEEDBACK {
        ObjectId _id PK
        string name
        string email
        int rating
        string comments
        datetime timestamp
    }

    RESUMES ||--o{ ANALYTICS : "one resume\nmany events"
```

---

## 5. Caching Behaviour

```mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant Cache
    participant Groq

    User->>Streamlit: Upload Resume (PDF)
    Streamlit->>Cache: extract_with_ai(text) called?
    Cache-->>Streamlit: MISS - not cached yet
    Streamlit->>Groq: API call - extract skills
    Groq-->>Streamlit: {name, skills[]}
    Streamlit->>Cache: Store result for this text
    Streamlit-->>User: Show results

    Note over User,Groq: User clicks something (Streamlit reruns)

    User->>Streamlit: Same resume still loaded
    Streamlit->>Cache: extract_with_ai(text) called?
    Cache-->>Streamlit: HIT - return saved result instantly
    Note over Groq: API NOT called again ✅
    Streamlit-->>User: Show results instantly
```

---

## 6. End-to-End System Flow

```mermaid
flowchart TD
    Browser([Browser]) --> SL[Streamlit Cloud\napp/main.py]
    SL --> AG{Auth Gate\nsession_state}
    AG -- not logged in --> LP[Login Page\nlogin.py]
    LP --> MDB1[(MongoDB\nusers)]
    MDB1 -- verified --> AG
    AG -- logged in --> NAV[Role-Based Sidebar]
    NAV --> UP[User Uploads PDF]
    UP --> PDF[pdfminer\nextract text]
    PDF --> HASH[SHA-256 Hash]
    HASH --> DUP{In MongoDB?}
    DUP -- yes --> CACHE[Load Cached\nResult]
    DUP -- no --> GROQ[Groq API\nLlama 3\nSkill Extraction]
    GROQ --> RULES[Rule-Based\nScoring + Experience]
    RULES --> ST[SentenceTransformer\nEmbedding 384-dim]
    ST --> COS[Cosine Similarity\nvs Job Description]
    COS --> SKGAP[Skill Gap\nAnalysis]
    SKGAP --> SAVE[(MongoDB\nresumes + analytics)]
    SAVE --> REC[Course\nRecommendations]
    REC --> UI([Streamlit UI\nResults Displayed])
    CACHE --> UI

    NAV -- admin role --> ADMIN[Admin Dashboard\nadmin.py]
    ADMIN --> MDB2[(MongoDB\nAll Collections)]
    MDB2 --> CHARTS[Plotly Charts\nClustering\nSimilarity Search]
    CHARTS --> UI
```

---

## 7. AI vs Rule-Based Decision Map

```mermaid
flowchart LR
    A[Resume Text] --> B{What to extract?}

    B --> C[Skills + Name]
    B --> D[Email + Phone]
    B --> E[Experience Level]
    B --> F[Resume Score]
    B --> G[Job Match]

    C -->|Context needed\nAI required| C1[Groq API\nLlama 3\nllama-3.1-8b-instant]
    D -->|Pattern-based\n100% deterministic| D1[Regex]
    E -->|Binary signals\nkeyword sections| E1[Rule-Based]
    F -->|Section detection\nexplainable| F1[Rule-Based]
    G -->|Semantic meaning\nembedding math| G1[SentenceTransformers\nCosine Similarity]

    style C1 fill:#6366f1,color:#fff
    style D1 fill:#10b981,color:#fff
    style E1 fill:#10b981,color:#fff
    style F1 fill:#10b981,color:#fff
    style G1 fill:#8b5cf6,color:#fff
```
