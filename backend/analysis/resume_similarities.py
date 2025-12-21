import numpy as np
from backend.database.user_data import load_all_resumes_for_ml
from backend.nlp.similarity import cosine_similarity


def get_top_k_similar_resumes(query_embedding, k=5):
    """
    Returns top-K most similar resumes from DB (excluding itself).

    Args:
        query_embedding: list or np.array (embedding of one resume)
        k: number of neighbors

    Returns:
        List of tuples: (resume_id, similarity_score)
    """

    resume_ids, embeddings = load_all_resumes_for_ml()

    if len(resume_ids) == 0:
        return []

    query_vec = np.array(query_embedding)

    scores = []
    for rid, emb in zip(resume_ids, embeddings):
        score = cosine_similarity(query_vec, emb)
        scores.append((rid, score))

    # sort by similarity (high → low)
    scores.sort(key=lambda x: x[1], reverse=True)

    # exclude self-match (score ≈ 1.0)
    filtered = [s for s in scores if s[1] < 0.999]

    return filtered[:k]
