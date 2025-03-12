from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(taken_courses, prereqs):
    # Extract descriptions
    taken_descriptions = [course["description"] for course in taken_courses]
    prereq_descriptions = [prereq["description"] for prereq in prereqs]

    if not taken_descriptions or not prereq_descriptions:
        return []

    # Vectorize the text descriptions
    vectorizer = TfidfVectorizer().fit(taken_descriptions + prereq_descriptions)
    taken_vectors = vectorizer.transform(taken_descriptions)
    prereq_vectors = vectorizer.transform(prereq_descriptions)

    # Compute similarity scores
    similarity_matrix = cosine_similarity(prereq_vectors, taken_vectors)

    results = []
    for i, prereq in enumerate(prereqs):
        matched_courses = []
        for j, taken_course in enumerate(taken_courses):
            similarity_score = similarity_matrix[i, j]
            if similarity_score > 0.3:  # Threshold for relevance
                matched_courses.append({
                    "taken_course_code": taken_course["course_code"],
                    "taken_description": taken_course["description"],
                    "similarity_score": round(similarity_score, 2)
                })
        
        results.append({
            "prereq_course_code": prereq["prereq_course_code"],
            "prereq_description": prereq["description"],
            "matched_courses": matched_courses
        })

    return results
