import streamlit as st
import pandas as pd
import plotly.express as px

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
    st.markdown(
        """
        <style>
        .pg-badge b { color: #a5b4fc !important; -webkit-text-fill-color: #a5b4fc !important; }
        </style>
        <div style='margin-bottom:0.8rem;'>
            <div class='pg-badge' style='display:inline-block; background:rgba(99,102,241,0.15);
                        border:1px solid rgba(99,102,241,0.4);
                        padding:5px 14px; border-radius:999px;'>
                <b style='font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px;'
                >Admin Only</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.title("Admin Dashboard")
    st.caption("System analytics, trends, and internal insights")

    st.divider()

    # ===================== AUTH =====================
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False

    if not st.session_state["admin_authenticated"]:
        st.markdown(
            """
            <div style='max-width:420px; margin: 3rem auto; background:rgba(13,21,37,0.9);
                        border:1px solid rgba(99,102,241,0.25); border-radius:24px; padding:2.5rem;
                        box-shadow:0 0 40px rgba(99,102,241,0.2), 0 16px 48px rgba(0,0,0,0.5); text-align:center;'>
                <div style='font-size:3rem; margin-bottom:1rem;'>🔐</div>
                <h3 style='color:#f1f5f9; margin-bottom:0.3rem;'>Admin Access Required</h3>
                <p style='color:#64748b; font-size:13px; margin-bottom:0;'>Enter the admin password to continue</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Admin Password", type="password", label_visibility="collapsed",
                                     placeholder="🔑 Enter admin password...")
            if st.button("Unlock Dashboard", width="stretch"):
                if password == ADMIN_PASSWORD:
                    st.session_state["admin_authenticated"] = True
                    st.success("Access granted ✅")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Try again.")
        return

    col_logout, _ = st.columns([1, 5])
    with col_logout:
        if st.button("🚪 Logout"):
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
    st.markdown(
        """
        <div style='display:flex; align-items:center; gap:10px; margin-bottom:0.5rem;'>
            <span style='font-size:1.3rem;'>📊</span>
            <h2 style='margin:0;'>System Overview</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-highlight">
                <div class="mh-label">📄 Total Analyses</div>
                <div class="mh-value">{len(df)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-highlight">
                <div class="mh-label">⭐ Avg Resume Score</div>
                <div class="mh-value">{round(df["resume_score"].mean(), 1)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-highlight">
                <div class="mh-label">🎯 Unique Job Roles</div>
                <div class="mh-value">{df["target_role"].nunique()}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

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

            fig = px.pie(
                values=sizes,
                names=labels,
                title="Rating Distribution",
                hole=0.4,
            )
            fig.update_traces(textinfo='percent+label')
            fig.update_layout(
                margin=dict(t=30, b=10, l=10, r=10), 
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#cbd5f5")
            )

            st.plotly_chart(fig, width="stretch")


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
        st.dataframe(gm_df.reset_index(drop=True), width="stretch")
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
        rm_df = rm_df.sort_values("Missing Count", ascending=False).reset_index(drop=True)

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
        st.dataframe(evs_df.reset_index(drop=True), width="stretch")
    else:
        st.info("No experience-score analytics found.")

    # -------- Role-wise Job Match --------
    st.markdown("### 🧩 Role-wise Avg Job Match Score (%)")
    role_match = get_rolewise_job_match()

    if role_match:
        rm_df2 = pd.DataFrame(
            role_match.items(),
            columns=["Role", "Average Job Match Score"]
        )
        st.dataframe(rm_df2.reset_index(drop=True), width="stretch")
    else:
        st.info("No job-match analytics found.")

    st.divider()

    # ===================== DISTRIBUTIONS =====================
    st.subheader("📈 Distributions")

    col1, col2 = st.columns(2)

    with col1:
        exp_counts = df["experience_level"].value_counts().reset_index()
        exp_counts.columns = ["Experience Level", "Count"]
        fig = px.bar(exp_counts, x="Experience Level", y="Count", title="Experience Level Distribution", text="Count")
        fig.update_traces(textposition='outside')
        fig.update_layout(
            margin=dict(t=30, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5f5")
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        role_counts = df["target_role"].value_counts().reset_index()
        role_counts.columns = ["Target Job Role", "Count"]
        fig = px.pie(role_counts, names="Target Job Role", values="Count", title="Target Job Role Distribution", hole=0.3)
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(
            margin=dict(t=30, b=10, l=10, r=10), 
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5f5")
        )
        st.plotly_chart(fig, width="stretch")

    st.divider()

    # ===================== SCORE DISTRIBUTION =====================
    st.subheader("📉 Resume Score Distribution")

    fig = px.histogram(
        df, 
        x="resume_score", 
        nbins=10, 
        title="Resume Score Distribution",
        labels={"resume_score": "Score"},
        color_discrete_sequence=["#2563eb"],
        text_auto=True
    )
    fig.update_layout(
        margin=dict(t=30, b=10, l=10, r=10), 
        yaxis_title="Count",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5f5")
    )

    st.plotly_chart(fig, width="stretch")

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
