import os
import sys
import streamlit as st

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from views.user import user_page
from views.admin import admin_page
from views.feedback import feedback_page
from views.about import about_page

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

def main():
    st.sidebar.title("Navigation")

    page = st.sidebar.selectbox(
        "choose a page",
        ["Home", "User", "Feedback", "Admin","About"]
    )

    if page == "Home":
        st.title("AI Resume Analyzer Pro..")
        st.write("Welcome Dev! Use the Sidebar to navigate.")

    elif page == "User":
        user_page()

    elif page == "Feedback":
       feedback_page()

    elif page == "Admin":
        admin_page()
        
    elif page == "About":
        about_page()

if __name__ == "__main__":
    main()
