# 🎓 AI Resume Analyzer — Detailed Technical Explainer (Discussed Components)

This document provides a bit-by-bit, detailed technical breakdown of all the components, code architectures, and optimization logic we have discussed so far.

---

## 🔐 1. Authentication & Session Management

### The Core Problem: Streamlit's Execution Model
* Streamlit operates on a **reactive execution model**: every time a user clicks a button, changes a checkbox, or types in a text box, Streamlit runs the entire Python file (`app/main.py`) from line 1 to the end.
* Because of this, standard variables get reset to their defaults on every reload. We need a way to persist login credentials throughout the user's session.

### The Role of `st.session_state` (In-Memory Sandbox)
* `st.session_state` is a sandbox memory cache that persists across app reruns. 
* **Key feature: Isolation**: `session_state` is completely isolated **per browser tab**. If User A and User B access the site simultaneously, they get separate states. This prevents session leaks (unlike a global variable or direct database flag which would log everyone in globally).

### The Authentication Gate Flow
1. **Start**: The app launches `app/main.py`.
2. **Initialize State**: We check if authentication variables exist. If not, we set defaults:
   ```python
   if "logged_in" not in st.session_state:
       st.session_state.logged_in = False
       st.session_state.role = None
       st.session_state.username = None
   ```
3. **The Gate**: The main function immediately checks:
   ```python
   if not st.session_state.logged_in:
       login_page() # Render login UI
       return # Stop execution (blocks the rest of the app)
   ```
