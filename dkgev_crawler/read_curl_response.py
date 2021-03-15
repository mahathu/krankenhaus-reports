"""
curl -X POST 
-b "PHPSESSID=68budq5rpgtismaivg756i3lga" 
-d "search%5BwhereSearchString%5D=&search%5BwhereRange%5D=1000&search%5BwhatSearchString%5D=&search%5Bsend%5D=&search%5BicdOps%5D=&search%5Bfachabteilung%5D=&search%5BmedPflegLeistung%5D=&search%5BserviceAusstattungZimmer%5D=&search%5BserviceBettenPatientenzimmer%5D=&search%5BserviceAusstattungKrankenhaus%5D=&search%5BserviceHilfeService%5D=&search%5BwhereType%5D=&search%5BfilterIcdOps%5D=&search%5BfilterFachabteilungen%5D=&search%5BfilterMedPflegLeistungen%5D=&search%5BfilterAusstattungZimmer%5D=&search%5BfilterBettenPatientenzimmer%5D=&search%5BfilterAusstattungKrankenhaus%5D=&search%5BfilterHilfeService%5D=&search%5B_token%5D=-43VJy5duLWVsmSRH8zrhqlqHEOUUd2p12XnCIMKrBM" 
"https://dkgev.deutsches-krankenhaus-verzeichnis.de/app/suche/ergebnis"
"""

import json
import ast
import pandas as pd

with open('curl_response', 'r') as f:
    file_content = f.read()

# turn into valid JSON...
file_content = file_content.replace("'", '"')
file_content = file_content.replace(",}", '}')
properties = ['address', 'lat', 'lng', 'name', 'path', 'color', 'zIndex']
for s in properties:
    file_content = file_content.replace(f"{s}:", f'"{s}":')
    file_content = file_content.replace(f"{s} :", f'"{s}":')

# e = 178 # error at char
# o = 10 # offset
# print(file_content[e-o:e+o])

df = pd.DataFrame(json.loads(file_content))
df.drop(['color', 'zIndex'], axis=1, inplace=True)

df.to_pickle("Krankenhaus_df.tbl")