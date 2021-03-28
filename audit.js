//Dieses Skript soll alle n Tage automatisch ausgeführt werden

const fs = require('fs');
const lighthouse = require('lighthouse');
const lighthouse_desktop_config = require('lighthouse/lighthouse-core/config/desktop-config')
const chromeLauncher = require('chrome-launcher');
const path = require('path');
const readXlsxFile = require('read-excel-file/node');
const csvParse = require('csv-parse/lib/sync');

const URL_FILE_PATH = 'source_data/urls.txt';
const LOG_FILE_PATH = 'log.txt';
const N_RUNS_PER_WEBSITE = 1;
const OUTPUT_DIRECTORY = "reports";
const XLSX_URL_COLUMN = 4;

let total_time_ms = 0;
let lighthouse_options = {
    // logLevel: 'info',
    onlyCategories: [
        'performance',
        'accessibility',
        'best-practices',
        'seo'],
    output: "json",

    // throttling:
    // disableNetworkThrottling: true,
    // disableCpuThrottling: true,
    // disableDeviceEmulation: true,
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

/* schlägt einen Dateinamen für den report vor*/
function generate_filename(url){
    let filename;
    let format = lighthouse_options.output;
    let url_short = url.split('//')[1];
    if ( url_short.includes('www.') ){
        url_short = url.split('www.')[1];
    }

    let i = 1; /* increase until filename does not exist yet */

    do {
        filename = `${folderName}--${url_short}-${i}.${format}`
        i++;
    } while (fs.existsSync(path.join(OUTPUT_DIRECTORY, folderName, filename)));

    return filename;
}

/* Führt den Lighthouse audit n mal aus und speichert
das Ergebnis anschließend in einer neuen JSON-Datei */
async function run_audit(url, filePath, save_report=true){
    let startTime = new Date().getTime();

    try {
        let results = await lighthouse(url, lighthouse_options, lighthouse_desktop_config)

        if(save_report){
            fs.writeFileSync(filePath, results.report);

            /*das JSON-Objekt, das in filePath geschrieben wurde,
            ist auch unter results.lhr als JS-Objekt verfügbar */
            let report_duration = new Date().getTime() - startTime;
            total_time_ms += report_duration
            log(`Report finished (${report_duration/1000}s, ${Math.floor(total_time_ms/1000/60)}m total). Output saved to ${filePath}`);
        }
        return results.lhr;

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
let f = fs.readFileSync('dkgev_crawler/Krankenhaus_latlng.csv')
// 2329 Zeilen, 1740 unique URLs, 1712 unique after removing trailing '/'
let urls = csvParse(f, {columns: true}).map(row => {
    let u = row['url'];
    if(u.slice(-1) == '/'){
        return u.slice(0, -1);
    }
    return u;
});

urls = [...new Set(urls)]; //unique values

chromeLauncher.launch({chromeFlags: ['--headless']}).then( async chrome => {
    lighthouse_options.port = chrome.port; /* Den Lighthouse-Run-Optionen den Port auf dem Chrome läuft hinzufügen */
    lighthouse_options_url_testing.port = chrome.port;

    // #3 für jede gelesene URL n mal den Test ausführen:
    // siehe auch: https://github.com/GoogleChrome/lighthouse/blob/master/docs/variability.md
    
    for (let [i, url] of urls.entries()) {
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
            log(`[${(i+run_number).toString().padStart(4, '0')}/${urls.length*N_RUNS_PER_WEBSITE}] Running lighthouse audit #${run_number} for ${url}`);
            
            let fileName = generate_filename(url);
            let filePath = path.join(OUTPUT_DIRECTORY, folderName, fileName);

            try {
                let lhr = await run_audit(url, filePath, true);

                if (lhr['runWarnings']) 
                    { lhr['runWarnings'].join(); }

            } catch(error_msg) 
                { log("Lighthouse Error: " + error_msg); }

            /* Lighthouse-Calls müssen synchron (nacheinander) ausgeführt
            werden, sonst kommen sie durcheinander. Daher "await" */
        }
    };

    await chrome.kill();
    log("Alle Audits abgeschlossen, Chrome-Prozess beendet.");
    log_stream.end(); // Stream für das logfile schließen        
});