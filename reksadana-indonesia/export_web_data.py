import pandas as pd
import json

df = pd.read_csv('reksadana-indonesia/reksadana_indonesia_scored.csv')
records = df.to_dict(orient='records')
for r in records:
    for k, v in r.items():
        if pd.isna(v):
            r[k] = None

js_data = '(typeof window !== "undefined" ? window : globalThis).INDONESIA_REKSADANA_DATA = ' + json.dumps(records, indent=2) + ';'
with open('reksadana-indonesia/data.js', 'w', encoding='utf-8') as f:
    f.write(js_data)

print(f"data.js generated with {len(records)} Indonesian mutual funds!")
