import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Base URL for the classification website
base_url = 'https://www.classification.gov.au'

def fetch_movie_details(title):
    # Set up the browser (make sure you have geckodriver or chromedriver in your PATH)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless Chrome
    browser = webdriver.Chrome(options=options)

    try:
        # Go to the search page
        browser.get(f'{base_url}/search/title')

        # Enter the title in the search box and press Enter
        search_box = browser.find_element(By.NAME, 'search')
        search_box.send_keys(title)
        search_box.send_keys(Keys.RETURN)

        # Wait for the results to load and display the links
        WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.c-classifiction-title__text')))

        # Find the relevant movie link and click it
        movie_links = browser.find_elements(By.CSS_SELECTOR, '.c-classifiction-title__text')
        for link in movie_links:
            if title.lower() in link.text.lower():
                link.click()
                break

        # Wait for the movie details page to load
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.content-bottom')))

        # Extract the required details from the page
        details = {
            'title': title,
            'is_listed': True,
            'classification_date': browser.find_element(By.CSS_SELECTOR, 'div.field--name-field-date').text if element_exists(browser, By.CSS_SELECTOR, 'div.field--name-field-date') else 'N/A',
            'year_of_production': browser.find_element(By.CSS_SELECTOR, 'div.field--name-field-year-of-production').text if element_exists(browser, By.CSS_SELECTOR, 'div.field--name-field-year-of-production') else 'N/A',
            'classification': browser.find_element(By.CSS_SELECTOR, 'div.field--name-field-consumer-advice').text if element_exists(browser, By.CSS_SELECTOR, 'div.field--name-field-consumer-advice') else 'N/A',
            'category': browser.find_element(By.CSS_SELECTOR, 'div.field--name-field-category-detail').text if element_exists(browser, By.CSS_SELECTOR, 'div.field--name-field-category-detail') else 'N/A',
            'duration': browser.find_element(By.CSS_SELECTOR, 'div.field--name-field-duration').text if element_exists(browser, By.CSS_SELECTOR, 'div.field--name-field-duration') else 'N/A',
            'producer': browser.find_element(By.CSS_SELECTOR, 'div.field--name-field-producer').text if element_exists(browser, By.CSS_SELECTOR, 'div.field--name-field-producer') else 'N/A',
            'director_creator': browser.find_element(By.CSS_SELECTOR, 'div.field--name-field-director').text if element_exists(browser, By.CSS_SELECTOR, 'div.field--name-field-director') else 'N/A'
        }
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error fetching details for {title}: {e}")
        details = {
            'title': title,
            'is_listed': False,
            'classification_date': 'N/A',
            'year_of_production': 'N/A',
            'classification': 'N/A',
            'category': 'N/A',
            'duration': 'N/A',
            'producer': 'N/A',
            'director_creator': 'N/A'
        }
    finally:
        # Close the browser
        browser.quit()

    return details

def element_exists(browser, by, value):
    try:
        browser.find_element(by, value)
    except NoSuchElementException:
        return False
    return True

def process_json_input(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data['Data']

def main():
    # Read input JSON file
    data = process_json_input('input.json')

    results = []
    delay = 10  # Initial delay between requests
    for item in data:
        title = item['Title_name']
        try:
            details = fetch_movie_details(title)
            results.append(details)
            print(f"Fetched details for {title}")
        except Exception as e:
            print(f"Error fetching details for {title}: {e}")
            delay *= 2  # Exponential backoff in case of errors
            if delay > 60:  # Cap the delay to avoid extremely long waits
                delay = 60
        else:
            delay = max(10, delay / 2)  # Decrease the delay if no errors occur
        time.sleep(random.uniform(delay, delay + 5))  # Randomized delay to respect server load

    # Print the results
    for result in results:
        print(json.dumps(result, indent=4))

if __name__ == '__main__':
    main()
