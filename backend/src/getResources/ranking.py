from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def rank_search_results(syllabus, results):
    # Create a list of snippets from the results
    snippets = [result['snippet'] for result in results]
    
    # Combine syllabus and snippets for vectorization
    corpus = [syllabus] + snippets
    vectorizer = TfidfVectorizer().fit_transform(corpus)

    # Compute cosine similarity between syllabus and snippets
    cosine_similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()

    # Rank the results based on similarity scores
    ranked_results = sorted(zip(cosine_similarities, results), reverse=True, key=lambda x: x[0])
    return ranked_results
