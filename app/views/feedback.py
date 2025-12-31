import streamlit as st
from backend.database.feedback import save_feedback,get_recent_feedback

def feedback_page():
    st.title("Feedback")

    st.write(
        "We’d love to hear your thoughts about this project. "
        "Your feedback helps us improve."
    )

    with st.form("feedback_form"):
        name=st.text_input("Name(optional)")
        email=st.text_input("Email")
        rating=st.slider("Rating",min_value=1,max_value=5,value=5)
        message=st.text_area("Your Feedback(commnets)",height=120)

        submitted=st.form_submit_button("Submit Feedback")

        if submitted:
            if not message.strip():
                st.error("Feedback message cannot be empty..")
            else:
                save_feedback(
                    name=name,
                    email=email,
                    rating=rating,
                    message=message
                )
            st.success("Thankyou for your feedback ! ")
    st.divider()

    st.subheader("What others are saying")

    feedbacks=get_recent_feedback(limit=5)

    if not feedbacks:
        st.info("No feedbacks yet ! Be the first")
    else:
        for fb in feedbacks:
            st.markdown(
                f"""
                <div style="padding:12px; border-radius:8px; border:1px solid #e0e0e0; margin-bottom:10px;">
                    <div style="font-size:18px;">⭐ <b>{fb.get('rating', 0)}/5</b></div>
                    <div style="color:gray; font-size:14px;">
                        {fb.get('name', 'Anonymous')}
                    </div>
                    <div style="margin-top:8px;">
                        {fb.get('message')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
    )
