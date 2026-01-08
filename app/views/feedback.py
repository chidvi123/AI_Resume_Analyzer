import streamlit as st
from backend.database.feedback import save_feedback, get_recent_feedback


def feedback_page():
    st.title("💬 Feedback")

    st.write(
        "We’d love to hear your thoughts about this project. "
        "Your feedback helps us improve."
    )

    # ================= FEEDBACK FORM =================
    with st.form("feedback_form"):
        name = st.text_input("Name (optional)")
        email = st.text_input("Email (optional)")

        st.info("Use the slider to give a rating.")
        rating = st.slider("Rating", min_value=1, max_value=5, value=5)

        message = st.text_area("Your Feedback (comments)", height=120)

        submitted = st.form_submit_button("Submit Feedback")

        if submitted:
            if not message.strip():
                st.error("Feedback message cannot be empty.")
            elif email and "@" not in email:
                st.error("Please enter a valid email address.")
            else:
                save_feedback(
                    name=name,
                    email=email,
                    rating=rating,
                    message=message
                )
                st.success("Thank you for your feedback!")

    st.divider()

    # ================= RECENT FEEDBACK =================
    st.subheader("What others are saying")

    feedbacks = get_recent_feedback(limit=5)

    if not feedbacks:
        st.info("No feedback yet. Be the first to share!")
    else:
        for fb in feedbacks:
            st.markdown(
                f"""
                <div class="card-auto" style="margin-bottom: 12px;">
                    <div style="font-size:18px;">⭐ <b>{fb.get('rating', 0)}/5</b></div>
                    <div style="color: #94a3b8; font-size:14px;">
                        {fb.get('name', 'Anonymous')}
                    </div>
                    <div style="margin-top:8px;">
                        {fb.get('message')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
