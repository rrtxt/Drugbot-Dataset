# %%
import requests
import json
from bs4 import BeautifulSoup

# %%
def get_csrf_token(session : requests.Session, url : str):
    response = session.get(url, verify=False)

    if response.status_code != 200:
        print(f"Failed to get the page")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    token_tag = soup.find("meta", {'name': 'csrf-token'})
    if token_tag:
        print(f"CSRF Token: {token_tag.get('content')}")
        return token_tag.get('content')
    else:
        print("CSRF token not found")
        return None

def fetch_datatables_data(total, draw = 1, start = 0):
   # Base URL and endpoints
    base_url = "https://cekbpom.pom.go.id"
    main_page_url = f"{base_url}/produk-obat"
    data_table_url = f"{base_url}/produk-dt/01"

    session = requests.Session()
    
    session.headers.update({
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    })
    
    csrf_token = get_csrf_token(session, main_page_url)
    if not csrf_token:
        return
    
    headers = {
        "X-CSRF-TOKEN": csrf_token,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    
    payload = {
        "draw": "1",
        "start": "0",
        "length": f"{total}",
        "search[value]": "",
        "product_register": "",
        "product_name": "",
        "product_brand": "",
        "product_package": "",
        "product_form": "",
        "ingredients": "",
        "submit_date": "",
        "product_date": "",
        "expire_date": "",
        "manufacturer_name": "",
        "status": "",
        "release_date": ""
    }
    
    response = session.post(data_table_url, data=payload, headers=headers, verify=False)
    if response.status_code == 200:
        try:
            data = response.json()
            print("Data fetced successfully")
            return data
        except Exception as e:
            print("Failed to parse JSON response")
            print(response.text) 
            return None
    else:
        print(f"Request failed to fetch data")
        print(response.text)
        return None

# %%
scrap_data = fetch_datatables_data(total=11572)

# %%
data = scrap_data['data']

# %%
filename = "bpom_drugs.json"
try:
    with open(filename, "w") as file:
        json.dump(data, file, indent=1)
    
    print("Save BPOM json data success")
except json.JSONDecodeError as e:
    print(f"Error save json: {e}")

# %%
with open('bpom_drugs.json') as json_data:
    drugs = json.load(json_data)
    json_data.close()

drugs

# %%
from html import unescape
import re

def extract_data_by_key(json, keys : list[str]):
    result = {}
    # Iterate over all keys and values
    for key, value in json.items():
        if key in keys:
            result[key] = value
    return result

def clean_text_from_html(html_string):
    if not isinstance(html_string, str):
        return ""

    decoded_html = unescape(html_string)
    
    # Remove all HTML tags
    # This regex pattern matches any HTML tag (opening or closing)
    tag_pattern = re.compile(r'<[^>]+>')
    text_without_tags = tag_pattern.sub('', decoded_html)
    
    # Remove extra whitespace
    # Replace multiple spaces, tabs, and newlines with a single space
    clean_text = re.sub(r'\s+', ' ', text_without_tags)
    
    # Trim leading and trailing whitespace
    clean_text = clean_text.strip()
    
    return clean_text

def parse_ingredients(ingredients_html):
    if not ingredients_html or not isinstance(ingredients_html, str):
        return []
    
    # First decode HTML entities
    decoded = unescape(ingredients_html)
    
    # Then split by HTML tags (primarily <br> tags)
    tag_pattern = re.compile(r'<[^>]+>')
    ingredients_parts = tag_pattern.split(decoded)
    
    # Clean each ingredient and filter out empty items
    result = []
    for item in ingredients_parts:
        cleaned = re.sub(r'\s+', ' ', item).strip()
        if cleaned:
            result.append(cleaned.lower())
    
    return result


# %%
def preprocess_bpom_data(drugs, keys_to_extract=None):
    if keys_to_extract is None:
        keys_to_extract = ['ID', 'PRODUCT_NAME', 'PRODUCT_PACKAGE', 'PRODUCT_FORM', 'INGREDIENTS', 'MANUFACTURER_NAME']

    cleaned_drugs = []
    
    # Map BPOM json data for specified keys
    for drug in drugs:
        # Skip if drug is none or not a dictionary
        if not drug or not isinstance(drug, dict):
            continue
        
        mapped_data = extract_data_by_key(drug, keys_to_extract)

        drug_data = {}
        for key, value in mapped_data.items():
        # Process based on key and value type
            if key == 'INGREDIENTS' and value:
                # Parse ingredients into an array instead of just cleaning HTML
                drug_data[key.lower()] = parse_ingredients(value)
            elif isinstance(value, int) or isinstance(value, float):
                # Keep numeric values as-is
                drug_data[key.lower()] = value
            elif isinstance(value, str):
                # Clean and normalize string values
                drug_data[key.lower()] = value.strip().lower()
            else:
                # Handle other types appropriately
                drug_data[key.lower()] = value
        
        if drug_data:
            cleaned_drugs.append(drug_data)
    
    return cleaned_drugs

# %%
cleaned_drugs = preprocess_bpom_data(drugs)

# %%
len(cleaned_drugs)

# %%
filename = "cleaned_bpom_drugs.json"
try:
    with open(filename, "w") as file:
        json.dump(cleaned_drugs, file, indent=1)
    
    print("Save BPOM json data success")
except json.JSONDecodeError as e:
    print(f"Error save json: {e}")


