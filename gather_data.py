import os, json
import pandas as pd

output_format = 'json'
reports_path = 'reports'
out_file = 'scores.csv'

# for subdir in [
#         f for f in os.listdir(reports_path) if 
#         os.path.isdir(os.path.join(reports_path, f))
#     ]:
#     print(subdir)

reports = [
    os.path.join(path, f) 
    for path, subdirs, files in os.walk(reports_path) 
    for f in files if f.endswith(output_format)
]
rows = []

for report_path in reports:
    with open(report_path) as f:
        report_data = json.load(f)

    row_values = {
        f'{category}-score': report_data['categories'][category]['score'] for category in report_data['categories']
    }
    row_values['hospital_url'] = report_data['requestedUrl']
    row_values['timestamp'] = report_data['fetchTime']
    row_values['report_path'] = report_path
    rows.append(row_values)

scores = pd.DataFrame(rows)
scores.to_csv(out_file, index=False)
print(f"Output written to {out_file}")