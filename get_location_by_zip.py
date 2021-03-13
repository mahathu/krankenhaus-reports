# use the Zipcodebase api to get latitude and longitude
# by zip code and save them in a file for future usage.

import requests
from termcolor import cprint
import pandas as pd

API_BASE_URL = 'https://app.zipcodebase.com/api/v1/search'
n_zipcodes_per_request = 50 # max is 100
output_data_dir = 'output_data'

### step 1: gather zip codes ###

df = pd.read_excel('source_data/Krankenhauslistevers2wind.xlsx')

other_zips = [] # for cells in which multiple, '/' separated zip codes are given
extract_zips = lambda s: other_zips.extend(s.split('/')) if '/' in s else s

zipcodes = df['PLZ'].dropna().astype("string") # remove empty vals
zipcodes = zipcodes.str.strip() # strip whitespace from values
zipcodes.apply(extract_zips) # save all the '/'-separated zips in an array
zipcodes = zipcodes[zipcodes.map(len) == 5] # drop all values of length != 5
print(f"{len(zipcodes)} out of {len(df)} total lines (-{len(df) - len(zipcodes)}) remain after filtering rows with multiple zip codes and NA values.")

zipcodes = zipcodes.append(pd.Series(other_zips))
print(f"{len(other_zips)} zip codes added from hospitals with multiple given zip codes. ({len(zipcodes)} total)")

zipcodes = zipcodes.drop_duplicates().sort_values().tolist()
# PLZs können/sollten mMn nicht zu ints gecasted werden, weil einige in DE mit 0 beginnen
print(f"{len(zipcodes)} unique zip codes after removing duplicates.\n")


### step 2: make requests ###

with open('zipcodebase_api_key', 'r') as api_file:
    request_headers = {"apikey": api_file.read()}

# Uncomment the following two lines to save API calls when debugging:
# n_zipcodes_per_request = 2
# zipcodes = zipcodes[:2]

zipcode_dicts = []

for i in range(0, len(zipcodes), n_zipcodes_per_request):
    print(f"Requesting data for zip codes {i+1} through {min(i+n_zipcodes_per_request, len(zipcodes))}... ", end='')

    zips_string = ','.join(zipcodes[i:i+n_zipcodes_per_request])
    request_params = (
        ('country', 'DE'),
        ('codes', zips_string),
    )

    response = requests.get(API_BASE_URL, headers=request_headers, params=request_params)
    cprint("Done!", "green")

    try:
        results = response.json()['results']
    except ValueError:
        print("Error decoding response data!")
        break
    
    # for each of the n_zipcodes_per_request:
    for zip, zip_results in results.items():
        # zip_results is a list of areas corresponding to the zip code (can be >1)
        # for example, 01067 gives: 'Dresden', 'Dresden Friedrichstadt' and 'Dresden Innere Altstadt'
        zipcode_dicts.extend(zip_results)

zipcode_data = pd.DataFrame(zipcode_dicts)
zipcode_data.drop(columns=['state_code', 'province_code'], inplace=True)

zipcode_data.to_csv(f'{output_data_dir}/zipcode_data.csv', index=False)
zipcode_data.to_pickle(f'{output_data_dir}/zipcode_data.pkl')

cprint(f"Output saved to {output_data_dir}.", "green")