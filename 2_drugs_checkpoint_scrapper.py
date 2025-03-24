# %%
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

# %%
checkpoint_filename = os.getenv("DRUG_INITIAL_CHECKPOINT_FILENAME") 

# %%
df = pd.read_excel(checkpoint_filename)
df

# %%
initials = df['Initial']
initials

# %%
drug_names : list = []
drug_links : list = []

# %%
for initial in initials:
    initial = initial.lower()
    url = f"https://www.drugs.com/alpha/{initial}.html"
    response = requests.get(url)
    if response.status_code == 200:
        # Get the <ul> contain drugs list
        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.find('main')
        drug_list = main_content.select_one('div#content > ul')
        if drug_list is None:
            print(f"Cannot get {initial} drug list")
            continue
            
        print(f"Get {initial} drug list")
        
        # Get each drug its name and link
        drug_list_content = drug_list.find_all('li')
        for content in drug_list_content:
            drug_content = content.find('a')
            drug_link = drug_content.get('href')
            drug_name = drug_content.text
            
            drug_names.append(drug_name)
            drug_links.append(drug_link)
             
            print(f"Drug {drug_name} with link : {drug_link}")
    else:
        print(f"Error fetching {url} : {response.status_code}")

# %%
isScrapped = [False for i in range(0, len(drug_names))]

# %%
data = {
    'drugName' : drug_names,
    'drugLink' : drug_links,
    'isScrapped' : isScrapped
}

drug_df = pd.DataFrame(data)
drug_df 

# %%
filename = os.getenv("DRUG_CHECKPOINT_FILENAME")

# %%
drug_df.to_excel(filename, index=False)


