from flask import Flask, request, jsonify
import time
from helium import start_chrome, write, click, S, find_all, get_driver
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/api/nz-title-check', methods=['POST'])
def nz_title_check():
    try:
        input_data = request.get_json()

        if not input_data or 'movie_names' not in input_data or not isinstance(input_data['movie_names'], list):
            return jsonify({'error': 'Invalid JSON request format. Expected {"movie_names": ["Movie Title 1", "Movie Title 2", ...]}'}, 400)

        movie_names = input_data['movie_names']

        browser = start_chrome('https://www.fvlb.org.nz/', headless=True)

        all_movies_details = []

        for movie_name in movie_names:
            search_title_input = S("#fvlb-input")  
            exact_match_checkbox = S("#ExactSearch")
            search_button = S(".submitBtn")

            write(movie_name, into=search_title_input)
            click(exact_match_checkbox)
            click(search_button)

            wait_for_element(search_title_input)
            time.sleep(1)

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

                wait_for_element(search_title_input) 
                time.sleep(1)

                movie_links = find_all(S('.result-title'))

                for link in movie_links:
                    if movie_name.lower() in link.web_element.text.strip().lower():
                        click(link)
                        exact_match_found = True
                        break

            if not exact_match_found:
                all_movies_details.append({'movie_name': movie_name, 'error': f'No exact match found for the movie: {movie_name}'})
                continue

            wait_for_element(S('h1')) 
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

        return jsonify(all_movies_details), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def wait_for_element(selector, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if selector.exists:
            return True
        time.sleep(0.5)
    return False

if __name__ == '__main__':
    app.run(port=8080, debug=True)

