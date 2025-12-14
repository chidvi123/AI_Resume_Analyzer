from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text:str):
    if not text:
        return None
    
    embedding=_model.encode(text)
    return embedding