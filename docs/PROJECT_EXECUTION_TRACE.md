# 🗺️ AI Resume Analyzer — Step-by-Step Code Execution Trace

This document maps out the literal, step-by-step execution path of the codebase. It details **which file calls what function, what data is passed, and what value is returned** from startup to database storage.

---

## 🔑 Phase 1: Application Ingestion & Authentication Gate

### 1. File: `app/main.py` (Startup Entry point)
*   **Trigger**: You run `streamlit run app/main.py`
*   **Action**: Initializes session state (`logged_in = False`). It immediately checks:
    ```python
    if not st.session_state.logged_in:
        login_page() # Render login UI
        return # STOP execution
    ```
*   **Output**: Stops execution of the main app and redirects the user to the login views.

### 2. File: `app/views/login.py` (Authentication UI)
*   **Trigger**: User enters username/password and clicks "Sign In".
*   **Action**: Calls `verify_user(username, password)` from `backend/database/auth.py`.
*   **Input**: `username` (string), `password` (string).

### 3. File: `backend/database/auth.py` (Security Engine)
*   **Trigger**: Called by `login.py`.
*   **Action**: 
    1. Fetches database reference using `get_db()` from `backend/database/db.py`.
    2. Queries MongoDB: `db['users'].find_one({"username": username})`.
    3. Verifies password hash using `bcrypt.checkpw(password, stored_hash)`.
*   **Output (Returns)**:
    *   `user` (dictionary) if passwords match.
    *   `None` if passwords do not match.

### 4. File: `app/views/login.py` (Authentication UI)
*   **Trigger**: Receives output from `auth.py`.
*   **Action**: 
    *   *If user is None*: Displays `st.error("Invalid credentials")`.
    *   *If user is dict*: Sets session state:
        ```python
        st.session_state.logged_in = True
        st.session_state.username = user["username"]
        st.session_state.role = user["role"]
        st.rerun() # Forces Streamlit to rerun main.py
        ```

### 5. File: `app/main.py` (On Rerun)
*   **Trigger**: Streamlit re-runs file.
*   **Action**: Since `session_state.logged_in` is now `True`, the login gate is skipped. It loads the sidebar, checks `role`, and dynamically builds navigation options.
*   **Redirect**: User clicks on "👤 User" $\rightarrow$ imports and calls `user_page()` from `app/views/user.py`.

---

## 📄 2. Resume Ingestion

### 6. File: `app/views/user.py` (Parser UI)
*   **Trigger**: User uploads a resume PDF.
*   **Action**: Calls `save_uploaded_file(uploaded_file)` from `backend/utils/helpers.py` (Line 67).
*   **Input**: PDF file buffer.
*   **Output (Returns)**: `file_path` (string path where PDF is saved on disk).

### 7. File: `app/views/user.py` (Parser UI)
*   **Action**: Calls `extract_text_from_pdf(file_path)` from `backend/parser/pdf_reader.py` (Line 78).
*   **Input**: `file_path` (string).

### 8. File: `backend/parser/pdf_reader.py` (PDF Parser)
*   **Trigger**: Called by `user.py`.
*   **Action**: Runs `pdfminer`'s `extract_text()` to read raw text content from the PDF.
*   **Output (Returns)**: `extracted_text` (raw string of text).

---

## 🤖 Phase 3: NLP & AI Parsing Pipeline

### 9. File: `app/views/user.py` (Parser UI)
*   **Action**: Calls `parse_resume(extracted_text)` from `backend/parser/resume_parser.py` (Line 85).
*   **Input**: `extracted_text` (string).

### 10. File: `backend/parser/resume_parser.py` (Parser Core)
*   **Trigger**: Called by `user.py`.
*   **Action**:
    1. Extracts email and phone number using regular expressions (Regex).
    2. Calls `extract_with_ai(extracted_text)` (decorated with `@st.cache_data`).
    3. `extract_with_ai` calls **Groq API** running **Llama 3.1** model.
    4. Converts Groq's JSON text reply to dictionary: `parsed = json.loads(raw_text_response)`.
*   **Output (Returns)**: `parsed_data` (dictionary: `{ "name": name, "email": email, "phone": phone, "skills": [skills] }`).

