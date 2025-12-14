import numpy as np


def cosine_similarity(vec1,vec2)->float:
    if vec1 is None or vec2 is None:
        return 0.0
    
    vec1=np.array(vec1)
    vec2=np.array(vec2)

    similarity=np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))

    return float(similarity)