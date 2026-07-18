from collections import Counter,defaultdict
from statistics import mean
from backend.database.db import get_db
from bson import ObjectId

# -------------------------------------------------
# 1. Global Missing Skills
# -------------------------------------------------

def get_global_missing_skills():
    db = get_db()
    analytics_col = db["analytics"]
    counter = Counter()

    # Deduplicate by resume_id so we only count each candidate's profile once globally
    seen_resumes = set()
    for r in analytics_col.find({}, {"resume_id": 1, "skills_missing": 1}):
        rid = r.get("resume_id")
        if rid:
            rid_str = str(rid)
            if rid_str not in seen_resumes:
                seen_resumes.add(rid_str)
                counter.update(r.get("skills_missing", []))
    
    return dict(counter)


# -------------------------------------------------
# 2. Role-wise Missing Skills
# -------------------------------------------------

def get_rolewise_missing_skills():
    db = get_db()
    analytics_col = db["analytics"]
    role_skill_counter = defaultdict(Counter)

    # Deduplicate by (resume_id, target_role) so we count once per candidate per role matching
    seen_searches = set()
    for a in analytics_col.find({}, {"resume_id": 1, "target_role": 1, "skills_missing": 1}):
        rid = a.get("resume_id")
        role = a.get("target_role")
        if rid and role:
            search_key = (str(rid), role)
            if search_key not in seen_searches:
                seen_searches.add(search_key)
                role_skill_counter[role].update(a.get("skills_missing", []))
            
    return {role: dict(counter) for role, counter in role_skill_counter.items()}

        

# -------------------------------------------------
# 3. Experience Level vs Resume Score
# -------------------------------------------------

from collections import defaultdict
from statistics import mean
from backend.database.db import get_db


def get_experience_vs_score():
    """
    Returns average resume score per experience level.
    """
    db = get_db()
    analytics_col = db["analytics"]

    buckets = defaultdict(list)

    cursor = analytics_col.find(
        {},
        {
            "experience_level": 1,
            "resume_score": 1,
            "_id": 0
        }
    )

    for a in cursor:
        buckets[a["experience_level"]].append(a["resume_score"])

    return {
        level: round(mean(scores), 2)
        for level, scores in buckets.items()
        if scores
    }


#-------------------------------------------------
# 4. Role-wise Job Match Score
# -------------------------------------------------

def get_rolewise_job_match():
    db=get_db()
    analytics_col=db["analytics"]

    buckets=defaultdict(list)

    for a in analytics_col.find({},{"target_role":1,"job_match_score":1}):
        buckets[a["target_role"]].append(a["job_match_score"]*100)

    return {role :round(mean(scores)) for role,scores in buckets.items()}


#-------------------------------------------------
# 5. Cluster-Level Insights
# -------------------------------------------------

def get_cluster_insights():
    db = get_db()
    resumes_col = db["resumes"]
    analytics_col = db["analytics"]

    clusters = defaultdict(list)

    # 1. Fetch resumes grouped by their KMeans cluster assignment
    for r in resumes_col.find(
        {},
        {
            "cluster_id": 1,
            "resume_score": 1,
            "experience_level": 1,
        },
    ):
        if "cluster_id" in r:
            clusters[r["cluster_id"]].append(r)
    
    cluster_insights = {}

    # 2. Iterate through each cluster to aggregate features
    for cid, items in clusters.items():
        if not items:
            continue

        scores = [r["resume_score"] for r in items]
        exp_levels = [r["experience_level"] for r in items]

        skill_counter = Counter()

        for r in items:
            # Query the analytics collection to get missing skills logged for this resume ID
            analytics_docs = list(analytics_col.find({"resume_id": r["_id"]}, {"skills_missing": 1}))
            for doc in analytics_docs:
                skill_counter.update(doc.get("skills_missing", []))
        
        cluster_insights[cid] = {
            "count": len(items),
            "avg_resume_score": round(mean(scores), 2),
            "common_missing_skills": [
                s for s, _ in skill_counter.most_common(5)
            ],
            "dominant_experience": Counter(exp_levels).most_common(1)[0][0],
        }
    return cluster_insights

