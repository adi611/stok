import requests
import time
from bs4 import BeautifulSoup
import json

# URL of the website
url = "https://economictimes.indiatimes.com/markets/stocks/news"

# Send a GET request to the URL
response = requests.get(url)

# print(str(response.text))

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# Locate the target elements based on the specified structure
each_story_divs = soup.select('body main.pageHolder div.main_container section.section_list div.tabdata div.eachStory')

# Iterate through each 'eachStory' div and extract title and time
for each_story_div in each_story_divs:
    # Extract title
    title = each_story_div.find('h3').find('a').text.strip()

    # Extract time
    time = each_story_div.find('time').text.strip()

    # Print or store the extracted data
    print(f'Title: {title}, Time: {time}')
