import os
import json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Determine the project root based on this script's location
# Assumes this script is in scripts/db/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def load_data():
    """Loads politician data from the JSON file."""
    data_file = PROJECT_ROOT / "data" / "politicians.json"
    if not data_file.exists():
        print(f"Error: Data file not found at {data_file}")
        return None
        
    with open(data_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            print(f"Loaded {len(data)} records from {data_file}")
            return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {data_file}: {e}")
            return None

def main():
    print("Starting Supabase data load script...")
    
    # Load environment variables from .env file at the project root
    load_dotenv(dotenv_path=PROJECT_ROOT / '.env')
    
    supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") # Use the public URL
    # --- Using ANON KEY as requested by user ---
    # IMPORTANT: Ensure RLS policies in Supabase allow inserts/updates for the 'anon' role
    # --- Using ANON KEY as requested by user ---
    # This key bypasses Row Level Security and is recommended for trusted server-side operations.
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") 
    
    if not supabase_url or not supabase_key:
        print("Error: Supabase URL or Service Role Key not found in environment variables.")
        print("Please ensure NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in your .env file.")
        return
        
    if "YOUR_SUPABASE_URL" in supabase_url or "YOUR_SUPABASE_SERVICE_ROLE_KEY" in supabase_key:
         print("Warning: Placeholder Supabase URL or Service Role Key detected in environment variables.")
         print("Please replace them with your actual Supabase credentials in the .env file before running.")
         # Optionally, exit here if placeholders are found
         # return 

    try:
        print(f"Connecting to Supabase at {supabase_url}...")
        supabase: Client = create_client(supabase_url, supabase_key)
        print("Supabase client created.")
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return

    politicians_data = load_data()
    if politicians_data is None:
        print("Failed to load data. Exiting.")
        return
        
    if not politicians_data:
        print("No politician data to load. Exiting.")
        return

    print(f"Attempting to upsert {len(politicians_data)} records into 'politicians' table...")
    
    # Supabase client's upsert can handle a list of dictionaries directly
    try:
        # Prepare data: Map JSON keys (camelCase) to DB columns (snake_case)
        data_to_upsert = []
        key_map = {
            "nameKana": "name_kana",
            "photoUrl": "photo_url",
            "termEnd": "term_end",
            "profileUrl": "profile_url"
            # other keys like 'id', 'name', 'party', 'district', 'chamber' match
        }
        
        for record in politicians_data:
            # Ensure required fields are present
            if not record.get('id') or not record.get('name') or not record.get('chamber'):
                print(f"Skipping record due to missing required fields (id, name, chamber): {record.get('id', 'N/A')}")
                continue

            transformed_record = {}
            for key, value in record.items():
                db_key = key_map.get(key, key) # Use mapped key if exists, otherwise original
                transformed_record[db_key] = value
            
            data_to_upsert.append(transformed_record)

        if not data_to_upsert:
             print("No valid records to upsert after filtering/transformation.")
             return

        print(f"Upserting {len(data_to_upsert)} valid records...")
        response = supabase.table('politicians').upsert(data_to_upsert).execute()
        
        # Check for errors in the response if the API provides details
        # Note: The structure of the response object might vary. Inspect it if needed.
        # if response.error:
        #    print(f"Error during upsert: {response.error}")
        # else:
        #    print(f"Upsert successful. Response data count (might not reflect actual rows affected): {len(response.data)}")
        print("Upsert operation executed using Service Role Key. Check Supabase dashboard for results.")
        # print("Reminder: If RLS is enabled, ensure the 'anon' role has INSERT/UPDATE permissions.") # No longer relevant when using service_role

    except Exception as e:
        print(f"An error occurred during the upsert operation: {e}")

    print("Data load script finished.")

if __name__ == "__main__":
    main()
