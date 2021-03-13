# use the Zipcodebase api to get latitude and longitude
# by zip code and save them in a file for future usage.

import requests
from termcolor import cprint
import pandas as pd
import math

API_BASE_URL = 'https://app.zipcodebase.com/api/v1/search'
N_ZIPCODES_PER_REQUEST = 50 # max is 100
OUT_DIR = 'output_data'

### step 1: gather zip codes ###
df = pd.read_excel('source_data/Krankenhauslistevers2wind.xlsx')

zipcodes = df['PLZ'].dropna().astype("string") # remove empty vals

# some elements contain not a single zip code, but
# instead a list of '/' separated codes. The following
# line appends the zip codes extracted from such elements.
zipcodes = zipcodes.append(pd.Series(
    [z for zip_list in zipcodes for z in zip_list.split("/") if "/" in zip_list]
))
zipcodes = zipcodes.str.strip() # strip whitespace from values
zipcodes = zipcodes[zipcodes.map(len) == 5] # drop all values of length != 5
zipcodes = zipcodes.drop_duplicates().sort_values().tolist() # drop dupes, sort values
print(f"{len(zipcodes)} unique zip codes found.")

### step 2: make requests ###

# Uncomment the following two lines to save API calls when debugging:
# N_ZIPCODES_PER_REQUEST = 2
# zipcodes = zipcodes[:2]

input(f"Press enter to continue ({math.ceil(len(zipcodes)/N_ZIPCODES_PER_REQUEST)} API calls will be made!)")

with open('zipcodebase_api_key', 'r') as api_file:
    request_headers = {"apikey": api_file.read()}

zipcode_dicts = []

for i in range(0, len(zipcodes), N_ZIPCODES_PER_REQUEST):
    print(f"Requesting data for zip codes {i+1} through {min(i+N_ZIPCODES_PER_REQUEST, len(zipcodes))}... ", end='')

    zips_string = ','.join(zipcodes[i:i+N_ZIPCODES_PER_REQUEST])
    request_params = (
        ('country', 'DE'),
        ('codes', zips_string),
    )

    response = requests.get(API_BASE_URL, headers=request_headers, params=request_params)
    cprint("Done!", "green")

    try:
        results = response.json()['results']
    except ValueError:
        cprint(f"Error decoding response data for input zip codes: {zips_string}", red)
        continue
    
    # for each of the n zipcodes do this:
    for zip, zip_results in results.items():
        # zip_results is a list of areas corresponding to the zip code (can be >1)
        # for example, 01067 gives: 'Dresden', 'Dresden Friedrichstadt' and 'Dresden Innere Altstadt'
        zipcode_dicts.extend(zip_results)

zipcode_data = pd.DataFrame(zipcode_dicts)
zipcode_data.drop(columns=['state_code', 'province_code'], inplace=True)

zipcode_data.to_csv(f'{OUT_DIR}/zipcode_data.csv', index=False)
zipcode_data.to_pickle(f'{OUT_DIR}/zipcode_data.pkl')

cprint(f"Output saved to {OUT_DIR}.", "green")