from sklearn.cluster import KMeans
from backend.nlp.resume_registry import get_all_resume_entries

def cluster_resumes(n_clusters=3,random_state=42):
    resumes=get_all_resume_entries()

    if len(resumes)<2:
        return []
    
    embeddings=[r["embeddings"] for r in resumes]

    k=min(n_clusters,len(embeddings))

    kmeans=KMeans(n_clusters=k,random_state=random_state,n_init=10)
    labels=kmeans.fit_predict(embeddings)

    for record,label in zip(resumes,labels):
        record["cluster_id"]=int(label)
    
    return labels.tolist()