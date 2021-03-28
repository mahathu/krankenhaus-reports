import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from termcolor import cprint

MARKERSIZE_MAX = 10
MARKERSIZE_MIN = 2
DEBUG = 0 # use lower resolution, and open picture instead of saving it

def get_x_and_y_from_zip(zip):
    try:
        row = zip_locations.loc[zip_locations['postal_code'] == zip].iloc[0]
    except IndexError:
        cprint(f"PLZ nicht gefunden: {zip}", "red")
        return -1, -1
    
    return m(row['longitude'], row['latitude'])

zip_locations = pd.read_pickle('output_data/zipcode_data.pkl')
#hospitals = pd.read_excel('source_data/Krankenhauslistevers2wind.xlsx')
hospitals = pd.read_csv('dkgev_crawler/Krankenhaus_latlng.csv')
hospitals = hospitals[hospitals['url'].notna()]

scores = pd.read_csv('source_data/scores.csv')
# im hospitals df jeder URL, die noch keines hat, ein 
# '/' anhängen, damit das joinen richtig funktioniert
hospitals['url'] = hospitals['url'].astype('string').apply(lambda u: u if u[-1] == '/' else u+'/')

hospitals = hospitals.merge(scores, on='url', how='inner')
print(hospitals.columns)

# top 10 hospitals:
# hospitals = hospitals.sort_values(by='performance-score', ascending=False).head(10)

betten_max = hospitals['n_Betten'].max()

print("Building basemap...")
m = Basemap(
    projection='cass', 
    resolution='c' if DEBUG else 'f',
    area_thresh = 150, # keine Gewässer unter 150km^2 einzeichnen
    width=7e5,
    height=9e5,
    lat_0=51.1642292, # center lat/lon of map
    lon_0=10.4541194
)

print("Drawing topology...")
m.etopo(scale=.1 if DEBUG else 3, alpha=.2)

print("Drawing country lines...")
m.drawcoastlines(linewidth=.5)
m.drawcountries()

# add x and y vals to dataframe:
# hospitals['x'], hospitals['y'] = zip(*hospitals['PLZ'].map(get_x_and_y_from_zip))
xy= pd.DataFrame( hospitals.apply(
    lambda row: m(row['lng'],row['lat']),
    axis = 1
).tolist())

xy= pd.DataFrame( hospitals[['lng','lat']].apply(
    lambda row: m(*row), 
    axis = 1
).tolist())

# plt.scatter(
#     x=xy[0], 
#     y=xy[1], 
#     s=MARKERSIZE_MIN + (hospitals['n_Betten'] / betten_max * (MARKERSIZE_MAX-MARKERSIZE_MIN)),
#     c=hospitals['performance-score'],
#     alpha=1
# )

# if DEBUG:
#     plt.show()
#     exit(0)

for metric in ['performance', 'accessibility', 'best-practices', 'seo']:
    markers = plt.scatter(
        x=xy[0], 
        y=xy[1], 
        s=MARKERSIZE_MIN + (hospitals['n_Betten'] / betten_max * (MARKERSIZE_MAX-MARKERSIZE_MIN)),
        c=hospitals[f'{metric}-score'],
        alpha=1
    )
    fn = f'output_data/hospitals-{metric}.png'

    plt.title(metric)
    plt.savefig(fn, dpi=1500, bbox_inches='tight')
    markers.remove()

    print(f"Saved {fn}")