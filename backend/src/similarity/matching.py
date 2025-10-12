from sentence_transformers import util
def computing_similarity(user_syllabus, course_syllabus):
    similarities = [
        { 
            "course_id": course["id"],
            "similarity": util.cos_sim(user_syllabus, course["embedding"]).item()
        }
        for course in course_syllabus
    ]
    return similarities #returns course id and also their similarity score
    #score close to 1 says that course is relevant to the user syllabus
