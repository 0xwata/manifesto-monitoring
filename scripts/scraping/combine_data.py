import json
from pathlib import Path

# Import common utilities from the same directory
from common_scraper_utils import save_data_to_json

def main():
    print("Combining data from House of Representatives and House of Councilors...")
    
    # Use PROJECT_ROOT defined in common_scraper_utils
    from common_scraper_utils import PROJECT_ROOT
    data_dir = PROJECT_ROOT / "data" # Define data_dir based on project root
    
    representatives_file = data_dir / "house_of_representatives.json"
    councilors_file = data_dir / "house_of_councilors.json"
    combined_file = data_dir / "politicians.json"
    
    house_of_representatives_data = []
    if representatives_file.exists():
        with open(representatives_file, 'r', encoding='utf-8') as f:
            house_of_representatives_data = json.load(f)
        print(f"Loaded {len(house_of_representatives_data)} members from {representatives_file}")
    else:
        print(f"Warning: {representatives_file} not found.")
        
    house_of_councilors_data = []
    if councilors_file.exists():
        with open(councilors_file, 'r', encoding='utf-8') as f:
            house_of_councilors_data = json.load(f)
        print(f"Loaded {len(house_of_councilors_data)} members from {councilors_file}")
    else:
        print(f"Warning: {councilors_file} not found.")
        
    all_politicians = house_of_representatives_data + house_of_councilors_data
    
    if all_politicians:
        # Use the updated save_data_to_json from common utils
        # It now calculates the path relative to PROJECT_ROOT internally
        save_data_to_json(all_politicians, "politicians.json") 
    else:
        print("No data to combine. politicians.json not created/updated.")
        
    print("Data combining complete.")

if __name__ == "__main__":
    main()