4. **Sign In / Registration Verification**:
   * **Verify**: When a user logs in, `app/views/login.py` takes the input and runs `verify_user(username, password)`.
   * **Bcrypt Hashing**: We never store plain text passwords. [`backend/database/auth.py`](file:///c:/Users/ADMIN/Documents/Projects/AI_Resume_Analyzer/backend/database/auth.py) uses the **bcrypt** library. 
     * When registering, the password is encrypted with a random salt:
       ```python
       password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
       ```
     * When logging in, bcrypt validates it by running the input password against the stored hash:
       ```python
       bcrypt.checkpw(password.encode(), user["password_hash"])
       ```
   * **State Update**: If verified, we explicitly set the state:
     ```python
     st.session_state.logged_in = True
     st.session_state.username = user["username"]
     st.session_state.role = user["role"]
     st.rerun() # Reload main.py
     ```
   * **Rerun Bypass**: On reload, `logged_in` is `True`, so the gate is skipped, and the sidebar renders.

### Role-Based Access Control (RBAC)
* We dynamically render the sidebar menu depending on the authenticated role:
  ```python
  if st.session_state.role == "admin":
      pages = ["🏠 Home", "👤 User", "💬 Feedback", "ℹ️ About", "🛠️ Admin"]
  else:
      pages = ["🏠 Home", "👤 User", "💬 Feedback", "ℹ️ About"]
  ```
* This hides the admin panel from standard users.

---

## 📄 2. Resume Ingestion & Deduplication Cache

### Local File Ingestion
1. The user uploads a PDF in `app/views/user.py`.
2. The file is saved to the server's disk under `Uploaded_Resumes/` via `save_uploaded_file()` in `backend/utils/helpers.py`.
   * *Scaling note*: For a large-scale cloud application, local disk is avoided (since cloud servers have ephemeral, temporary storage). In production, you would upload the file to a cloud bucket like **AWS S3** and store the URL reference in MongoDB.

### Text Extraction
* We run `extract_text_from_pdf()` using the `pdfminer` package. It reads the raw byte stream of the PDF, deciphers the layout, and extracts a continuous string of text.

### SHA-256 Deduplication (At start of pipeline)
* To avoid running expensive LLM API calls and storing identical data, we generate a unique **SHA-256 hash** of the raw text immediately after extraction:
  ```python
  resume_hash = hashlib.sha256(extracted_text.encode("utf-8")).hexdigest()
  ```
* We check MongoDB resumes collection: `existing = get_resume_by_hash(resume_hash)`.
  * **Cache Hit (Duplicate)**: If the hash is found in MongoDB, we pull the previously saved results directly. The app skips Groq API calls, experience checks, scoring, and semantic text matching.
  * **Cache Miss (New)**: The app runs the full analysis pipeline.

---

## 🤖 3. AI parsing & Groq API Integration

### Groq Llama 3.1 LLM Parsing
* Standard parser libraries use rules (regex) to extract skills, which fail if the resume has formatting variations.
* We pass the resume text to the **Groq LPU API** using Meta's **Llama 3.1 (8B)** model (`llama-3.1-8b-instant`).
* We enforce a strict output schema by requesting a JSON response:
  ```python
  response_format={"type": "json_object"}
  ```
* This forces the LLM to return a clean, parseable JSON block containing only the extracted `"name"` and `"skills"` array.

### Python JSON Parsing
* The API returns a raw string. We extract the message choice and parse it into a Python dictionary:
  ```python
  raw = response.choices[0].message.content.strip()
  parsed = json.loads(raw)
  ```
  * `response.choices[0].message.content`: Grabs the text inside the first response choice.
  * `json.loads(raw)`: Converted the JSON text string into a native Python dictionary so we can read variables.

### Streamlit Caching for API calls (`@st.cache_data`)
* To prevent Streamlit from hitting the Groq API on every page rerun (e.g., when the user selects a job dropdown), we decorate the extraction function:
  ```python
  @st.cache_data(show_spinner=False)
  def extract_with_ai(text: str) -> dict:
  ```
* Streamlit intercepts this call: if the input `text` is the same, it skips the Groq API call entirely and loads the previous dictionary output from RAM.

---

## 📊 4. Rule-Based Experience Level Detection

* Located in [`backend/analysis/experience_level.py`](file:///c:/Users/ADMIN/Documents/Projects/AI_Resume_Analyzer/backend/analysis/experience_level.py).
* Runs using regular expressions and heuristics instead of an AI model to guarantee speed and predictability:
  1. **Experienced**: Scans text for senior terms (e.g., `"5+ years"`, `"Lead"`, `"Manager"`).
  2. **Intermediate**: Scans for internship terms (e.g., `"internship"`, `"trainee"`).
  3. **Page Count Heuristic**: If no keywords match, it checks the PDF page count:
     * 1 Page $\rightarrow$ `"Fresher"`
     * 2 Pages $\rightarrow$ `"Intermediate"`
     * 3+ Pages $\rightarrow$ `"Experienced"`

---

## 🎨 5. UI Animations with Lottie

* In `app/main.py`, we render vector graphics using `streamlit_lottie`.
* **What it is**: Lottie animations are vector graphic animations exported as JSON coordinates from After Effects.
* **Why it is used**:
  * Unlike GIFs, Lottie animations are tiny text files (few KB), reducing website load times.
  * They render dynamically, meaning they scale perfectly to any resolution without becoming blurry.

---

## 🗄️ 6. MongoDB Database Schemas (Resumes vs. Analytics)

To keep database queries clean and optimal, we split the resume analysis data and search query logs into two distinct collections. This forms a standard **One-to-Many (1:N)** relationship.

```
       resumes collection                   analytics collection
┌───────────────────────────────┐      ┌───────────────────────────────┐
│ _id: ObjectId("64b2c3...")    │◄─────┼─── resume_id: ObjectId(...)   │ (Match Event 1)
│ resume_hash: "a1b2c3d4..."    │      ├───────────────────────────────┤
│ semantic_text: "..."          │◄─────┼─── resume_id: ObjectId(...)   │ (Match Event 2)
│ parsed_data: { name, skills } │      └───────────────────────────────┘
│ experience_level: "Fresher"   │
│ resume_score: 85              │
└───────────────────────────────┘
```

### Collection 1: `resumes`
This collection holds the permanent, unique candidate resume profiles. We search this collection by `resume_hash` at the start of the pipeline.

```python
{
    "resume_hash": resume_hash,            # SHA-256 hash of raw extracted text (Primary Key check)
    "semantic_text": semantic_text,        # Cleaned and structured profile text (noise filtered out)
    "parsed_data": parsed_data,            # Groq AI output dictionary containing extracted skills
    "experience_level": experience_level,  # Classified experience tier (Fresher, Intermediate, Experienced)
    "resume_score": resume_score,          # Completeness score from headings checklist
    "score_breakdown": score_breakdown,    # Detailed score points mapping per heading category
    "embedding": resume_embedding,         # 384-dimensional list of floats for NLP similarity matching
    "timestamp": datetime.now()            # Date and time the candidate first uploaded this file
}
```

### Collection 2: `analytics`
This collection logs **every single match event** triggered when a user clicks the "Analyze for this role" button. If the same candidate compares their resume against 3 different job roles, they will have **1 resume record** in `resumes` and **3 query events** in `analytics`.

```python
{
    "username": username,                   # Username of the active logged-in user who ran the comparison
    "resume_id": existing["_id"],           # References the _id of the parent document in 'resumes' (Foreign Key)
    "timestamp": datetime.now(),            # Date and time this matching comparison was made
    "experience_level": experience_level,  # Seniority level at the time of query
    "resume_score": resume_score,          # Completeness score of the resume
    "target_role": target_role,            # The selected role aiming for (e.g. "data_scientist")
    "job_match_score": match_score,        # Cosine similarity matching percentage
    "skills_present": present_skills,      # List of string names of skills candidate has matched
    "skills_missing": missing_skills,      # List of string names of skills candidate is missing (gaps)
    "skills_present_count": len(skills),   # Number of requirements candidate meets
    "skills_missing_count": len(missing)   # Count of skill gaps candidate lacks
}
```

---

## 🧮 7. Line-by-Line Code Explanations

### File 1: `backend/utils/normalizer.py`
This file standardizes parsed resume skills to resolve spelling variants, lowercase differences, and abbreviations.

```python
from backend.utils.constants import SKILL_ALIASES
```
* **Line 1**: Imports the dictionary `SKILL_ALIASES` which maps variations (e.g. `"ml"`, `"reactjs"`) to standardized strings (e.g. `"machine learning"`, `"react"`).

```python
def normalize_skills(skills: list[str]) -> list[str]:
```
* **Line 3**: Declares the main function `normalize_skills`, which accepts a list of raw string skills as input and is typed to return a list of standardized strings.

```python
    if not skills:
        return []
```
* **Lines 7–8**: Safe guard. If the input list is empty or `None`, it immediately exits and returns an empty list.

```python
    normalized = set()
```
* **Line 10**: Declares an empty Python `set()`. A set is used because it automatically handles deduplication (elements in a set must be unique, preventing duplicate entries for the same skill).

```python
    for skill in skills:
```
* **Line 12**: Runs a loop to iterate through each raw skill string in the input list.

```python
        skill_clean = skill.lower().strip()
```
* **Line 13**: Converts the skill text to lowercase (`.lower()`) and removes any accidental leading or trailing white spaces (`.strip()`) to standardize spelling.

```python
        skill_clean = SKILL_ALIASES.get(skill_clean, skill_clean)
```
* **Line 14**: Performs an alias lookup in `SKILL_ALIASES`. If the cleaned skill is a key in the map (e.g., `"reactjs"`), it returns its mapped value (`"react"`). If the skill is not in the dictionary, `.get()` defaults to keeping the original string name.

```python
        normalized.add(skill_clean)
```
* **Line 15**: Adds the standardized skill string to the `normalized` set.

```python
    return sorted(list(normalized))
```
* **Line 17**: Converts the unique set back into a standard Python list, sorts it alphabetically, and returns it.

---

### File 2: `backend/utils/sematic_text_builder.py`
This file builds a clean, structured candidate profile string from raw PDF text, normalized skills, and experience levels, filtering out formatting noise to prepare text for the vector embedding model.

```python
import re
```
* **Line 13**: Imports the built-in Python Regular Expressions (`re`) module to handle text replacement and filtering.

```python
IMPORTANT_SECTIONS = ["experience", "work experience", "internship", ...]
```
* **Lines 15–24**: Defines a list of header/section keywords that contain relevant candidate signals.

```python
def build_semantic_resume_text(raw_text: str, skills: list[str], experience_level: str) -> str:
```
* **Lines 26–30**: Defines the profile building function. It accepts the raw resume text string, normalized skills list, and experience level string.

```python
    if not raw_text:
        return ""
```
* **Lines 31–32**: Safe guard check. If `raw_text` is empty, returns an empty string.

```python
    text = raw_text.lower()
```
* **Line 34**: Converts the entire input resume text to lowercase to ensure regex checks and string matching are case-insensitive.

```python
    text = re.sub(r"\S+@\S+", " ", text)
```
* **Line 37**: Uses regex substitution (`re.sub`) to replace all email patterns (e.g. `name@domain.com`) with a blank space to remove personal identifiers.

```python
    text = re.sub(r"\+?\d[\d\s\-]{8,}\d", " ", text)
```
* **Line 38**: Uses regex to search for patterns of 8+ consecutive digits with optional spaces/dashes (phone numbers) and replaces them with a space.

```python
    lines = text.splitlines()
```
* **Line 40**: Splits the continuous lowercase text string into a Python list of individual lines based on newline characters.

```python
    selected_lines = []
```
* **Line 42**: Initializes an empty list `selected_lines` to collect high-signal lines for the final profile text.

```python
    for line in lines:
```
* **Line 44**: Initiates a loop to scan every line of the resume text.

```python
        if any(section in line for section in IMPORTANT_SECTIONS):
            selected_lines.append(line)
```
* **Lines 45–46**: Checks if the current line mentions any keyword in the `IMPORTANT_SECTIONS` list. If yes, it is added to `selected_lines` (this keeps headers like "Professional Experience" or "Projects").

```python
        elif len(line.split()) > 4:
            selected_lines.append(line)
```
* **Lines 47–48**: If the line is not a heading, it checks if it contains more than 4 words. This keeps descriptive sentences and filters out single-word clutter, page numbers, or dates.

```python
    semantic_text = f"""
    experience_level: {experience_level}
    skills: {', '.join(skills)}
    resume_content:
    {' '.join(selected_lines)}
    """
```
* **Lines 50–55**: Formulates a structured multi-line string. It puts the experience level and skills right at the top (giving them strong weight) and appends the filtered content below.

```python
    semantic_text = re.sub(r"\s+", " ", semantic_text)
```
* **Line 57**: Uses regex to replace any sequence of multiple spaces, tabs, or newlines with a single space, collapsing the entire document into a single continuous paragraph.

```python
    return semantic_text.strip()
```
* **Line 59**: Trims any leading or trailing spaces and returns the finalized semantic text block.

---

### File 3: `backend/nlp/embeddings.py`
This file implements the deep learning model loading and vector encoding logic to convert candidate profiles and job roles into numerical vector arrays.

```python
import streamlit as st
```
* **Line 1**: Imports Streamlit to leverage model and data caching decorators (`@st.cache_resource` and `@st.cache_data`).

```python
from sentence_transformers import SentenceTransformer
```
* **Line 2**: Imports the `SentenceTransformer` class from the Hugging Face library, which is the standard library for loading pre-trained text embedding models.

```python
@st.cache_resource
def load_embedding_model():
```
* **Lines 4–5**: Defines the model loading helper. The `@st.cache_resource` decorator ensures the transformer model is loaded into memory only **once** upon app startup, rather than reloading it on every single run.

```python
    return SentenceTransformer("all-MiniLM-L6-v2")
```
* **Line 6**: Loads the `all-MiniLM-L6-v2` transformer model (a fast, lightweight 80MB model mapping text to a 384-dimensional vector space).

```python
@st.cache_data(show_spinner=False)
def get_embedding(text: str):
```
* **Lines 8–9**: Declares the vector encoding function. The `@st.cache_data` decorator saves computed vector outputs in RAM. If the same string is requested again, it returns the cached array in 0ms.

```python
    if not text:
        return None
```
* **Lines 10–11**: Safe guard. Returns `None` if the input text profile is empty.

```python
    model = load_embedding_model()
```
* **Line 13**: Fetches the initialized `SentenceTransformer` model from memory.

```python
    return model.encode(text)
```
* **Line 14**: Calls `.encode()` which executes a neural network forward-pass to project the string into a 384-dimensional NumPy array, and returns it.

---

### File 4: `backend/nlp/similarity.py`
This file implements the vector cosine similarity math to determine how well a resume vector matches a target job role vector.

```python
import numpy as np
```
* **Line 1**: Imports the NumPy mathematical library to run high-speed linear algebra operations.

```python
def cosine_similarity(vec1, vec2) -> float:
```
* **Line 4**: Declares the function, accepting two vector inputs (either numpy arrays or lists) and typed to return a float value.

```python
    if vec1 is None or vec2 is None:
        return 0.0
```
* **Lines 5–6**: Safeguard check. If either vector parameter is missing, it returns a score of `0.0`.

```python
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
```
* **Lines 8–9**: Force-casts the vector inputs into standard NumPy arrays to allow vector dot-products and norm calculations.

```python
    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
```
* **Line 11**: Computes the Cosine Similarity formula:
  * `np.dot(vec1, vec2)` calculates the **dot product** of the vectors.
  * `np.linalg.norm(vec)` calculates the **Euclidean Length** of the vectors: $\sqrt{\sum x_i^2}$.
  * The calculation divides the dot product by the product of their lengths to yield the cosine of the angle between them in a 384-dimensional space:
    $$\cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$

```python
    return float(similarity)
```
* **Line 13**: Casts the result from NumPy data types to a standard Python float, returning a value between `-1.0` and `1.0` (with `1.0` meaning identical semantic direction/meaning).

---

### File 5: `backend/analysis/skill_gap.py`
This file performs the set-algebra calculations to find overlapping skills (matched) and missing skills (gaps) between the candidate's profile and the job role requirements.

```python
from collections import Counter
```
* **Line 1**: Imports the `Counter` dictionary class to support other frequency tally functions in the same module.

```python
from backend.database.db import get_db
```
* **Line 2**: Imports the singleton database connection loader.

```python
from backend.utils.normalizer import normalize_skills
```
* **Line 3**: Imports the normalization helper to standardize spellings before comparing them.

```python
def analyze_skill_gap(resume_skills, required_skills):
```
* **Line 5**: Declares the skill gap analysis function, taking the candidate's skills list and the role requirements list.

```python
    resume_set = set(normalize_skills(resume_skills))
```
* **Line 7**: Standardizes the candidate's skills list and converts it into a Python `set()`.

```python
    required_set = set(normalize_skills(required_skills))
```
* **Line 8**: Standardizes the job's required skills list and converts it into a Python `set()`.

```python
    present_skills = sorted(list(resume_set & required_set))
```
* **Line 10**: Uses the **set intersection operator (`&`)** to find skills present in **both** sets (i.e. matched skills), converts the set back into a standard list, and sorts it alphabetically.

```python
    missing_skills = sorted(list(required_set - resume_set))
```
* **Line 11**: Uses the **set difference operator (`-`)** to find skills present in `required_set` but not in the candidate's `resume_set` (i.e. missing skills), converts it to a sorted list.

```python
    return {
        "present_skills": present_skills,
        "missing_skills": missing_skills
    }
```
* **Lines 13–16**: Packages the lists into a dictionary mapping `"present_skills"` and `"missing_skills"` keys, and returns it.

---

### File 6: `backend/recommender/course_recommender.py`
This file serves as a lookup registry. It matches the lowercase string representation of the target job role to return a list of recommended course titles and links.

```python
# ds_course = [ ['Title', 'URL'], ... ]
```
* **Lines 7–16**: Declares static lists containing nested lists of titles and link strings for Data Science courses. Similar lists are declared for web development, DevOps, iOS, Android, etc.

```python
def get_recommended_courses(target_role: str) -> list:
```
* **Line 129**: Declares the main recommender function, accepting the selected job role string as input and returning a list.

```python
    role = target_role.lower()
```
* **Line 130**: Converts the input string to lowercase to ensure substring matching behaves case-insensitively.

```python
    if "data_scientist" in role or "ml" in role or ("data" in role and "scientist" in role):
        return ds_course
```
* **Lines 132–133**: Checks if the target role contains keywords indicating Data Science or Machine Learning. If true, returns the `ds_course` registry list.

```python
    elif "machine_learning" in role or "machine learning" in role:
        return ds_course
```
* **Lines 134–135**: Checks for explicit machine learning matches, returning `ds_course`.

```python
    elif "data_analyst" in role or ("data" in role and "analyst" in role):
        return analyst_course
```
* **Lines 136–137**: Directs data analyst roles to the `analyst_course` list. Similar checks route roles for DevOps, QA, Android, iOS, Software Engineer, Full Stack, Frontend, Backend, UI/UX, and Web.

```python
    return []
```
* **Line 161**: Default fallback. If the selected role matches none of the defined keywords, it returns an empty list.

---

### File 7: `backend/database/user_data.py`
This file controls the primary read and write operations for candidate profiles, database caching, and ML retrieval queries inside MongoDB.

```python
import numpy as np
```
* **Line 1**: Imports NumPy for numerical structures.

```python
from datetime import datetime
```
* **Line 2**: Imports Python's `datetime` class to record the timeline of uploads.

```python
from backend.database.db import get_db
```
* **Line 3**: Imports the singleton MongoDB Atlas connection.

```python
from bson import ObjectId
```
* **Line 4**: Imports `ObjectId` to read and reference MongoDB internal object identifiers.

```python
def save_resume(record: dict):
```
* **Line 6**: Declares the helper to write analyzed resumes to the database.

```python
    db = get_db()
    resumes_col = db["resumes"]
```
* **Lines 7–8**: Retrieves the connection instance and references the `"resumes"` collection.

```python
    record["timestamp"] = datetime.now()
```
* **Line 9**: Appends the current timeline timestamp into the resume document dictionary.

```python
    resumes_col.insert_one(record)
```
* **Line 10**: Executes a PyMongo `.insert_one()` query to write the document record directly to MongoDB.

```python
def get_resume_by_hash(resume_hash: str):
```
* **Line 12**: Declares the search helper to lookup unique documents via their SHA-256 hashes.

```python
    db = get_db()
    resumes_col = db["resumes"]
```
* **Lines 13–14**: Connects to the database and references the `"resumes"` collection.

```python
    return resumes_col.find_one({"resume_hash": resume_hash})
```
* **Lines 16–18**: Executes `.find_one()`. If a matching record is found, it returns the **entire MongoDB document** (including parsed data, scores, and embeddings) as a native Python dictionary. If no match is found, it returns `None`.

---

### File 8: `backend/database/analytics.py`
This file logs job matching search events to track trends, query match averages, and experience ranges in a separate analytics collection.

```python
from backend.database.db import get_db
```
* **Line 1**: Imports the database connection manager.

```python
def save_analytics_record(record: dict):
```
* **Line 3**: Declares the save function, taking the analytics event dictionary as input.

```python
    db = get_db()
```
* **Line 4**: Retrieves the database reference instance.

```python
    analytics_col = db["analytics"]
```
* **Line 5**: Establishes a reference to the target `"analytics"` collection in MongoDB.

```python
    analytics_col.insert_one(record)
```
* **Line 7**: Runs a PyMongo write operation `.insert_one()` to persist the event record to MongoDB.

---

### File 9: `backend/analysis/resume_score.py`
This file calculates a completeness/quality score (0-100) using a set of rules and weights across various section headings, applying a custom rule to distinguish real experience from courses or internships.

```python
def calculate_resume_score(text: str) -> dict:
```
* **Line 12**: Declares the scoring function, taking the raw extracted text and returning a results dictionary.

```python
    text = text.lower()
```
* **Line 14**: Lowercases the text to support case-insensitive checks.

```python
    score = 0
    breakdown = {}
```
* **Lines 16–17**: Initializes the cumulative score to `0` and builds an empty dictionary to log scores for individual categories.

```python
    rules = { "Summary/Objective": {"keywords": [...], "points": 10}, ... }
```
* **Lines 19–44**: Defines the scoring rules dictionary. Each category defines the list of search triggers and total potential points (e.g. Education: 15, Skills: 20, Projects: 20, Experience: 25).

```python
    real_experience_keywords = [...]
    training_keywords = [...]
```
* **Lines 46–63**: Declares list elements pointing to real full-time jobs versus education/training courses.

```python
    for section, rule in rules.items():
```
* **Line 65**: Loops through each criteria in the rules dictionary.

```python
        if section == "Experience/Internship":
```
* **Line 67**: Custom rule for experience scoring to prevent students with only Udemy courses or simple internships from getting the full 25 points.

```python
            has_real_exp = any(k in text for k in real_experience_keywords)
            has_intern = "intern" in text or "internship" in text
            has_training = any(k in text for k in training_keywords)
```
* **Lines 69–71**: Performs boolean checks. `has_real_exp` checks if full-time job keywords exist. `has_intern` searches for intern/internship matches. `has_training` searches for learning course platforms.

```python
            if has_real_exp:
                breakdown[section] = rule["points"]
                score += rule["points"]
```
* **Lines 73–75**: If a professional job match is found, award the full 25 points.

```python
            elif has_intern and not has_training:
                breakdown[section] = rule["points"] // 2
                score += rule["points"] // 2
```
* **Lines 77–79**: If it only matches internship keywords and no course training tags are present, award half points (12 points).

```python
            else:
                breakdown[section] = 0
```
* **Lines 81–82**: Otherwise, award `0` points for this section.

```python
        else:
            if any(keyword in text for keyword in rule["keywords"]):
                breakdown[section] = rule["points"]
                score += rule["points"]
```
* **Lines 84–87**: For standard sections (e.g., Education, Projects): if any matching keyword is present in the text, award the full section points.

```python
            else:
                breakdown[section] = 0
```
* **Lines 88–89**: Otherwise, set that category's breakdown score to `0`.

```python
    if len(text.split()) < 150:
        score -= 10
```
* **Lines 91–92**: Length penalty heuristic: if the total word count is less than 150 (too short for a proper resume), deduct 10 points.

```python
    score = max(0, min(score, 100))
```
* **Line 94**: Clips the final score between `0` and `100` to prevent negative values or scores exceeding the maximum limit.

```python
    return {
        "score": score,
        "breakdown": breakdown
    }
```
* **Lines 96–99**: Returns the packaged results dictionary containing the overall score and section breakdowns.

---

### File 10: `backend/analysis/experience_level.py`
This file implements the experience classification rules, checking for professional vs. internship keyword boundaries, and falling back to a page count heuristic.

```python
import re
```
* **Line 13**: Imports the regular expression module.

```python
def detect_experience_level(text: str, num_pages: int | None = None) -> str:
```
* **Line 15**: Declares the classifier function, taking the text and an optional page count, returning the level string.

```python
    text = text.lower()
```
* **Line 16**: Converts text to lowercase to ensure consistency.

```python
    experience_patterns = [ r"\bwork experience\b", ... ]
    internship_patterns = [ r"\binternship\b", ... ]
```
* **Lines 20–39**: Defines lists of regex patterns. The prefix `r` denotes a raw string. The `\b` escape sequence matches a **word boundary**, which is critical to prevent substring matches (e.g. matching `"intern"` inside the word `"international"`).

```python
    if any(re.search(pattern, text) for pattern in experience_patterns):
        return "Experienced"
```
* **Lines 42–43**: Scans the text for any full-time experience pattern. If a match is found, it immediately classifies the candidate as `"Experienced"`.

```python
    if any(re.search(pattern, text) for pattern in internship_patterns):
        return "Intermediate"
```
* **Lines 46–47**: If no experienced signals match, searches the internship patterns. If found, returns `"Intermediate"`.

```python
    if num_pages is not None:
```
* **Line 50**: Fallback check if no keyword triggers matched.

```python
        if num_pages <= 1:
            return "Fresher"
        elif num_pages == 2:
            return "Intermediate"
        else:
            return "Experienced"
```
* **Lines 51–56**: Classifies based on pages (1 page or less is fresher, 2 is intermediate, 3+ is experienced).

```python
    return "Fresher"
```
* **Line 58**: Ultimate default classification if no keywords or page counts were matching.

---

### File 11: `backend/analysis/admin_insights.py`
This file aggregates analytics data from MongoDB (using Python's `Counter` and `defaultdict`) to calculate trends such as global missing skills, experience-level distributions, average job match scores, and KMeans cluster summaries.

```python
from collections import Counter, defaultdict
```
* **Line 1**: Imports standard Python collection tools: `Counter` (to easily count occurrences of values) and `defaultdict` (which initializes dictionary keys automatically with default types to avoid `KeyError` crashes).

```python
def get_global_missing_skills():
```
* **Line 10**: Declares the function to tally missing competencies across all unique resumes.

```python
    db = get_db()
    analytics_col = db["analytics"]
    counter = Counter()
```
* **Lines 11–13**: Establishes database connection and references the `analytics` collection.

```python
    seen_resumes = set()
    for r in analytics_col.find({}, {"resume_id": 1, "skills_missing": 1}):
```
* **Lines 16–17**: Queries the analytics logs. To prevent duplicate submissions by the same user from inflating/skewing the counts, it filters the results using the `seen_resumes` set.

```python
        rid = r.get("resume_id")
        if rid:
            rid_str = str(rid)
            if rid_str not in seen_resumes:
                seen_resumes.add(rid_str)
                counter.update(r.get("skills_missing", []))
```
* **Lines 18–23**: Adds the candidate ID to the set and counts their missing skills list exactly **once** globally.

```python
    return dict(counter)
```
* **Line 25**: Converts the Counter back to a normal Python dictionary and returns it.

```python
def get_rolewise_missing_skills():
```
* **Line 33**: Declares the helper to analyze missing skills grouped by target job roles.

```python
    db = get_db()
    analytics_col = db["analytics"]
    role_skill_counter = defaultdict(Counter)
```
* **Lines 34–36**: Connects to the database and references the `analytics` collection.

```python
    seen_searches = set()
    for a in analytics_col.find({}, {"resume_id": 1, "target_role": 1, "skills_missing": 1}):
```
* **Lines 39–40**: Queries the logs. We create a `seen_searches` set to collect unique `(resume_id, target_role)` pairs. This prevents double-counting if a user matches the same resume against the same job role multiple times.

```python
        rid = a.get("resume_id")
        role = a.get("target_role")
        if rid and role:
            search_key = (str(rid), role)
            if search_key not in seen_searches:
                seen_searches.add(search_key)
                role_skill_counter[role].update(a.get("skills_missing", []))
```
* **Lines 41–46**: If the search key is unique, adds it to the set and updates the role-specific counter in **a single query**, completely bypassing the slow nested $N+1$ lookups to the `resumes` collection.

```python
    return {role: dict(counter) for role, counter in role_skill_counter.items()}
```
* **Line 48**: Converts all Counters to dictionaries and returns the final rolewise map.

```python
def get_experience_vs_score():
```
* **Line 61**: Declares a helper correlating candidate experience to their quality score.

```python
    buckets = defaultdict(list)
```
* **Line 68**: Instantiates a dictionary where new keys automatically initialize with empty lists (`[]`).

```python
    cursor = analytics_col.find({}, {"experience_level": 1, "resume_score": 1, "_id": 0})
```
* **Lines 70–77**: Pulls score and seniority pairs from the search database.

```python
    for a in cursor:
        buckets[a["experience_level"]].append(a["resume_score"])
```
* **Lines 79–80**: Appends each resume score to the list corresponding to its experience tier.

```python
    return {level: round(mean(scores), 2) for level, scores in buckets.items() if scores}
```
* **Lines 82–86**: Loops through the buckets, computes the statistical average score using `mean(scores)`, rounds to 2 decimal places, and returns the dictionary.

```python
def get_rolewise_job_match():
```
* **Line 93**: Declares the function grouping matching percentages by job categories.

```python
    for a in analytics_col.find({}, {"target_role": 1, "job_match_score": 1}):
        buckets[a["target_role"]].append(a["job_match_score"] * 100)
```
* **Lines 99–100**: Iterates through search records. It multiplies `job_match_score` (between 0.0 and 1.0) by 100 to convert to a percentage value.

```python
    return {role: round(mean(scores)) for role, scores in buckets.items()}
```
* **Line 102**: Computes the average match percentage rounded to the nearest integer.

```python
def get_cluster_insights():
```
* **Line 109**: Declares the helper compiling profiles for candidate cluster pools.

```python
    for r in resumes_col.find({}, {"cluster_id": 1, "resume_score": 1, "skills_missing": 1, "experience_level": 1}):
        if "cluster_id" in r:
            clusters[r["cluster_id"]].append(r)
```
* **Lines 115–125**: Fetches cluster assignments and logs all candidate records under their assigned K-Means cluster keys.

```python
    for cid, items in clusters.items():
        scores = [r["resume_score"] for r in items]
        exp_levels = [r["experience_level"] for r in items]
        skill_counter = Counter()
        for r in items:
            skill_counter.update(r.get("skills_missing", []))
```
* **Lines 129–140**: For each cluster, lists all scores and seniorities, and aggregates the count of missing competencies.

```python
        cluster_insights[cid] = {
            "count": len(items),
            "avg_resume_score": round(mean(scores), 2),
            "common_missing_skills": [s for s, _ in skill_counter.most_common(5)],
            "dominant_experience": Counter(exp_levels).most_common(1)[0][0]
        }
```
* **Lines 141–148**: Builds cluster statistics: count, average score, top 5 most common missing skills using `.most_common(5)`, and the dominant seniority using the most frequent item in `Counter(exp_levels)`.

---

### File 12: `backend/analysis/resume_similarities.py`
This file performs similarity searches against the vector database, loading all stored candidate embeddings and sorting them based on their cosine scores against a selected resume vector.

```python
import numpy as np
```
* **Line 1**: Imports NumPy for numerical vector casting.

```python
from backend.database.user_data import load_all_resumes_for_ml
```
* **Line 2**: Imports the DB loader utility that fetches all candidate IDs and their vectors in bulk.

```python
from backend.nlp.similarity import cosine_similarity
```
* **Line 3**: Imports the Cosine Similarity calculator.

```python
def get_top_k_similar_resumes(query_embedding, k=5):
```
* **Line 6**: Declares the helper, taking the selected resume's embedding vector and the target count of recommendations `k`.

```python
    resume_ids, embeddings = load_all_resumes_for_ml()
```
* **Line 18**: Calls the bulk loader to pull two parallel lists representing all candidate IDs and vector arrays from MongoDB.

```python
    if len(resume_ids) == 0:
        return []
```
* **Lines 20–21**: Safeguard check. If no resumes are saved in MongoDB, exits and returns an empty list.

```python
    query_vec = np.array(query_embedding)
```
* **Line 23**: Standardizes the selected candidate's embedding as a NumPy array.

```python
    scores = []
    for rid, emb in zip(resume_ids, embeddings):
        score = cosine_similarity(query_vec, emb)
        scores.append((rid, score))
```
* **Lines 25–28**: Loops through all candidate records in the database using `zip()`. It calculates the cosine similarity score between our selected query vector and each candidate's vector, appending the `(id, score)` tuples.

```python
    scores.sort(key=lambda x: x[1], reverse=True)
```
* **Line 31**: Sorts the list in descending order based on the similarity score (`x[1]`), putting the most mathematically similar candidates at the top.

```python
    filtered = [s for s in scores if s[1] < 0.999]
```
* **Line 34**: Excludes self-matches. A candidate has a 100% match score ($\approx 1.0$) against their own resume. We filter out scores above `0.999` to ensure we don't recommend the candidate back to themselves.

```python
    return filtered[:k]
```
* **Line 36**: Returns the top `k` similar candidate records.

---

### File 13: `backend/analysis/resume_clustering.py`
This file implements the unsupervised KMeans machine learning clustering using scikit-learn, grouping candidate vector embeddings in 384-dimensional space and saving cluster mappings in MongoDB.

```python
import numpy as np
```
* **Line 1**: Imports NumPy for array management.

```python
from sklearn.cluster import KMeans
```
* **Line 2**: Imports the **`KMeans`** classifier from the `scikit-learn` library to perform clustering calculations.

```python
from backend.database.user_data import load_all_resumes_for_ml
```
* **Line 3**: Imports the bulk data loader helper.

```python
def cluster_resumes(k=5, random_state=42):
```
* **Line 5**: Declares the main clustering algorithm function. It takes two arguments: $k$ (the target cluster count) and `random_state` (a seed value to ensure the centroid positions are initialized identically on every run).

```python
    resume_ids, embeddings = load_all_resumes_for_ml()
```
* **Line 14**: Loads candidate IDs and their embedding vectors from the MongoDB collection.

```python
    if len(resume_ids) < k:
        return [], None
```
* **Lines 17–18**: Safeguard check. In K-Means, you cannot form $k$ groups if your dataset is smaller than $k$. If the count of resumes in the database is less than the clusters requested, it halts and returns an empty list.

```python
    X = np.array(embeddings)
```
* **Line 21**: Packages the list of embeddings into a standard 2D NumPy array structure required by scikit-learn: `(n_samples, n_features)` which matches `(number_of_resumes, 384)`.

```python
    model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
```
* **Lines 23–27**: Instantiates the scikit-learn `KMeans` class. 
  * `n_clusters=k`: Set to form $k$ clusters.
  * `random_state=random_state`: Anchor seed for reproducibility.
  * `n_init=10`: Runs the clustering algorithm 10 separate times using different random initial centroids and automatically picks the run with the most mathematically optimal convergence.

```python
    cluster_labels = model.fit_predict(X)
```
* **Line 29**: Calls `.fit_predict(X)` to:
  1. Fit: Run distance minimization iterations to locate the centroids (centers) of each cluster.
  2. Predict: Assign an integer label between `0` and `k-1` to each resume specifying its closest centroid.

```python
    assignments = list(zip(resume_ids, cluster_labels))
```
* **Line 31**: Pairs each MongoDB candidate ID with its assigned integer cluster group label and packages it into a list.

```python
    return assignments, model
```
* **Line 33**: Returns the cluster assignment list and the trained model object.

---

### File 14: `app/views/admin.py`
This file renders the Admin Dashboard UI. It connects the components by querying the databases, loading data frames, displaying charts, running recommender similarity, and launching clustering.

```python
import streamlit as st
import pandas as pd
import plotly.express as px
```
* **Lines 1–3**: Imports Streamlit (UI rendering), Pandas (DataFrame loading), and Plotly Express (chart visualization).

```python
from backend.database.db import get_db
from backend.analysis.resume_similarities import get_top_k_similar_resumes
from backend.analysis.resume_clustering import cluster_resumes
from backend.database.user_data import save_cluster_assignments
from backend.analysis.admin_insights import (...)
from backend.database.feedback import get_feedback_rating_stars
```
* **Lines 5–16**: Imports all backend connection utilities: database reference loaders, similarities math, KMeans models, and analytics aggregators.

```python
ADMIN_PASSWORD = "admin123"
```
* **Line 18**: Hardcodes the security passcode token for admin access.

```python
def admin_page():
```
* **Line 21**: Main dashboard rendering controller.

```python
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False
```
* **Lines 46–47**: Initializes the admin authenticated token to `False` in memory.

```python
    if not st.session_state["admin_authenticated"]:
        # Renders Overlay Layout (Lines 50-61)
        password = st.text_input("Admin Password", type="password", ...)
        if st.button("Unlock Dashboard"):
            if password == ADMIN_PASSWORD:
                st.session_state["admin_authenticated"] = True
                st.rerun()
```
* **Lines 49–73**: If the user hasn't entered the passcode yet, stops the page load and displays a lock overlay. If they enter `"admin123"`, sets the token to `True` and runs `st.rerun()` to reload.

```python
    db = get_db()
    analytics_col = db["analytics"]
    data = list(analytics_col.find({}, {"_id": 0}))
```
* **Lines 83–85**: Connects to the database and reads all recorded entries from the `"analytics"` collection (excluding `_id` keys).

```python
    df = pd.DataFrame(data)
```
* **Line 91**: Loads the database records directly into a Pandas DataFrame.

```python
    for col in df.columns:
        if df[col].apply(lambda x: str(type(x))).str.contains("ObjectId").any():
            df[col] = df[col].astype(str)
```
* **Lines 94–96**: Resolves BSON types: scans columns and converts MongoDB `ObjectId` types to plain strings so they don't break charting operations.

```python
    df["resume_score"] = pd.to_numeric(df["resume_score"], errors="coerce")
```
* **Line 99**: Converts the `resume_score` column into formal numeric values. Any invalid text is converted to NaN (`errors="coerce"`) to prevent mathematical calculation errors when computing averages.

```python
    # Overview Metrics (Lines 113-146)
    st.metric("📄 Total Analyses", len(df))
    st.metric("⭐ Avg Resume Score", round(df["resume_score"].mean(), 1))
```
* **Lines 113–146**: Computes and displays dashboard summary cards (using `len(df)` and `.mean()`).

```python
    avg_rating, rating_counts = get_feedback_rating_stars()
    fig = px.pie(values=sizes, names=labels, title="Rating Distribution", hole=0.4)
    st.plotly_chart(fig)
```
* **Lines 150–183**: Renders feedback rating statistics, plotting a donut chart representing star breakdowns using Plotly.

```python
    global_missing = get_global_missing_skills()
    gm_df = pd.DataFrame(sorted(global_missing.items(), ...))
    st.dataframe(gm_df)
```
* **Lines 188–197**: Queries global missing skills from the database, sorts them, and prints them inside an interactive table. Similar sections display role-wise missing skills, experience averages, and target role breakdowns (Lines 201–300).

```python
    selected_id = st.selectbox("Select Resume ID", resume_map.keys())
    selected_resume = resumes_col.find_one({"_id": resume_map[selected_id]})
    top_k = get_top_k_similar_resumes(selected_resume["embedding"], k=5)
```
* **Lines 305–330**: Displays a selection dropdown. When the admin selects a resume ID, fetches its 384 numbers and queries similarities to show the top 5 matches.

```python
    k = st.number_input("Number of clusters (k)", ...)
    if st.button("Run Clustering"):
        assignments, _ = cluster_resumes(k=k)
        save_cluster_assignments(assignments)
```
* **Lines 336–349**: K-Means clustering controls. Clicking the button runs scikit-learn classification and writes the groups to MongoDB resumes.

---

## 🚀 8. Architectural Optimization: Database Design & Performance Refactoring

During our optimization cycle, we resolved a major logical database design flaw and implemented a high-performance deduplication strategy for the Admin Panel.

### 1. The Database Refactoring (1:N Normalization)
* **The Bug**: Originally, `skills_missing` and `skills_present` were saved directly inside the `resumes` collection. 
  * If candidate Amit matched his resume against **Data Scientist** first, his list was saved as `["Machine Learning", "Python"]`.
  * If he subsequently matched his resume against **Web Developer**, the `resumes` document was NOT updated (to preserve cache integrity).
  * When the Admin Dashboard ran, it saw his Web Developer search log, queried his `resumes` document, and read the static Data Science list. It mistakenly recorded that Web Developers are missing Machine Learning!
* **The Solution**: We moved the actual `skills_present` and `skills_missing` lists from the `resumes` collection directly into the **`analytics`** collection logs. Because `analytics` logs each transaction uniquely, it preserves the exact role-specific skill gaps for every match!
* **The Code**:
  In `app/views/user.py`:
  ```python
  save_analytics_record({
      "username": st.session_state.username,
      "resume_id": existing["_id"],
      "skills_present": present_skills,
      "skills_missing": missing_skills,
      ...
  })
  ```

### 2. High-Performance Deduplication Logic
* **The Problem**: If a user runs multiple query comparisons for the same resume and same role, their identical search logs would inflate the global charts (double-counting).
* **The Solution**: Inside `backend/analysis/admin_insights.py`, we deduplicate search entries on-the-fly using Python **sets** before compiling frequencies:
  * **Global counts**: We collect unique `resume_id` keys in a set to count each candidate exactly **once** globally.
  * **Role-wise counts**: We collect unique `(resume_id, target_role)` tuples to count a candidate exactly **once per target role**.
* **The Performance Gain**: By shifting the missing skills arrays to `analytics`, we fetch the logs and their skill lists in **a single database query**. We completely deleted the nested `find_one()` query loop, fixing a massive $N+1$ query performance bottleneck!

### 3. Active User Metrics
* **Total Registered Users**: Counts the total documents inside the MongoDB `users` collection:
  ```python
  total_registered_users = db["users"].count_documents({})
  ```
* **Unique Active Users**: Tracks the unique usernames in the search logs:
  ```python
  unique_active_users = df["username"].nunique() if "username" in df.columns else 0
  ```
  These two metrics are displayed side-by-side on the system overview dashboard.
