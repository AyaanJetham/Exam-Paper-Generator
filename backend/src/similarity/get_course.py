import csv
def load_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]


def get_course_info(courses_data, course_id):
    for course in courses_data:
        if course['id'] == course_id:
            return course
    return None
