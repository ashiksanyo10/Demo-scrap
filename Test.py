import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Load movie titles from JSON file
with open('input.json', 'r') as file:
    movie_titles = json.load(file)

# Setup Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run headless Chrome for faster execution
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Base URL of the classification website
base_url = 'https://www.classification.gov.au'

# Initialize results list
results = []

# Function to scrape movie details
def scrape_movie_details(title):
    driver.get(base_url)
    search_box = driver.find_element(By.NAME, 'query')
    search_box.send_keys(title)
    search_box.send_keys(Keys.RETURN)
    
    time.sleep(2)  # Wait for the search results to load
    
    try:
        # Click on the first search result link
        first_result = driver.find_element(By.CSS_SELECTOR, 'h2 a')
        first_result.click()
        
        time.sleep(2)  # Wait for the movie page to load
        
        # Parse the movie page content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract industry details
        industry_details = soup.find('div', {'id': 'industry-details'})
        
        is_listed = "Yes" if industry_details else "No"
        title_name = title
        director_name = industry_details.find('span', {'class': 'director-name'}).text if industry_details.find('span', {'class': 'director-name'}) else "N/A"
        producer_name = industry_details.find('span', {'class': 'producer-name'}).text if industry_details.find('span', {'class': 'producer-name'}) else "N/A"
        classification = industry_details.find('span', {'class': 'classification'}).text if industry_details.find('span', {'class': 'classification'}) else "N/A"
        consumer_advice = industry_details.find('span', {'class': 'consumer-advice'}).text if industry_details.find('span', {'class': 'consumer-advice'}) else "N/A"
        
        # Add the details to results
        results.append({
            "is_listed": is_listed,
            "title_name": title_name,
            "director_name": director_name,
            "producer_name": producer_name,
            "classification": classification,
            "consumer_advice": consumer_advice
        })
        
    except Exception as e:
        print(f"Error fetching details for {title}: {e}")

# Iterate through the movie titles and fetch details
for title in movie_titles:
    scrape_movie_details(title)
    time.sleep(10)  # Delay to avoid overloading the website

# Print or save the results
print(results)

# Close the browser
driver.quit()
