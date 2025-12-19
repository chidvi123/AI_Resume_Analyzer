from backend.nlp.resume_registry import get_all_resume_entries
from backend.nlp.similarity import cosine_similarity

def find_similar_resumes(
        current_embedding,
        top_k=3,
        exclude_self=True
):
     """
     Returns top_k most similar resumes to the current resume
     based on cosine similarity.
     """
     resumes=get_all_resume_entries()
     similarities=[]

     for record in resumes:
          similarity=cosine_similarity(
               current_embedding,
               record["embedding"]
          )

          similarities.append({
               "resume_id":record["resume_id"],
               "experinece_level":record["experience_level"],
               "target_role":record["target_role"],
               "resume_score":record["resume_score"],
               "similarity":similarity
          })

     #sort by similarity (most->least)

     similarities.sort(
          key=lambda x:x["similarity"],
          reverse=True
        )
     
     #remove self match (sim=1.0)
     if exclude_self:
          similarities=[
               s for s in similarities
               if s["similarity"]<0.999
          ]
     return similarities[:top_k]    