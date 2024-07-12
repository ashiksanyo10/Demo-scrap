import json
import time
import logging
from helium import start_chrome, write, click, S, find_all, get_driver
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# File paths
input_file_path = 'E:\\Amazon-api\\movie.json'
output_file_path = 'rating.json'

def load_movie_titles(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)['movie_names']

def save_movie_details(movie_details, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(movie_details, file, indent=4, ensure_ascii=False)

def wait_for_element(selector, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if selector.exists():
            return True
        time.sleep(0.5)
    return False

def nz_title_check(movie_names):
    browser = start_chrome('https://www.fvlb.org.nz/', headless=True)

    all_movies_details = []

    for i, movie_name in enumerate(movie_names):
        if i > 0 and i % 10 == 0:
            logging.debug("1 minute of batch break - please wait")
            time.sleep(60)  # 1 minute delay after every batch of 10 movies

        search_title_input = S("#fvlb-input")
        exact_match_checkbox = S("#ExactSearch")
        search_button = S(".submitBtn")

        write(movie_name, into=search_title_input)
        click(exact_match_checkbox)
        click(search_button)

        if not wait_for_element(S('.result-title')):
            all_movies_details.append({
                'is_listed': "No",
                'title_name': movie_name,
                'dir_name': 'N/A',
                'classification': 'N/A',
                'runtime': 'N/A'
            })
            continue

        time.sleep(3)  # 3 seconds delay between each movie search

        movie_links = find_all(S('.result-title'))
        exact_match_found = False

        for link in movie_links:
            if link.web_element.text.strip() == movie_name:
                click(link)
                exact_match_found = True
                break

        if not exact_match_found:
            write('', into=search_title_input)
            click(search_button)

            if not wait_for_element(S('.result-title')):
                all_movies_details.append({
                    'title_name': movie_name,
                    'dir_name': 'N/A',
                    'classification': 'N/A',
                    'runtime': 'N/A'
                })
                continue

            time.sleep(3)  # 3 seconds delay between each movie search

            movie_links = find_all(S('.result-title'))

            for link in movie_links:
                if movie_name.lower() in link.web_element.text.strip().lower():
                    click(link)
                    exact_match_found = True
                    break

        if not exact_match_found:
            all_movies_details.append({
                'title_name': movie_name,
                'dir_name': 'N/A',
                'classification': 'N/A',
                'runtime': 'N/A'
            })
            continue

        if not wait_for_element(S('h1')):
            all_movies_details.append({
                'title_name': movie_name,
                'dir_name': 'N/A',
                'classification': 'N/A',
                'runtime': 'N/A'
            })
            continue

        time.sleep(1)

        page_source = get_driver().page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        movie_details = {}
        title_element = soup.find('h1')
        movie_details['title_name'] = title_element.text.strip() if title_element else 'N/A'

        director_element = soup.find('div', class_='film-director')
        movie_details['dir_name'] = director_element.text.strip().replace('Directed by ', '') if director_element else 'N/A'

        classification_element = soup.find('div', class_='film-classification')
        movie_details['classification'] = classification_element.text.strip() if classification_element else 'N/A'

        runtime_element = soup.find_all('div', class_='film-approved')[1]
        runtime = runtime_element.text.strip().replace('This title has a runtime of ', '').replace(' minutes.', '')
        movie_details['runtime'] = runtime if runtime else 'N/A'

        all_movies_details.append(movie_details)

        browser.back()

    get_driver().quit()

    return all_movies_details

def main():
    start_time = time.time()

    movie_names = load_movie_titles(input_file_path)
    movie_details = nz_title_check(movie_names)
    save_movie_details(movie_details, output_file_path)

    end_time = time.time()
    total_time = end_time - start_time

    logging.info(f"Total time taken: {total_time:.2f} seconds")

if __name__ == '__main__':
    main()
