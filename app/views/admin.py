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

ADMIN_PASSWORD = "admin123"


def admin_page():

    # ===================== HEADER =====================
    st.title("Admin Dashboard")
    st.caption("System analytics, trends, and internal insights")

    st.divider()

    # ===================== AUTH =====================
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False

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

    # ===================== LOAD DATA =====================
    db = get_db()
    analytics_col = db["analytics"]
    data = list(analytics_col.find({}, {"_id": 0}))

    if not data:
        st.info("No analytics data available yet.")
        return

    df = pd.DataFrame(data)

    # --- Convert ObjectId columns ONLY ---
    for col in df.columns:
        if df[col].apply(lambda x: str(type(x))).str.contains("ObjectId").any():
            df[col] = df[col].astype(str)

    # --- Ensure numeric safety ---
    df["resume_score"] = pd.to_numeric(df["resume_score"], errors="coerce")
    df["job_match_score"] = pd.to_numeric(df["job_match_score"], errors="coerce")

    # ===================== OVERVIEW METRICS =====================
    st.subheader("📊 System Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Resumes", len(df))

    with col2:
        st.metric("Average Resume Score", round(df["resume_score"].mean(), 2))

    with col3:
        st.metric("Unique Job Roles", df["target_role"].nunique())

    st.divider()

    # ===================== FEEDBACK ANALYTICS =====================
    st.subheader("⭐ User Feedback Analytics")

    avg_rating, rating_counts = get_feedback_rating_stars()

    if avg_rating == 0.0:
        st.info("No feedback ratings available yet.")
    else:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.metric("Average Rating", f"{avg_rating} / 5")

        with col2:
            labels = list(map(str, sorted(rating_counts.keys())))
            sizes = [rating_counts[r] for r in sorted(rating_counts.keys())]

            fig, ax = plt.subplots(
                figsize=(3, 3),   
                dpi=90            
            )

            ax.pie(
                sizes,
                labels=labels,
                autopct="%1.0f%%",
                startangle=90,
                textprops={"fontsize": 9}  
            )

            ax.set_title(
                "Rating Distribution",
                fontsize=10
            )

            plt.tight_layout()

            st.pyplot(fig, width="content") 


    # ===================== ADMIN INSIGHTS =====================
    st.subheader("📊 Admin Insights (Trends & Patterns)")

    # -------- Global Missing Skills --------
    st.markdown("### 🔧 Most Missing Skills (Overall)")
    global_missing = get_global_missing_skills()

    if global_missing:
        gm_df = pd.DataFrame(
            sorted(global_missing.items(), key=lambda x: x[1], reverse=True)[:7],
            columns=["Skill", "Missing Count"]
        )
        st.dataframe(gm_df, width="stretch")
    else:
        st.info("No missing skill data available.")

    # -------- Role-wise Missing Skills --------
    st.markdown("### 🎯 Missing Skills by Role")
    rolewise_missing = get_rolewise_missing_skills()

    if rolewise_missing:
        rows = []
        for role, skills in rolewise_missing.items():
            for skill, count in skills.items():
                rows.append([role, skill, count])

        rm_df = pd.DataFrame(rows, columns=["Role", "Skill", "Missing Count"])
        rm_df = rm_df.sort_values("Missing Count", ascending=False)

        st.dataframe(rm_df, width="stretch")
    else:
        st.info("No role-wise missing skill data.")

    # -------- Experience vs Resume Score --------
    st.markdown("### 📈 Experience Level vs Avg Resume Score")
    exp_vs_score = get_experience_vs_score()

    if exp_vs_score:
        evs_df = pd.DataFrame(
            exp_vs_score.items(),
            columns=["Experience Level", "Average Resume Score"]
        )
        st.dataframe(evs_df, width="stretch")
    else:
        st.info("No experience-score analytics found.")

    # -------- Role-wise Job Match --------
    st.markdown("### 🧩 Role-wise Avg Job Match Score (%)")
    role_match = get_rolewise_job_match()

    if role_match:
        rm_df = pd.DataFrame(
            role_match.items(),
            columns=["Role", "Average Job Match Score"]
        )
        st.dataframe(rm_df, width="stretch")
    else:
        st.info("No job-match analytics found.")

    st.divider()

    # ===================== DISTRIBUTIONS =====================
    st.subheader("📈 Distributions")

    col1, col2 = st.columns(2)

    with col1:
        exp_counts = df["experience_level"].value_counts()
        fig, ax = plt.subplots()
        ax.bar(exp_counts.index, exp_counts.values)
        ax.set_title("Experience Level Distribution")
        st.pyplot(fig)

    with col2:
        role_counts = df["target_role"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(role_counts.values, labels=role_counts.index, autopct="%1.1f%%")
        ax.set_title("Target Job Role Distribution")
        st.pyplot(fig)

    st.divider()

    # ===================== SCORE DISTRIBUTION =====================
    st.subheader("📉 Resume Score Distribution")

    fig, ax = plt.subplots(
        figsize=(4, 2.5),   # 👈 controls size
        dpi=100
    )

    ax.hist(
        df["resume_score"].dropna(),
        bins=10,
        edgecolor="white"
    )

    ax.set_xlabel("Score", fontsize=9)
    ax.set_ylabel("Count", fontsize=9)
    ax.set_title("Resume Score Distribution", fontsize=10)

    plt.tight_layout()

    st.pyplot(fig, width="content")

    st.divider()


    # ===================== RESUME SIMILARITY =====================
    st.subheader("🔍 Resume Similarity")

    resumes_col = db["resumes"]
    resumes = list(resumes_col.find({}, {"_id": 1}))

    if resumes:
        resume_map = {str(r["_id"]): r["_id"] for r in resumes}

        selected_id = st.selectbox("Select Resume ID", resume_map.keys())
        selected_resume = resumes_col.find_one({"_id": resume_map[selected_id]})

        if selected_resume:
            top_k = get_top_k_similar_resumes(
                selected_resume["embedding"],
                k=5
            )

            if top_k:
                sim_df = pd.DataFrame(
                    [(str(rid), round(score * 100, 2)) for rid, score in top_k],
                    columns=["Resume ID", "Similarity %"]
                )
                st.dataframe(sim_df, width="stretch")
            else:
                st.info("No similar resumes found.")
    else:
        st.info("No resumes available.")

    st.divider()

    # ===================== CLUSTERING =====================
    st.subheader("🧩 Resume Clustering")

    k = st.number_input("Number of clusters (k)", min_value=2, max_value=20, value=5)

    if st.button("Run Clustering"):
        assignments, _ = cluster_resumes(k=k)

        if not assignments:
            st.warning("Not enough resumes to perform clustering.")
        else:
            save_cluster_assignments(assignments)
            st.success("Clustering completed successfully.")

    # ===================== CLUSTER INSIGHTS =====================
    st.subheader("🧠 Cluster Insights")

    cluster_insights = get_cluster_insights()
    if cluster_insights:
        for cid, info in cluster_insights.items():
            st.markdown(f"**Cluster {cid}**")
            st.write(info)
    else:
        st.info("Run clustering to see cluster insights.")

    st.divider()

    # ===================== RAW DATA =====================
    with st.expander("📄 View / Export Raw Analytics Data"):
        st.dataframe(df, width="stretch")

        csv = df.to_csv(index=False)
        st.download_button(
            "Download Analytics CSV",
            csv,
            "admin_analytics.csv",
            "text/csv"
        )
