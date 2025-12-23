from collections import Counter,defaultdict
from statistics import mean
from backend.database.db import get_db
from bson import ObjectId

# -------------------------------------------------
# 1. Global Missing Skills
# -------------------------------------------------

def get_global_missing_skills():
    db=get_db()
    resumes_col=db["resumes"]

    counter=Counter()

    for r in resumes_col.find({},{"skills_missing":1}):
        counter.update(r.get("skills_missing",[]))
    
    return dict(counter)


# -------------------------------------------------
# 2. Role-wise Missing Skills
# -------------------------------------------------

def get_rolewise_missing_skills():
    db=get_db()
    resumes_col=db["resumes"]
    analytics_col=db["analytics"]
    role_skill_counter=defaultdict(Counter)

    for a in analytics_col.find({},{"resume_id":1,"target_role":1}):
        resume_id = a.get("resume_id")
        role = a.get("target_role")

        if not resume_id or not role:
            continue

        resume = resumes_col.find_one(
            {"_id": ObjectId(resume_id)},
            {"skills_missing": 1}
        )

        if resume:
            role_skill_counter[role].update(
                resume.get("skills_missing", [])
            )
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
    db=get_db()
    resumes_col=db["resumes"]

    clusters=defaultdict(list)

    for r in resumes_col.find(
        {},
        {
            "cluster_id":1,
            "resume_score":1,
            "skills_missing":1,
            "experience_level":1,
        },
    ):
        if "cluster_id" in r:
            clusters[r["cluster_id"]].append(r)
    
    cluster_insights={}

    for cid,items in clusters.items():
        if not items:
            continue

        scores=[r["resume_score"] for r in items]
        exp_levels=[r["experience_level"] for r in items]

        skill_counter=Counter()

        for r in items:
            skill_counter.update(r.get("skills_missing",[]))
        
        cluster_insights[cid]={
            "count":len(items),
            "avg_resume_score":round(mean(scores),2),
            "common_missing_skills":[
                s for s,_ in skill_counter.most_common(5)
            ],
            "dominant_experience":Counter(exp_levels).most_common(1)[0][0],
        }
    return cluster_insights

