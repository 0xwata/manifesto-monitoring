import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin

# Import common utilities from the same directory
from common_scraper_utils import normalize_name, save_data_to_json

SHUGIIN_BASE_URL = "https://www.shugiin.go.jp"

def _get_shugiin_member_details_from_list_page():
    """
    衆議院の議員一覧ページから議員名、会派、選挙区、プロフィールURLを取得する。
    """
    list_url = f"{SHUGIIN_BASE_URL}/internet/itdb_annai.nsf/html/statics/syu/1giin.htm"
    members_data = []
    print(f"Fetching Shugiin member list from {list_url}")
    try:
        response = requests.get(list_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 議員情報が含まれるテーブルを見つける
        # ページ構造に基づき、border="1" のテーブルが該当すると仮定
        table = soup.select_one('table[border="1"]')
        if not table:
            tables = soup.find_all('table')
            if tables:
                table = max(tables, key=lambda t: len(t.find_all('tr'))) # 最も行数の多いテーブルを選択
            else:
                print("Error: Could not find the main member table on Shugiin list page.")
                return []

        rows = table.select('tr')
        
        for i, row in enumerate(rows):
            if i == 0: # Skip header row
                continue
            
            cells = row.select('td')
            if len(cells) < 4: # Name, Furigana, Party, District
                # print(f"Skipping row with insufficient cells: {row.text.strip()}")
                continue

            name_cell = cells[0]
            party_cell = cells[2]
            district_cell = cells[3]
            
            name_link = name_cell.select_one('a')
            if name_link:
                raw_member_name = name_link.text.strip()
                # Clean name: remove trailing "君" or other potential suffixes
                member_name = re.sub(r'君$', '', raw_member_name).strip() 
                
                profile_path = name_link.get('href')
                profile_url = urljoin(list_url, profile_path) if profile_path else ""
                
                party_name = party_cell.text.strip()
                district_name = district_cell.text.strip()
                
                if member_name and party_name and district_name and profile_url:
                    members_data.append({
                        'name': member_name,
                        'party': party_name,
                        'district': district_name,
                        'profileUrl': profile_url,
                        'chamber': '衆議院',
                        'nameKana': '', # Will be fetched from profile page
                        'photoUrl': '', # Will be fetched from profile page
                        'termEnd': '',  # Will be fetched from profile page
                        'id': '' # Will be generated from profile URL later
                    })
                else:
                    print(f"  Skipping row due to missing data: Name='{member_name}', Party='{party_name}', District='{district_name}', URL='{profile_url}'")
            else:
                print(f"  Skipping row, no link found in name cell: {name_cell.text.strip()}")
        
        print(f"Found {len(members_data)} initial member entries from Shugiin list page.")
    except Exception as e:
        print(f"Error scraping Shugiin member list page: {e}")
    return members_data

def scrape_shugiin_profile_details(profile_url):
    """
    衆議院議員の個別プロフィールページから詳細情報（ふりがな、写真URL、任期満了日、ID）を取得する。
    """
    details = {
        'nameKana': '',
        'photoUrl': '',
        'termEnd': '',
        'id': ''
    }
    try:
        # print(f"  Fetching profile: {profile_url}") # Reduced verbosity
        response = requests.get(profile_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # ID (URLから抽出)
        member_id_match = re.search(r'/profile/(\d+)\.html', profile_url)
        if member_id_match:
            details['id'] = f"hr-{member_id_match.group(1)}"
        else: # Fallback if ID pattern not found
            details['id'] = f"hr-{profile_url.split('/')[-1].split('.')[0]}"


        # 議員名とふりがな (h2要素から)
        name_header = soup.select_one('h2')
        if name_header:
            full_name_text = name_header.text.strip()
            name_parts = full_name_text.split('（') # "氏名（ふりがな）" の形式を期待
            # name = name_parts[0].strip() # Name is already known from list page
            if len(name_parts) > 1:
                details['nameKana'] = name_parts[1].replace('）', '').strip()
        
        # 写真URL (Construct based on ID pattern provided by user)
        if details['id']:
            member_numeric_id = details['id'].replace('hr-', '') # Get numeric part
            # Construct the specific URL pattern
            photo_url_path = f"/internet/itdb_giinprof.nsf/html/profile/{member_numeric_id}.jpg/$File/{member_numeric_id}.jpg"
            details['photoUrl'] = urljoin(SHUGIIN_BASE_URL, photo_url_path)
        else:
            details['photoUrl'] = "" # Cannot construct URL without ID

        # 任期満了日 (h2の次のp要素から探すことが多い)
        # プロフィール情報から任期満了日を探す
        profile_text_elements = soup.select('p, div, li') # Check various elements
        for element in profile_text_elements:
            text = element.text.strip()
            term_end_match = re.search(r'任期満了[：:日\s]*((?:令和|平成|昭和)\s?\d{1,2}年\s?\d{1,2}月\s?\d{1,2}日|\d{4}年\s?\d{1,2}月\s?\d{1,2}日)', text)
            if term_end_match:
                details['termEnd'] = term_end_match.group(1).strip()
                break 
        
        time.sleep(0.3) # Rate limiting

    except Exception as e:
        print(f"  Error scraping profile {profile_url}: {e}")
    return details

def main():
    print("Starting House of Representatives scraper...")
    
    # 1. Get initial data (name, party, district, profileUrl) from the list page
    initial_members_data = _get_shugiin_member_details_from_list_page()
    
    if not initial_members_data:
        print("No initial member data found. Exiting.")
        return

    all_representatives_data = []
    
    # 2. For each member, scrape their profile page for additional details
    for member_base_info in initial_members_data:
        print(f"Processing: {member_base_info['name']}")
        profile_details = scrape_shugiin_profile_details(member_base_info['profileUrl'])
        
        # Combine base info with profile details
        full_member_info = {**member_base_info, **profile_details}
        
        # Ensure 'id' is present, even if profile scraping failed partially
        if not full_member_info.get('id') and member_base_info.get('profileUrl'):
             member_id_match = re.search(r'/profile/(\d+)\.html', member_base_info['profileUrl'])
             if member_id_match:
                 full_member_info['id'] = f"hr-{member_id_match.group(1)}"

        all_representatives_data.append(full_member_info)

    # 3. Save the combined data
    save_data_to_json(all_representatives_data, "house_of_representatives.json")
    
    print("House of Representatives scraping complete.")

if __name__ == "__main__":
    main()
