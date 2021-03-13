import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from termcolor import cprint

MARKERSIZE_MAX = 15
MARKERSIZE_MIN = 2
DEBUG = False # use lower resolution, and open picture instead of saving it

def get_x_and_y_from_zip(zip):
    try:
        row = zip_locations.loc[zip_locations['postal_code'] == zip].iloc[0]
    except IndexError:
        cprint(f"PLZ nicht gefunden: {zip}", "red")
        return -1, -1
    
    return m(row['longitude'], row['latitude'])

zip_locations = pd.read_pickle('output_data/zipcode_data.pkl')
hospitals = pd.read_excel('source_data/Krankenhauslistevers2wind.xlsx')

betten_max = 3000 # hospitals['Betten'].max() angeblich 192154 :D

hospitals = hospitals.dropna(subset=['PLZ'])
hospitals['PLZ'] = hospitals['PLZ'].astype('string') # convert from obj to str
hospitals['PLZ'] = hospitals['PLZ'].apply(lambda s: s.split('/')[0].strip()) # if value is list of zip codes, take the first one and drop rest

# assign each hospital a random score:
hospitals['score'] = np.random.uniform(size=len(hospitals))

m = Basemap(
    projection='cass', 
    resolution='c' if DEBUG else 'f',
    area_thresh = 150, # keine Gewässer unter 150km^2 einzeichnen
    width=7e5,
    height=9e5,
    lat_0=51.1642292, # center lat/lon of map
    lon_0=10.4541194
)

m.etopo(scale=.1 if DEBUG else 3, alpha=.2)

m.drawcoastlines(linewidth=.5)
m.drawcountries()
#m.drawlsmask()
# plt.set_cmap('viridis')

# add x and y vals to dataframe:
hospitals['x'], hospitals['y'] = zip(*hospitals['PLZ'].map(get_x_and_y_from_zip))

plt.scatter(
    x=hospitals['x'], 
    y=hospitals['y'], 
    s=MARKERSIZE_MIN + (hospitals['Betten'] / betten_max * (MARKERSIZE_MAX-MARKERSIZE_MIN)),
    c=hospitals['score'],
    alpha=1
)

if DEBUG:
    plt.show()
else:
    plt.savefig('output_data/map.png', dpi=1500, bbox_inches='tight')