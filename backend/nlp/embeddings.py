import streamlit as st
from sentence_transformers import SentenceTransformer

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data(show_spinner=False)
def get_embedding(text: str):
    if not text:
        return None

    model = load_embedding_model()
    return model.encode(text)
