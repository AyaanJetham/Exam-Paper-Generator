import requests
from dotenv import load_dotenv
import os

def search_courses_on_google(query):
    if not query:
        print("Query is empty!")
        return []
    load_dotenv()
    google_api_key = os.getenv("SEARCH_API")
    cse_id = '867ed41383a6f492d'
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={google_api_key}&cx={cse_id}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        results = response.json()

        if 'items' not in results:
            print("No results found in the response.")
            return []

        courses = []
        for item in results.get('items', []):
            course_info = {
                'title': item.get('title', 'No Title'),
                'link': item.get('link', 'No Link'),
                'snippet': item.get('snippet', 'No Snippet')
            }
            courses.append(course_info)

        if not courses:
            print("No courses found for the query.")

        return courses

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []