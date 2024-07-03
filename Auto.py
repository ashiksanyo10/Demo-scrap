from helium import start_chrome, go_to, write, press, find_all, S, kill_browser
import json
import time
import random

# Base URL for the classification website
base_url = 'https://www.classification.gov.au'

# Function to search for a movie
def search_movie(title):
    # Start the browser and go to the main page
    browser = start_chrome(base_url)
    
    # Allow some time for the page to load
    time.sleep(random.uniform(2, 5))
    
    # Enter the title in the search box and press Enter
    write(title, into='Search for a film, game or publication')
    press(ENTER)
    
    # Allow some time for the search results to load
    time.sleep(random.uniform(3, 6))
    
    # Print the titles found on the search results page
    movie_links = find_all(S('.c-classifiction-title__text'))
    for link in movie_links:
        print(link.web_element.text)
    
    # Close the browser
    kill_browser()

def main():
    # Read input JSON file
    with open('input.json', 'r') as f:
        data = json.load(f)
        titles = [item['Title_name'] for item in data['Data']]
    
    for title in titles:
        print(f"Searching for movie: {title}")
        search_movie(title)
        # Add a delay between searches to mimic human interaction
        time.sleep(random.uniform(5, 10))

if __name__ == '__main__':
    main()
