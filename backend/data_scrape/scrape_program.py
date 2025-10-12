import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# Load the dataframe
cse_data = pd.read_csv("../data/processed/final_data.csv")
# cse_data = df[df['Discipline'].isin(['Computer Science and Engineering', 'Computer Science', 'Electrical Engineering'])]

# Function to scrape data from a single URL
def scrape_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.find('div', class_='previewContent marginTop20')
    return content.get_text(separator="\n") if content else ""

# Scrape data from all URLs and store in a dictionary
scraped_data = {}
for index, row in cse_data.iterrows():
    url = row['url']
    course_id = row['id']
    scraped_data[course_id] = scrape_url(url)

# Save the scraped data to a JSON file
with open('scraped_data.json', 'w') as json_file:
    json.dump(scraped_data, json_file, indent=4)
