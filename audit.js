//Dieses Skript soll alle n Tage automatisch ausgeführt werden

const fs = require('fs');
const lighthouse = require('lighthouse');
const lighthouse_desktop_config = require('lighthouse/lighthouse-core/config/desktop-config')
const chromeLauncher = require('chrome-launcher');
const path = require('path');
const readXlsxFile = require('read-excel-file/node');
const URL_FILE_PATH = 'source_data/urls.txt';
const LOG_FILE_PATH = 'log.txt';
const N_RUNS_PER_WEBSITE = 1;
const OUTPUT_DIRECTORY = "reports";

const XLSX_URL_COLUMN = 4;

let lighthouse_options = {
    // logLevel: 'info',
    onlyCategories: [
        'performance',
        'accessibility',
        'best-practices',
        'seo'],
    output: "json",
};

//special options to only test if URLS are working:
let lighthouse_options_url_testing = {
    onlyCategories: ['performance'],
    disableNetworkThrottling: true,
    // disableCpuThrottling: true,
    // disableDeviceEmulation: true,
};

/* Diese Funktion gibt den string aus und 
schreibt ihn gleichzeitig ins logfile. */
function log(string){
    console.log(`[LOG] ${string}`);

    let now = new Date().toISOString().slice(0,-5);
    let log_line = `[${now}] ${string}\n`;
    log_stream.write(log_line);
}

/* Führt den Lighthouse audit n mal aus und speichert
das Ergebnis anschließend in einer neuen JSON-Datei */
function run_audit(url, filePath, save_report=true){
    try {
        return lighthouse(url, lighthouse_options, lighthouse_desktop_config).then( results => {

            if(save_report){
                fs.writeFileSync(filePath, results.report);

                /*das JSON-Objekt, das in filePath geschrieben wurde,
                ist auch unter results.lhr als JS-Objekt verfügbar */
                log(`Report finished. Output saved to ${filePath}`);
            } else return results.lhr;
        });
    } catch (error) {
        return `Fehler bei URL ${url}: ${error.message}`;
    }
}

// #0 - Setup
if(! fs.existsSync(OUTPUT_DIRECTORY)){
    /* ggf. output-Verzeichnis für alle reports erstellen
    falls es noch nicht existiert. */

    fs.mkdirSync(OUTPUT_DIRECTORY);
    log(`Output-Verzeichnis erstellt: ${OUTPUT_DIRECTORY}`);
}
if(! fs.existsSync(LOG_FILE_PATH)){ //logfile erstellen, falls es noch nicht existiert
    fs.writeFileSync(LOG_FILE_PATH, '');
}

//Stream für logfile:
let log_stream = fs.createWriteStream(LOG_FILE_PATH, {flags:'a'});

// #1 - Ein neues Verzeichnis für die Lighthouse-Audits des aktuellen Tages anlegen:
let folderName = new Date().toISOString().slice(0, 10); // aktuelles Datum
let report_directory = path.join(OUTPUT_DIRECTORY, folderName)

/* die nächsten 4 Zeilen sind auskommentiert, d.h. 
es wird kein neuer Ordner erstellt, wenn ein Ordner
mit dem gleichen Namen bereits existiert. Als Folge
werden die Reports eines Tages überschrieben, wenn 
am gleichen Tag das Skript nochmal ausgeführt wird.*/

// while (fs.existsSync(folderName)) {
//     // Verzeichnis mit dem Namen existiert bereits.
//     folderName += '_';
// };

if(! fs.existsSync(report_directory)){
    fs.mkdirSync(report_directory);
    log(`Neues Verzeichnis erstellt: ${report_directory}`);
}

// #2 - URLS einlesen
let url_file_content, xlsx_rows;
try {
    url_file_content = fs.readFileSync(URL_FILE_PATH, 'utf8');
} catch (err) {
    log("Fehler beim Lesen der URL-Liste: " + err);
    process.exit(1);
}

let urls = url_file_content.split('\n');

readXlsxFile('source_data/Krankenhausliste1.xlsx').then((rows) => {
    let xlsx_urls = rows.map(row => row[XLSX_URL_COLUMN]);
    let csv_rows = 'url, runWarnings, notiz\n';
    xlsx_urls.shift(); // ignore header row
    chromeLauncher.launch({chromeFlags: ['--headless']}).then( async chrome => {
        lighthouse_options.port = chrome.port; /* Den Lighthouse-Run-Optionen den Port auf dem Chrome läuft hinzufügen */
        lighthouse_options_url_testing.port = chrome.port;
    
        // #3 für jede gelesene URL n mal den Test ausführen:
        // siehe auch: https://github.com/GoogleChrome/lighthouse/blob/master/docs/variability.md
        
        for (let [i, url] of xlsx_urls.entries()) {
            if (url == null || url.startsWith('#') || !url.trim()){ //Überspringe leere Zeilen oder solche, die mit '#' anfangen
                csv_str = `null, URL leer, url leer\n`;
                continue;
            };

            let note = '';
            if (! url.startsWith('http') ){
                url = 'http://'+url;
                note = '"http://"-Prefix manuell hinzugefügt'
            }
    
    
            for(let run_number = 1; run_number < N_RUNS_PER_WEBSITE+1; run_number++){
                log(`[${i+run_number} / ${xlsx_urls.length*N_RUNS_PER_WEBSITE}] Running lighthouse audit #${run_number} for ${url}...`);
                
                let fileName = `${folderName}-${url.split('//')[1]}-report-${run_number}.${lighthouse_options.output}`;
                let filePath = path.join(OUTPUT_DIRECTORY, folderName, fileName);
    
                try {
                    let lhr = await run_audit(url, filePath, true);
                    //let runWarnings = lhr['runWarnings'].join();
                    //csv_str = `${url}, ${runWarnings}, ${note}\n`;
                } catch(error_msg) {
                    log("Lighthouse Error: " + error_msg);
                    //csv_str = `${url}, INVALID URL, ${note}\n`;
                }
                /* Lighthouse-Calls müssen synchron (nacheinander) ausgeführt
                werden, sonst kommen sie durcheinander. Daher "await" */
            }
        };
    
        await chrome.kill();
        log("Alle Audits abgeschlossen, Chrome-Prozess beendet.");
        log_stream.end(); // Stream für das logfile schließen        
    });
})