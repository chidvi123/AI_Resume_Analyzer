# AI Resume Analyzer — Complete Project Flow

## Entry Point

Everything starts from pp/main.py:

`
streamlit run app/main.py
`

---

## Step 1 — Authentication Gate

`
User opens app
      |
main.py checks: st.session_state.logged_in ?
      |
   No  -> show login_page()  (blocks everything)
   Yes -> show sidebar + navigation
`

### Login / Register Flow (app/views/login.py)

`
User enters username + password
      |
verify_user(username, password)   <- backend/database/auth.py
      |
MongoDB users collection lookup
      |
bcrypt.checkpw(password, stored_hash)
      |
   Match    -> session_state: logged_in=True, username, role -> st.rerun()
   No match -> show error

Register Tab:
      |
register_user(username, password, role=user)
      |
Check username exists in MongoDB
      |
bcrypt.hashpw(password) -> store in DB
      |
Auto-login immediately
`

---

## Step 2 — Role-Based Navigation

`
role == admin  ->  Home | User | Feedback | About | Admin
role == user   ->  Home | User | Feedback | About
`

| Sidebar Option | File |
|---|---|
| Home | app/views/home.py |
| User | app/views/user.py |
| Feedback | app/views/feedback.py |
| About | app/views/about.py |
| Admin | app/views/admin.py |

---

## Step 3 — Resume Analysis Pipeline (app/views/user.py)

`
User uploads PDF
      |
save_uploaded_file()                <- backend/utils/helpers.py
      |
extract_text_from_pdf(path)         <- backend/parser/pdf_reader.py
      |
SHA-256 hash of text
      |
get_resume_by_hash(hash)            <- backend/database/user_data.py
      |
In MongoDB?  -> load cached result (skip re-analysis)
Not in DB?   -> run full pipeline below
`

### Full Analysis Pipeline

`
resume_text
      |
      +-> parse_resume(text)              <- backend/parser/resume_parser.py
      |       |
      |       +-- Groq API (llama-3.1-8b-instant) -> name, skills[]
      |       +-- regex                            -> email
      |       +-- regex                            -> phone
      |
      +-> detect_experience_level(text)   <- backend/analysis/experience_level.py
      |       Rule-based: checks keywords, page count
      |       Result: Fresher / Intermediate / Experienced
      |
      +-> calculate_resume_score(text)    <- backend/analysis/resume_score.py
      |       Section keyword checks: Summary, Education, Skills,
      |       Projects, Experience, Certifications
      |       Result: score 0-100 + breakdown
      |
      +-> normalize_skills(skills)        <- backend/utils/normalizer.py
      |       Lowercase + aliases (ml -> machine learning)
      |
      +-> analyze_skill_gap(             <- backend/analysis/skill_gap.py
      |       resume_skills,
      |       ROLE_SKILLS[target_role]   <- backend/utils/constants.py
      |   )
      |   Result: { present_skills[], missing_skills[] }
      |
      +-> build_semantic_resume_text()   <- backend/utils/sematic_text_builder.py
      |
      +-> get_embedding(text)            <- backend/nlp/embeddings.py
      |       SentenceTransformer all-MiniLM-L6-v2 -> 384-dim vector
      |
      +-> JOB_ROLE_DESCRIPTIONS[role]    <- backend/utils/job_roles.py
      |       ~100-word realistic job posting per role
      |
      +-> get_embedding(job_description)
      |
      +-> cosine_similarity(             <- backend/nlp/similarity.py
              resume_embedding,
              job_embedding
          )
          Result: job_match_score (0.0 to 1.0)
`

### Data Persistence

`
Results -> save_resume()        -> MongoDB resumes collection
        -> save_analytics()     -> MongoDB analytics collection
                                   (resume_id, target_role, score, timestamp)
                                   One-to-many: one resume, many analysis events
`

### Recommendations

`
missing_skills + target_role
      |
get_recommended_courses(target_role)   <- backend/recommender/course_recommender.py
      Result: list of (course_title, url)

+ resume_videos[] and interview_videos[]
`

---

## Step 4 — Admin Dashboard (app/views/admin.py)

Only visible when session_state.role == admin.

