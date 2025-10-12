from preprocessing import load_data, extracting_syllabus
from nlp_task import clean_text
import json

data = load_data("data_scrape/scraped_data.json")
data = extracting_syllabus(data)
for course in data:
    course["text"] = clean_text(course["text"])
with open("data_scrape/cleaned_scraped.json", "w") as file:
    json.dump(data, file)
with open("data_scrape/cleaned_scraped.json" , 'r') as file:
  data = json.load(file)
  print(data)
