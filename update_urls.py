########################################################
#                                                      #
# dieses Skript dient lediglich dazu, die URLs aus der #
# xlsx-Datei provisorisch zu aktualisieren. Am Ende    #
# sollte ein Mensch nochmal drüber schauen.            #
#                                                      #
########################################################

import pandas as pd

kh_liste = pd.read_excel('source_data/Krankenhausliste1.xlsx')
diagnostic_notes = pd.read_csv('source_data/URL_DIAGNOSTICS.csv')

kh_liste['Webside'] = kh_liste['Webside'].astype(str)

for i, row in kh_liste.iterrows():
    kh_liste.at[i, 'url_updated'] = kh_liste.at[i, 'Webside']
    kh_liste.at[i, 'url_updated_comment'] = "URL unverändert"

    # http(s) ergänzen
    if row['Webside'] == 'nan':
        kh_liste.at[i, 'url_updated'] = "URL leer"
        kh_liste.at[i, 'url_updated_comment'] = "URL leer"
        continue
    if not row['Webside'].startswith('http'):
        prefix = 'http://'
        if "Try testing the second URL directly." in diagnostic_notes.at[i, 'runWarnings']:
            prefix = 'https://'
        
        kh_liste.at[i, 'url_updated'] = prefix + kh_liste.at[i, 'Webside']
        kh_liste.at[i, 'url_updated_comment'] = f'"{prefix}"-Präfix ergänzt'

kh_liste.to_excel('source_data/Krankenhausliste_URLs_updated.xlsx')
print(kh_liste)