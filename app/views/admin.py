import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
                st.rerun()   # 🔥 IMPORTANT FIX
            else:
                st.error("Incorrect password")

        return  # stop rendering rest of admin page
    
    if st.button("Logout"):
        st.session_state["admin_authenticated"]=False
        st.success("Logged out")
        st.stop()

    # -------- AUTHENTICATED ADMIN BELOW --------

    data = st.session_state.get("admin_analytics", [])

    st.write("Total resumes analyzed:", len(data))

    if data:
        st.dataframe(data)

        # summary metrics
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

        # charts
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

        # CSV export
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False)

        st.download_button(
            label="Download Analytics CSV",
            data=csv,
            file_name="admin_analytics.csv",
            mime="text/csv"
        )

    else:
        st.info("No analytics data available yet.")
