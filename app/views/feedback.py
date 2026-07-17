import streamlit as st
from backend.database.feedback import save_feedback, get_recent_feedback


def feedback_page():

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
                >Community</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.title("Feedback")
    st.caption("We'd love to hear your thoughts. Your feedback helps us improve the product.")

    st.divider()

    # ================= FEEDBACK FORM =================
    st.subheader("✍️ Share Your Experience")

    with st.form("feedback_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name (optional)", placeholder="Your name...")
        with col2:
            email = st.text_input("Email (optional)", placeholder="your@email.com")

        rating = st.slider("⭐ Rating", min_value=1, max_value=5, value=5,
                           help="Rate your experience from 1 (poor) to 5 (excellent)")

        stars = "⭐" * rating
        st.markdown(
            f"<div style='font-size:1.4rem; margin:-8px 0 6px;'>{stars}</div>",
            unsafe_allow_html=True
        )

        message = st.text_area("Your Feedback", height=120,
                               placeholder="What did you like? What could be improved?")

        submitted = st.form_submit_button("📩 Submit Feedback", width="stretch")

        if submitted:
            if not message.strip():
                st.error("❌ Feedback message cannot be empty.")
            elif email and "@" not in email:
                st.error("❌ Please enter a valid email address.")
            else:
                save_feedback(
                    name=name,
                    email=email,
                    rating=rating,
                    message=message
                )
                st.success("🎉 Thank you for your feedback! It means a lot.")

    st.divider()

    # ================= RECENT FEEDBACK =================
    st.subheader("💬 What Others Are Saying")

    feedbacks = get_recent_feedback(limit=5)

    if not feedbacks:
        st.markdown(
            """
            <div class="card-auto" style="text-align:center; padding:2.5rem;">
                <div style='font-size:2.5rem; margin-bottom:0.8rem;'>💬</div>
                <p style='color:#64748b;'>No feedback yet. Be the first to share!</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        for fb in feedbacks:
            rating_val = fb.get('rating', 0)
            stars_display = "⭐" * rating_val + "☆" * (5 - rating_val)
            reviewer = fb.get('name', '') or 'Anonymous'
            st.markdown(
                f"""
                <div class="feedback-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                        <div>
                            <div style="font-size:1.1rem; letter-spacing:1px; margin-bottom:3px;">{stars_display}</div>
                            <div style="font-size:13px; font-weight:600; color:#94a3b8;">{reviewer}</div>
                        </div>
                        <div style="font-size:11px; color:#475569; background:rgba(99,102,241,0.08);
                                    padding:3px 10px; border-radius:999px; border:1px solid rgba(99,102,241,0.15);">
                            {rating_val}/5
                        </div>
                    </div>
                    <div style="color:#cbd5e1; font-size:14px; line-height:1.65;">
                        {fb.get('message')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


