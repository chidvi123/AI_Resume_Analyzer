import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from backend.database.db import get_db
from backend.analysis.resume_similarities import get_top_k_similar_resumes
from backend.analysis.resume_clustering import cluster_resumes
from backend.database.user_data import save_cluster_assignments
from backend.analysis.admin_insights import (
    get_global_missing_skills,
    get_rolewise_missing_skills,
    get_experience_vs_score,
    get_rolewise_job_match,
    get_cluster_insights,
)
from backend.database.feedback import get_feedback_rating_stars

ADMIN_PASSWORD = "admin123"   # change later if needed


def admin_page():
    st.title("Admin Dashboard")

    # session flag for admin auth
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False

    # -------- LOGIN BLOCK --------
    if not st.session_state["admin_authenticated"]:
        password = st.text_input("Enter Admin Password", type="password")

        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state["admin_authenticated"] = True
                st.success("Access granted")
                st.rerun()
            else:
                st.error("Incorrect password")
        return

    if st.button("Logout"):
        st.session_state["admin_authenticated"] = False
        st.success("Logged out")
        st.stop()

    # -------- AUTHENTICATED ADMIN BELOW --------

    db = get_db()
    analytics_col = db["analytics"]
    data = list(analytics_col.find({}, {"_id": 0}))

    st.write("Total resumes analyzed:", len(data))

    if not data:
        st.info("No analytics data available yet.")
        return

    df = pd.DataFrame(data)
    for col in df.columns:
        if col.endswith("_id") or col == "_id":
            df[col] = df[col].astype(str)

    st.dataframe(df)

    # -------- SUMMARY METRICS --------
    avg_score = sum(d["resume_score"] for d in data) / len(data)

    experience_counts = {}
    role_counts = {}

    for d in data:
        experience_counts[d["experience_level"]] = (
            experience_counts.get(d["experience_level"], 0) + 1
        )
        role_counts[d["target_role"]] = (
            role_counts.get(d["target_role"], 0) + 1
        )

    st.subheader("Summary Metrics")
    st.write(f"Average Resume Score: {round(avg_score, 2)}")
    st.write("Experience Level Distribution")
    st.write(experience_counts)
    st.write("Target Job Role Distribution")
    st.write(role_counts)

    # ================= FEEDBACK ANALYTICS =================
    st.subheader("User Feedback Analytics")
    avg_rating,rating_counts=get_feedback_rating_stars()

    if avg_rating==0.0:
        st.info("No feedback ratings available yet.")
    else:
        st.write(f"**Average User Rating:**  {avg_rating} / 5")

        labels=[]
        sizes=[]

        for rating in sorted(rating_counts.keys()):
            labels.append(f"{rating}")
            sizes.append(rating_counts[rating])

        fig,ax = plt.subplots()
        ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90
        )

        ax.set_title("Feedback Rating Distribution")

        st.pyplot(fig)

    # ================= ADMIN INSIGHTS (NON-CLUSTER) =================

    st.subheader("📊 Admin Insights")

    # Global Missing Skills
    st.markdown("### 🔧 Most Missing Skills (Overall)")
    global_missing = get_global_missing_skills()
    if global_missing:
        st.write(
            dict(sorted(global_missing.items(), key=lambda x: x[1], reverse=True)[:10])
        )
    else:
        st.info("No missing skill data available.")

    # Role-wise Missing Skills
    st.markdown("### 🎯 Missing Skills by Role")
    rolewise_missing = get_rolewise_missing_skills()
    if rolewise_missing:
        for role, skills in rolewise_missing.items():
            st.write(
                f"**{role}** → "
                f"{dict(sorted(skills.items(), key=lambda x: x[1], reverse=True)[:5])}"
            )
    else:
        st.info("No role-wise missing skill data.")

    # Experience vs Resume Score
    st.markdown("### 📈 Experience Level vs Avg Resume Score")
    exp_vs_score = get_experience_vs_score()
    if exp_vs_score:
        st.write(exp_vs_score)
    else:
        st.info("No experience-score analytics found.")

    # Role-wise Job Match Score
    st.markdown("### 🧩 Role-wise Avg Job Match Score (%)")
    role_match = get_rolewise_job_match()
    if role_match:
        st.write(role_match)
    else:
        st.info("No job-match analytics found.")

    # ================= RESUME SIMILARITY =================

    st.subheader("Resume Similarity")

    resumes_col = db["resumes"]
    resumes = list(resumes_col.find({}, {"_id": 1, "parsed_data.name": 1}))

    if resumes:
        resume_map = {str(r["_id"]): r["_id"] for r in resumes}

        selected_id_str = st.selectbox(
            "Select a resume",
            resume_map.keys()
        )

        selected_resume = resumes_col.find_one(
            {"_id": resume_map[selected_id_str]}
        )

        if selected_resume:
            top_k = get_top_k_similar_resumes(
                selected_resume["embedding"],
                k=5
            )
            if top_k:
                st.write("Top similar resumes:")
                for rid, score in top_k:
                    st.write(f"- Resume {rid} → {round(score, 4)}")
            else:
                st.info("No similar resume found.")
    else:
        st.info("No resumes available for similarity.")

    # ================= RESUME CLUSTERING =================

    st.subheader("Resume Clustering")

    k = st.number_input(
        "Number of clusters (k)",
        min_value=2,
        max_value=20,
        value=5,
        step=1
    )

    if st.button("Run clustering"):
        assignments, model = cluster_resumes(k=k)

        if not assignments:
            st.warning("Not enough resumes to perform clustering.")
        else:
            save_cluster_assignments(assignments)
            st.success("Clustering completed and saved.")

        st.write("Assignments:", assignments)

    # ================= CLUSTER INSIGHTS =================

    st.subheader("🧠 Cluster Insights")

    cluster_insights = get_cluster_insights()
    if cluster_insights:
        for cid, info in cluster_insights.items():
            st.write(f"**Cluster {cid}**")
            st.write(info)
    else:
        st.info("Run clustering to see cluster insights.")

    # ================= CHARTS =================

    fig, ax = plt.subplots()
    ax.bar(experience_counts.keys(), experience_counts.values())
    ax.set_title("Experience Level Distribution")
    st.pyplot(fig)

    fig, ax = plt.subplots()
    ax.pie(
        role_counts.values(),
        labels=role_counts.keys(),
        autopct="%1.1f%%"
    )
    ax.set_title("Target Job Role Distribution")
    st.pyplot(fig)

    scores = [d["resume_score"] for d in data]
    fig, ax = plt.subplots()
    ax.hist(scores, bins=10)
    ax.set_title("Resume Score Distribution")
    st.pyplot(fig)

    # ================= CSV EXPORT =================

    csv = df.to_csv(index=False)

    st.download_button(
        label="Download Analytics CSV",
        data=csv,
        file_name="admin_analytics.csv",
        mime="text/csv"
    )