### 11. File: `app/views/user.py` (Parser UI)
*   **Action**: Calls `detect_experience_level(extracted_text)` from `backend/analysis/experience_level.py` (Line 86).
*   **Input**: `extracted_text` (string).

### 12. File: `backend/analysis/experience_level.py` (Experience Analyzer)
*   **Trigger**: Called by `user.py`.
*   **Action**: Scans text for job/internship keywords via Regex; falls back to PDF page count.
*   **Output (Returns)**: String representation (`"Fresher"`, `"Intermediate"`, or `"Experienced"`).

### 13. File: `app/views/user.py` (Parser UI)
*   **Action**: Calls `calculate_resume_score(extracted_text)` from `backend/analysis/resume_score.py` (Line 87).
*   **Input**: `extracted_text` (string).

### 14. File: `backend/analysis/resume_score.py` (Resume Scorer)
*   **Trigger**: Called by `user.py`.
*   **Action**: Runs keyword checklist checks on section headings to generate a score.
*   **Output (Returns)**: Dictionary: `{ "score": int_score, "breakdown": breakdown_dict }`.

---

## 🧮 Phase 4: Semantic Matching & Embeddings

### 15. File: `app/views/user.py` (Parser UI)
*   **Action**:
    1. Normalizes skills using `normalize_skills()` in `backend/utils/normalizer.py`.
    2. Builds a text profile using `build_semantic_resume_text()` in `backend/utils/sematic_text_builder.py`.
    3. Calls `get_embedding(profile_text)` from `backend/nlp/embeddings.py`.
*   **Input**: `profile_text` (string).

### 16. File: `backend/nlp/embeddings.py` (Deep Learning Vector Generator)
*   **Trigger**: Called by `user.py`.
*   **Action**:
    1. Loads the SentenceTransformer (`all-MiniLM-L6-v2`) model once (cached via `@st.cache_resource`).
    2. Converts text to vector: `model.encode(text)`.
*   **Output (Returns)**: `resume_embedding` (384-dimensional float array).

### 17. File: `app/views/user.py` (Parser UI)
*   **Action**:
    1. Fetches the job description text for selected target role from `backend/utils/job_roles.py`.
    2. Generates embedding for job description: `job_embedding = get_embedding(job_description)`.
    3. Calls `cosine_similarity(resume_embedding, job_embedding)` from `backend/nlp/similarity.py`.
*   **Input**: `resume_embedding` (array), `job_embedding` (array).

### 18. File: `backend/nlp/similarity.py` (Cosine Math)
*   **Trigger**: Called by `user.py`.
*   **Action**: Runs linear algebra computation to calculate the cosine of the angle between vectors.
*   **Output (Returns)**: `similarity_score` (float between 0.0 and 1.0).

---

## 💾 Phase 5: Hashing, Deduplication & Database Persistence

### 19. File: `app/views/user.py` (Parser UI)
*   **Action**: Computes unique SHA-256 hash from the generated `semantic_text` profile (Line 291):
    ```python
    resume_hash = hashlib.sha256(extracted_text.encode("utf-8")).hexdigest()
    ```
    Then calls `get_resume_by_hash(resume_hash)` from `backend/database/user_data.py` (Line 304).
*   **Input**: `resume_hash` (64-character string).

### 20. File: `backend/database/user_data.py` (Deduplication Check)
*   **Trigger**: Called by `user.py` (Line 304).
*   **Action**: Queries MongoDB `resumes` collection: `resumes_col.find_one({"resume_hash": resume_hash})`.
*   **Output (Returns)**:
    *   `db_record` (dictionary of past analysis) if found (Cache Hit).
    *   `None` if new resume hash (Cache Miss).

### 21. File: `app/views/user.py` (Parser UI)
*   **Action**:
    *   *If Cache Hit (Existing resume)*: Skips writing to `resumes` collection.
    *   *If Cache Miss (New resume)*: Calls `save_resume(resume_record)` in `backend/database/user_data.py` (Line 306).
    *   Logs the matching event: Calls `save_analytics_record(analytics_event)` in `backend/database/analytics.py` (Line 309).
    *   Generates course recommendations using `get_recommended_courses()` in `backend/recommender/course_recommender.py`.
