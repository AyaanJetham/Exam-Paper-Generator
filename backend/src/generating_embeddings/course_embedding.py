from sentence_transformers import SentenceTransformer, util
def course_embedding(data):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    course_embeddings = [
        {
            "id": course["id"],
            "embedding": model.encode(course["text"], convert_to_tensor=True)
        }
        for course in data
    ]
    return course_embeddings
