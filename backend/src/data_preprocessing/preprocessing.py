import json

def load_data(file):
    with open(file, 'r') as file:
        data = json.load(file)
    return data

def extracting_syllabus(data):
  all_courses = []
  for course_id, syllabus in data.items():
    all_courses.append({"id": course_id, "text": syllabus})
  return all_courses