`
get_global_missing_skills()     -> Bar chart: most needed skills globally
get_rolewise_missing_skills()   -> Role-wise skill gap breakdown
get_experience_distribution()  -> Pie: Fresher/Intermediate/Experienced split
get_role_performance()         -> Avg job match score per role

Resume Similarity Search:
  query text -> get_embedding(query) -> cosine_similarity vs all stored embeddings
  Returns top-N most similar resumes

KMeans Clustering:
  load_all_resumes_for_ml() -> all embeddings from MongoDB
  KMeans(n_clusters=k) -> save_cluster_assignments()
  Plotly scatter: clusters visualized

CSV Export of analytics data
`

---

## MongoDB Collections (Schema)

`
Database: ai_resume_analyzer

users
  username       (string, unique)
  password_hash  (bcrypt - never plain text)
  role           (user | admin)

resumes          (one per unique resume, deduplicated by SHA-256)
  _id            (ObjectId)
  name, email, phone
  skills[]
  experience_level
  score, score_breakdown{}
  target_role, job_match_score
  present_skills[], missing_skills[]
  embedding[]    (384-dim float vector)
  resume_hash    (SHA-256 for deduplication)
  cluster_id     (set after KMeans)
  timestamp

analytics        (one-to-many with resumes)
  resume_id   -> references resumes._id
  target_role
  job_match_score
  timestamp

feedback
  name, email
  rating (1-5)
  comments
  timestamp
`

---

## File Map

`
app/
  main.py                    ENTRY - routing, session, auth gate
  views/
    login.py                 Auth UI -> auth.py
    home.py                  Landing page
    user.py                  CORE - orchestrates full pipeline
    admin.py                 Admin dashboard - reads MongoDB
    feedback.py              Feedback form -> MongoDB
    about.py                 Static info + contact form

backend/
  parser/
    pdf_reader.py            PDF -> raw text (pdfminer)
    resume_parser.py         Text -> {name, email, phone, skills}
                             Skills: Groq API (Llama 3)
                             Email/Phone: regex

  analysis/
    experience_level.py      Rule-based: Fresher/Intermediate/Experienced
    resume_score.py          Section scoring (0-100)
    skill_gap.py             present vs missing skills
    admin_insights.py        Aggregation queries for charts

  nlp/
    embeddings.py            SentenceTransformer -> 384-dim vector
    similarity.py            Cosine similarity

  recommender/
    course_recommender.py    role -> curated courses + videos

  database/
    db.py                    MongoDB connection (singleton)
    auth.py                  register_user, verify_user (bcrypt)
    user_data.py             save/load resumes + embeddings
    analytics.py             save_analytics_record

  utils/
    constants.py             ROLE_SKILLS mapping
    job_roles.py             JOB_ROLE_DESCRIPTIONS (~100 words each)
    normalizer.py            skill aliases + normalization
    sematic_text_builder.py  structured text for embedding
    helpers.py               file save utility
`

---

## AI & NLP Stack Decisions

| Task | Method | Why |
|---|---|---|
| Skill/name extraction | Groq API (Llama 3) | Context-aware, understands resume phrasing |
| Email/Phone | Regex | Accurate, deterministic, free |
| Job matching | SentenceTransformers + cosine | Semantic meaning comparison |
| Resume scoring | Rule-based | Explainable - user sees why they scored X |
| Experience detection | Rule-based | Fast, transparent |
| Clustering | KMeans on embeddings | Groups similar resumes |

---

## Environment Variables

| Key | File | Purpose |
|---|---|---|
| MONGODB_URI | backend/database/db.py | MongoDB Atlas connection |
| GROQ_API_KEY | backend/parser/resume_parser.py | Llama 3 skill extraction |

Stored in .env locally and Streamlit Cloud Secrets for deployment.

---

## End-to-End Flow Summary

`
Browser
  -> Streamlit Cloud (main.py)
    -> Auth gate (session_state check)
      -> MongoDB + bcrypt login verified
        -> PDF uploaded -> pdfminer extracts text
          -> SHA-256 dedup check
            -> Groq AI extracts skills (Llama 3)
              -> Rule-based: score + experience level
                -> SentenceTransformer: resume + JD embeddings
                  -> Cosine similarity: job match %
                    -> Skill gap: present vs missing
                      -> Save to MongoDB (resumes + analytics)
                        -> Courses + videos recommended
                          -> Everything rendered in Streamlit UI
`

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
