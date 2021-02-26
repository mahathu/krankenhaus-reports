Installation
===

Für Lighthouse (sammeln der Website-Analyse-Daten:)
---

1) nodejs installieren (https://nodejs.org/de/download/)
2) Google Chrome (Version >=59) installieren (https://developers.google.com/web/updates/2017/04/headless-chrome). Chrome wird für Lighthouse-Audits benötigt, läuft in unserem Fall aber "headless", d.h. ohne Fenster/Benutzeroberfläche.
2) `npm install` im Projektverzeichnis (welches auch die Datei `package.json` enthält) - dadurch werden Lighthouse und seine Dependencies installiert

Python:
---


Misc
===

**Output-Modi vom Lighthouse node-Modul:**
CSV, JSON und HTML möglich.
JSON enthält zu jedem audit eine Beschreibung und genaue Ergebnisse.
CSV enthält nur den Score (zwischen 0 und 1)
HTML stellt die gleichen Inhalte wie JSON als Website dar, d.h. der Report lässt sich in einem Webbrowser angenehm lesen. JSON ist aber besser "machine-readable", d.h. für unsere Zwecke der Auswertung und Analyse der gesammelten Daten besser geeignet.