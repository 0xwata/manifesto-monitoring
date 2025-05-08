import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin

# Import common utilities from the same directory
from common_scraper_utils import normalize_name, save_data_to_json

SANGIIN_BASE_URL = "https://www.sangiin.go.jp"

def scrape_councilor_profile(name, profile_url, party_from_list, district_from_list):
    """
    参議院議員の個別プロフィールページから詳細情報を取得する。
    Party and district are passed from the list page scraping.
    """
    details = {
        'id': '',
        'name': name, # Name from list page
        'nameKana': '',
        'photoUrl': '',
        'party': party_from_list, # Party from list page
        'district': district_from_list, # District from list page
        'chamber': '参議院',
        'termEnd': '',
        'profileUrl': profile_url
    }
    try:
        # print(f"    Fetching Sangiin profile: {profile_url} for {name}")
        response = requests.get(profile_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # ID (URLから抽出)
        member_id_match = re.search(r'/profile/(\d+)\.htm', profile_url)
        if member_id_match:
            details['id'] = f"hc-{member_id_match.group(1)}"
        else: # Fallback
            id_from_url = profile_url.split('/')[-1].replace('.htm','').replace('.html','')
            details['id'] = f"hc-{id_from_url}"


        # ふりがな (Refined selectors)
        name_kana_element = soup.select_one('.kana, .furigana, span.fsSmall') # Common classes for furigana
        if name_kana_element:
            details['nameKana'] = name_kana_element.text.strip()
        if not details['nameKana']:
             # Try text in parentheses next to the main name heading if available
             name_heading = soup.find(lambda tag: tag.name in ['h1', 'h2', 'h3'] and name in tag.text)
             if name_heading:
                  kana_match = re.search(r'（(.+?)）', name_heading.text)
                  if kana_match:
                       details['nameKana'] = kana_match.group(1).strip()
        
        # 写真URL (Construct based on ID pattern)
        if details['id']: # Ensure we have an ID
             member_numeric_id = details['id'].replace('hc-', '') # Get numeric part
             details['photoUrl'] = f"{SANGIIN_BASE_URL}/japanese/joho1/kousei/giin/photo/g{member_numeric_id}.jpg"
        else:
             details['photoUrl'] = "" # Cannot construct URL without ID

        # 選挙区はリストページから取得するので、ここでは主に任期満了日をプロフィールから取得
        # 任期満了日
        # Profile pages vary, try common patterns
        term_text_elements = soup.select('td, th, p, span, div') # Search in various elements
        for element in term_text_elements:
            text_content = element.text.strip()
            if '任期満了' in text_content:
                term_match = re.search(r'任期満了\s*[:：]?\s*((?:令和|平成|昭和)\s?\d{1,2}年\s?\d{1,2}月\s?\d{1,2}日|\d{4}年\s?\d{1,2}月\s?\d{1,2}日)', text_content)
                if term_match:
                    details['termEnd'] = term_match.group(1).strip()
                    break # Found term end
        
        # If not found in specific elements, try a broader search in the page text
        if not details['termEnd']:
            page_text = soup.get_text()
            term_match = re.search(r'任期満了\s*[:：]?\s*((?:令和|平成|昭和)\s?\d{1,2}年\s?\d{1,2}月\s?\d{1,2}日|\d{4}年\s?\d{1,2}月\s?\d{1,2}日)', page_text)
            if term_match:
                details['termEnd'] = term_match.group(1).strip()
        
        time.sleep(0.3) # Rate limiting

    except Exception as e:
        print(f"    Error scraping Sangiin profile {profile_url} for {name}: {e}")
    return details

def main():
    print("Starting House of Councilors scraper...")
    # 参議院議員一覧ページ (URLは会期によって変わる可能性があるので注意)
    # 例: 第217回国会 (常会) (令和7年1月24日～ )
    list_url = f"{SANGIIN_BASE_URL}/japanese/joho1/kousei/giin/217/giin.htm" 
    # Consider making this URL configurable or dynamically found if it changes often.
    # For now, using the one that was problematic.
    
    all_councilors_data = []
    
    try:
        print(f"Fetching House of Councilors member list from {list_url}")
        response = requests.get(list_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # The main table seems to be identifiable by class or structure.
        # Based on inspection, a common class is 'tb_giinlist'.
        # Let's try a more specific selector first, then fall back.
        main_table = soup.select_one('table.tb_giinlist, table.giinIchiran, table[summary*="議員一覧"]')
        
        if not main_table:
            # Fallback: find tables that look like member lists (e.g., have '氏名' in header)
            all_tables = soup.select('table')
            for t in all_tables:
                if t.find('th', string=re.compile(r'氏\s*名')): # Check for "氏名" in header
                    main_table = t
                    break
        
        if not main_table:
            print("Error: Could not find the main member table on Sangiin list page.")
            return

        rows = main_table.select('tr')
        
        # Skip the first row if it's a header (usually contains th)
        start_row_index = 0
        if rows and rows[0].select('th'):
            start_row_index = 1

        for i in range(start_row_index, len(rows)):
            row = rows[i]
            cells = row.select('td')
            
            # Expecting at least 4 cells: Name, Kana, Party, District
            if len(cells) < 4:
                # print(f"  Skipping row with less than 4 cells: {row.text.strip()}")
                continue

            name_cell = cells[0]
            # kana_cell = cells[1] # Kana is often on profile page, list page might be less reliable
            party_cell = cells[2]
            district_cell = cells[3]
            # term_cell = cells[4] if len(cells) > 4 else None #任期満了

            name_link = name_cell.select_one('a')
            if name_link:
                raw_name = name_link.text.strip()
                # Clean name: remove [正字], [ホームページ] etc.
                member_name = re.sub(r'\s*\[.*?\]\s*', '', raw_name).strip()

                if not member_name or len(member_name) < 2 or member_name.endswith('行'):
                    continue

                profile_path = name_link.get('href')
                if not profile_path:
                    continue
                
                profile_url = urljoin(list_url, profile_path)
                
                party_name = party_cell.text.strip()
                district_name = district_cell.text.strip()
                # term_end_from_list = term_cell.text.strip() if term_cell else ""

                if member_name and party_name and district_name:
                    print(f"  Processing Sangiin member from list: {member_name} (Party: {party_name}, District: {district_name})")
                    
                    # Scrape profile for additional details (kana, photo, more reliable term end)
                    # Pass party and district from list, as they are reliable here.
                    profile_details = scrape_councilor_profile(member_name, profile_url, party_name, district_name)
                    
                    # Combine list data with profile data
                    # Profile data will overwrite if it finds better info (e.g. termEnd)
                    # but keeps party/district from list.
                    combined_info = {
                        'id': profile_details.get('id',''),
                        'name': member_name,
                        'nameKana': profile_details.get('nameKana',''),
                        'photoUrl': profile_details.get('photoUrl',''),
                        'party': party_name, # From list
                        'district': district_name, # From list
                        'chamber': '参議院',
                        'termEnd': profile_details.get('termEnd',''), # Prefer from profile if found
                        'profileUrl': profile_url
                    }
                    all_councilors_data.append(combined_info)
                else:
                    print(f"  Skipping row due to missing name, party, or district: {row.text.strip()}")
            # else:
                # print(f"  Skipping row, no link in name cell: {name_cell.text.strip()}")

        if not all_councilors_data:
             print("Warning: No Sangiin members were scraped after processing. Check selectors and page structure.")

    except Exception as e:
        print(f"Error during House of Councilors list scraping: {e}")

    save_data_to_json(all_councilors_data, "house_of_councilors.json")
    print("House of Councilors scraping complete.")

if __name__ == "__main__":
    main()
