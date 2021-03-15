import pandas as pd
import requests
import certifi
import urllib3
from bs4 import BeautifulSoup
from termcolor import cprint

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

default_na = 'N/A'
base_url = 'http://dkgev.deutsches-krankenhaus-verzeichnis.de'
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"

df = pd.read_pickle('Krankenhaus_df.tbl')

total = len(df)

hospitals = []
failed = []
for i, row in df.iterrows():
    errors = []


    print(
        f"[{i:04}/{total}] {row['name']}... ", 
        end='', 
        flush=True)

    r = requests.get(base_url+row['path'], headers={'User-Agent': user_agent}, verify=False)

    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Bettenzahl:
    try:
        n_betten = soup.select('#collapseBasicInfos ul.dashed:first-of-type li:first-of-type')[0].text.split()[-1]
    except:
        errors.append('beds')
        failed.append(row['name'])
        n_betten = default_na

    # URL der Website:
    try:
        kh_url = soup.select('section.head a.url')[0]['href']
    except:
        errors.append('URL')
        kh_url = default_na

    # Adresse:
    # try:
    #     adr = soup.select('section.head .col-sm-8 p')[0].text
    #     adr = ' '.join(adr.split())
    # except:
    #     errors.append('address')
    #     adr = default_na

    if not errors:
        cprint("Done!", "green")
    
    else:
        cprint(errors, "red")

    hospitals.append({ # add dict to results list
        "Krankenhaus": row['name'],
        "Adresse": row['address'],
        "n_Betten": n_betten,
        "url": kh_url
    })

df2 = pd.DataFrame(hospitals)
df2.to_csv("Krankenhausliste.csv", index=False)
print(f"All Done ({len(failed)} failed)")