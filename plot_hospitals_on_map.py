import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from mpl_toolkits.basemap import Basemap
from termcolor import cprint

MARKERSIZE_MIN = 2
MARKERSIZE_RANGE = 50


xvals = []
yvals = []
beds = []
scores = []

def add_datapoint(row):
    score = random.random() # placeholder
    zipcode = str(row['PLZ'])
    
    if '/' in zipcode:
        zipcode = zipcode.split('/')[0]

    zips = zip_locations.loc[zip_locations['postal_code'] == zipcode]

    if zips.empty:
        cprint(f"Couldn't locate {row[1]} (zip code: {zipcode})", 'red')
        return

    if len(zips) > 1:
        cprint(f"Found {len(zips)} locations for zip code {zipcode} (hospital {row[1]} in {row[0]})", 'yellow')

    # use the first row of all found zip code locations:
    x, y = m(zips.iloc[0]['longitude'], zips.iloc[0]['latitude'])
    bed_count_factor = (row['Betten'] - betten_min) / (betten_max - betten_min)

    print(f"Plotting {row[1]} in {zipcode} {zips.iloc[0]['city']} ({row['Betten']} Betten, {bed_count_factor:.2f})...")
    xvals.append(x)
    yvals.append(y)
    beds.append(MARKERSIZE_MIN+MARKERSIZE_RANGE*bed_count_factor)
    scores.append(score)


zip_locations = pd.read_pickle('output_data/zipcode_data.pkl')
hospitals = pd.read_excel('source_data/Krankenhauslistevers2wind.xlsx')

betten_max = 3000 # hospitals['Betten'].max() angeblich 192154 :D
betten_min = hospitals['Betten'].min() # 1

# hospitals = hospitals.sample(n=50, random_state=1)

m = Basemap(
    projection='cass', 
    resolution='h',
    area_thresh = 150, # keine Gewässer unter 150km^2
    width=7e5,
    height=9e5,
    lat_0=51.1642292, 
    lon_0=10.4541194
)

m.etopo(scale=3, alpha=.2)

m.drawcoastlines(linewidth=.5)
m.drawcountries()
#m.drawlsmask()

hospitals.apply(add_datapoint, axis = 1)

plt.set_cmap('viridis')
plt.scatter(
    x=xvals, 
    y=yvals, 
    s=beds,
    c=scores,
    alpha=1
)

plt.savefig('output_data/map.png', dpi=1500, bbox_inches='tight')
# plt.show()