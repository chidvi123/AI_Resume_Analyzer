import streamlit as st

def admin_page():
    st.title("Admin Dashboard")
    st.write("System-level analytics amd insights")

    data = st.session_state.get("admin_analytics",[])

    st.write("Total resume analyzed :",len(data))

    if data:
        st.dataframe(data)
    else:
        st.info("No analytics data available yet.")


    if data:
        total=len(data)

        avg_score=sum(d["resume_score"] for d in data)/total

        experience_counts={}
        role_counts={}

        for d in data:
            experience_counts[d['experience_level']]=experience_counts.get(d["experience_level"],0)+1
            role_counts[d["target_role"]]=role_counts.get(d["target_role"],0)+1

        st.subheader("Summary metrics")
        st.write(f"Average Resume Score: {round(avg_score, 2)}")

        st.write("Experience Level Distribution")
        st.write(experience_counts)

        st.write("Target Job Role Distribution")
        st.write(role_counts)
