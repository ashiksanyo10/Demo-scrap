import json
import pandas as pd

# File paths
input_json_file = 'ratings.json'  # Change this to the path of your input JSON file
output_excel_file = 'ratings.xlsx'  # Change this to the desired path of your output Excel file

def json_to_excel(input_json_path, output_excel_path):
    # Read JSON data from file
    with open(input_json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Create a DataFrame from the JSON data
    df = pd.DataFrame(data)
    
    # Write the DataFrame to an Excel file
    df.to_excel(output_excel_path, index=False)

def main():
    json_to_excel(input_json_file, output_excel_file)
    print(f"Successfully converted {input_json_file} to {output_excel_file}")

if __name__ == '__main__':
    main()
