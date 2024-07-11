import json

def convert_to_json(file_path):
    try:
        with open(file_path, 'r') as file:
            movie_titles = file.read().splitlines()
        
        json_data = {
            "movies_name": movie_titles
        }
        
        json_output_path = file_path.replace('.txt', '.json')
        
        with open(json_output_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        
        print(f"JSON file created successfully at: {json_output_path}")
    
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
txt_file_path = 'movies.txt'  # Replace with the path to your text file
convert_to_json(txt_file_path)
