# returning the top 7 relevant courses 

def rate_courses(score):
    most_relevant_course = sorted(score, key=lambda x: x["similarity"], reverse = True)
    top_courses = most_relevant_course[:8]
    return top_courses
    # for i, course in enumerate(top_courses, 1):
    #     print(f"Rank {i}: Course ID = {course['course_id']} | Similarity = {course['similarity']:.2f}")
