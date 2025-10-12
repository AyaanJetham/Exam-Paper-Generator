from sentence_transformers import SentenceTransformer, util

def user_syllabus_embedding(content):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    syllabus_embedding = model.encode(content, convert_to_tensor=True)
    return syllabus_embedding



