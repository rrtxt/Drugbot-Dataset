# %%
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

# %%
alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

# %%
all_initials : list = []

# %%
for alpha in alphabets:
    url = f"https://www.drugs.com/alpha/{alpha}.html"
    responses = requests.get(url)
    if responses.status_code == 200:
        soup = BeautifulSoup(responses.text, 'html.parser')
        
        ## Get list of all initials
        nav = soup.find('nav', class_='ddc-paging')
        alpha_list = nav.find('ul')
        alpha_contents = alpha_list.find_all('li')
        for content in alpha_contents:
            ## <li> with span is not used 
            if content.find('span') is not None:
                continue
            initial = content.text
            
            ## append alphabet to 0-9
            if initial == '0-9':
                initial = alpha + initial
                
            print(f"Inserting initial : {initial}")
            all_initials.append(initial)
    else:
        print(f'Error fetching {url}')

all_initials.append("0-9")

# %%
all_initials

# %%
isScrapped : list = [False for i in range(0, len(all_initials))]
isScrapped

# %%
data = {
    "Initial" : all_initials,
    "isScrapped" : isScrapped
}

# %%
filename = os.getenv("DRUG_INITIAL_CHECKPOINT_FILENAME")

# %%
df = pd.DataFrame(data)
df

# %%
df.to_excel(filename, index=False)


