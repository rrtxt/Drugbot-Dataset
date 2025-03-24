# %%
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time, datetime
import re
import os
import json

# %%
checkpoint_filename = os.getenv("DRUG_CHECKPOINT_FILENAME")

# %%
df = pd.read_excel(checkpoint_filename)
df

# %%
def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
        
    print(f"Saved JSON into {filename}")


def date_to_epoch(date_str=None, date_format="%Y-%m-%d %H:%M:%S"):
    """
    Convert a date string to an epoch timestamp.
    If no date string is provided, return the current epoch time.

    :param date_str: The date string (e.g., "2025-02-21 15:30:00"), or None for the current time.
    :param date_format: The format of the date string (default: "%Y-%m-%d %H:%M:%S").
    :return: The epoch timestamp as an integer.
    """
    if date_str is None:
        return int(time.time())  # Current epoch time
    
    dt = datetime.datetime.strptime(date_str, date_format)
    return int(time.mktime(dt.timetuple()))

def epoch_to_date(epoch, date_format="%Y-%m-%d %H:%M:%S"):
    """
    Convert an epoch timestamp to a human-readable date string.

    :param epoch: The epoch timestamp (e.g., 1740000000)
    :param date_format: The desired output format (default: "%Y-%m-%d %H:%M:%S")
    :return: A formatted date string
    """
    dt = datetime.datetime.fromtimestamp(epoch)
    return dt.strftime(date_format)

def save_checkpoint(df, data, index):
    last_drug = df.loc[index-1]
    checkpoint_data = {
        "data" : data,
        "last-drug" : last_drug
    }

    scrap_name = f"scrap-{date_to_epoch()}"
    scrap_json = {
        scrap_name : checkpoint_data
    }

    save_json("drug_checkpoint.json", scrap_json)
    return

# %%
# Initialize drugs_data
checkpoint_json = os.getenv("DRUG_CHECKPOINT_JSON")

# Check if json checkpoint exists
if os.path.exists(checkpoint_json):
    with open(checkpoint_json, "r") as file:
        try:
            drugs_data = json.load(file)
            print(f"Success read json")
        except json.JSONDecodeError as e:
            print(f"Error : {e}")
            
else:
    drugs_data = []
    
# drugs_data

checkpoint_json

# %%
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

scrapped_data = []

for i, row in df.iterrows():
    # Check if current drug has already been scrapped
    if row['isScrapped'] == True:
        continue
    
    url = f"https://www.drugs.com{row['drugLink']}"
    try:
        response = requests.get(url, timeout=10)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser') 
            
            # Regex pattern to match attributes starting with "content"
            pattern = re.compile('content', re.IGNORECASE)
            
            # Find the div with pattern
            drug_content = soup.find('div', id=pattern)
            
            # Remove first div child
            content_head = drug_content.find('div', class_="ddc-main-content-head")
            if content_head is not None:
                content_head.decompose()
            
            # Replace all whitespace (including newlines) with a single space
            cleaned_text = re.sub(r'\s+', ' ', drug_content.text).strip()
            
            # Create and insert drug object
            drug_data = {
                "drugName" : row['drugName'],
                "content" : cleaned_text
            }
            
            # drug_data = {
            #     row['drugName'] : {
            #         "content" : cleaned_text
            #     }
            # }
            drugs_data.append(drug_data)
            
            # Update isScrapped on current row
            df.loc[df.drugName == row['drugName'], 'isScrapped'] == True
            
            print(f"Success scrap {row['drugName']}")
        else:
            # last_drug = df.loc[i-1]
            # checkpoint_data = {
            #     "data" : scrapped_data,
            #     "last-drug" : last_drug
            # }

            # scrap_name = f"scrap-{date_to_epoch()}"
            # scrap_json = {
            #     scrap_name : checkpoint_data
            # }

            # save_json("drug_checkpoint.json", scrap_json)
            df.to_excel("drug_scrapper_checkpoint.xlsx", index=False)
            save_json(checkpoint_json, drugs_data) 
            print(f"Error fetching {url}") 
    except requests.exceptions.RequestException as e:
        df.to_excel("drug_scrapper_checkpoint.xlsx", index=False)
        save_json(checkpoint_json, drugs_data) 
        print(f"Request failed: {e}")
    except:
        df.to_excel("drug_scrapper_checkpoint.xlsx", index=False)
        save_json(checkpoint_json, drugs_data)    
        print('An exception occurred')
    
    time.sleep(1)
    
df.to_excel("drug_scrapper_checkpoint.xlsx", index=False)
save_json(checkpoint_json, drugs_data)


# %%