*   **Output**: Renders all visual analysis dashboards, skill gaps, and course recommendations in the Streamlit UI.

---

## 🛠️ Phase 6: Admin Dashboard & System Analytics

### 22. File: `app/main.py` (Sidebar Navigation)
*   **Trigger**: User (with role `"admin"`) selects the "🛠️ Admin" menu item in the Navigation sidebar.
*   **Action**: Streamlit triggers a script rerun and executes the navigation block (Line 649) calling `admin_page()` from `app/views/admin.py`.

### 23. File: `app/views/admin.py` (Admin Security Gate)
*   **Action**: Checks if `admin_authenticated` is `True` in session state.
    *   *If False*: Renders a secure password lock overlay. Takes the password input, checks it against the hardcoded `"admin123"`, sets `admin_authenticated = True`, and runs `st.rerun()`.
    *   *If True*: Allows the controller code to execute.

### 24. File: `app/views/admin.py` (Analytics Ingestion & Charting)
*   **Action**: 
    1. Fetches database reference using `get_db()`.
    2. Pulls all logged entries from MongoDB `analytics` collection: `analytics_col.find({}, {"_id": 0})`.
    3. Loads the raw records into a **Pandas DataFrame** `df = pd.DataFrame(data)` for data formatting.
    4. Computes metrics (total counts, average resume score, unique roles) and plots distribution charts (e.g. pie charts, histograms, bar charts) using **Plotly Express**.

### 25. File: `app/views/admin.py` (Trend Extraction)
*   **Action**: Triggers calculation requests to the admin insights engine inside `backend/analysis/admin_insights.py`:
    *   Calls `get_global_missing_skills()` to extract system-wide skill gaps.
    *   Calls `get_rolewise_missing_skills()` to extract skill gaps split by target roles.
    *   Calls `get_experience_vs_score()` to correlate candidate seniority to profile score.
    *   Calls `get_rolewise_job_match()` to audit matching ratios per role.

### 26. File: `backend/analysis/admin_insights.py` (Analytics Aggregator)
*   **Trigger**: Called by `admin.py`.
*   **Action**:
    *   Queries `resumes` and `analytics` collections.
    *   Tops lists using Python's `Counter` class (frequency counting) to group skill items.
*   **Output (Returns)**: Dictionary mappings of skills or score averages to be rendered inside Pandas DataFrames on the Admin UI.

### 27. File: `app/views/admin.py` (Semantic Candidate Search)
*   **Action**: Displays a list of all analyzed candidates. When the admin selects a candidate ID, it retrieves the candidate's embedding vector and calls `get_top_k_similar_resumes(embedding, k=5)` from `backend/analysis/resume_similarities.py`.

### 28. File: `backend/analysis/resume_similarities.py` (Top-K Semantic Matches)
*   **Trigger**: Called by `admin.py`.
*   **Action**:
    1. Loads all candidate embeddings from MongoDB using `load_all_resumes_for_ml()` in `user_data.py`.
    2. Loops through the vector database calculating the cosine similarity of each candidate against the selected candidate.
    3. Sorts them in descending order and returns the top 5 match tuples.
*   **Output (Returns)**: List of tuples `[(ObjectId, similarity_score), ...]`.

### 29. File: `app/views/admin.py` (K-Means Clustering Execution)
*   **Trigger**: Admin selects $k$ (number of clusters) and clicks "Run Clustering".
*   **Action**: Calls `cluster_resumes(k=k)` from `backend/analysis/resume_clustering.py`.

### 30. File: `backend/analysis/resume_clustering.py` (K-Means Machine Learning)
*   **Trigger**: Called by `admin.py`.
*   **Action**:
    1. Fetches all candidate vectors from MongoDB.
    2. Instantiates a `KMeans(n_clusters=k)` classifier from the `scikit-learn` package.
    3. Runs clustering: `.fit(embeddings)`.
    4. Computes label assignments and calls `save_cluster_assignments(assignments)` to save cluster numbers back to MongoDB.
*   **Output (Returns)**: Dictionary mapping candidate IDs to integer cluster groups.
