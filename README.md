Installation
===

### Für Lighthouse (sammeln der Website-Analyse-Daten:)

1) nodejs installieren (https://nodejs.org/de/download/)
2) Google Chrome (Version >=59) installieren (https://developers.google.com/web/updates/2017/04/headless-chrome). Chrome wird für Lighthouse-Audits benötigt, läuft in unserem Fall aber "headless", d.h. ohne Fenster/Benutzeroberfläche.
3) `npm install` im Projektverzeichnis (welches auch die Datei `package.json` enthält) - dadurch werden Lighthouse und seine Dependencies installiert
4) Um alle aufgeführten Krankenhäuser per Lighthouse zu testen: `node audit.js`. Wenn am gleichen Tag bereits Audits durchgeführt wurden, werden die neuen Ergebnisse in den gleichen Ordner gespeichert, und die alten somit überschrieben.

### Python:

1) ein neues virtuelles Environment erstellen: `python3 -m venv .venv` (https://docs.python.org/3/library/venv.html)
2) dieses neue virtuelle Environment aktivieren: `source .venv/bin/activate`
3) die nötigen Pakete im virtuellen Environment installieren: `pip3 install -r requirements.txt` 

Misc
===

**Output-Modi vom Lighthouse node-Modul:**
CSV, JSON und HTML möglich.
JSON enthält zu jedem audit eine Beschreibung und genaue Ergebnisse.
CSV enthält nur den Score (zwischen 0 und 1)
HTML stellt die gleichen Inhalte wie JSON als Website dar, d.h. der Report lässt sich in einem Webbrowser angenehm lesen. JSON ist aber besser "machine-readable", d.h. für unsere Zwecke der Auswertung und Analyse der gesammelten Daten besser geeignet.

JSON-Audits können hier menschenlesbar(er) dargestellt werden: https://googlechrome.github.io/lighthouse/viewer/