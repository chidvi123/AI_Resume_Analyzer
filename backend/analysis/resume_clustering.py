import numpy as np
from sklearn.cluster import KMeans
from backend.database.user_data import load_all_resumes_for_ml

def cluster_resumes(k=5, random_state=42):
    """
    Cluster resumes using KMeans on stored embeddings.

    Returns:
    - assignments: list of (resume_id, cluster_id)
    - model: trained KMeans model
    """

    resume_ids, embeddings = load_all_resumes_for_ml()

    # Not enough data to cluster
    if len(resume_ids) < k:
        return [], None

    # KMeans expects 2D array
    X = np.array(embeddings)

    model = KMeans(
        n_clusters=k,
        random_state=random_state,
        n_init=10
    )

    cluster_labels = model.fit_predict(X)

    assignments = list(zip(resume_ids, cluster_labels))

    return assignments, model