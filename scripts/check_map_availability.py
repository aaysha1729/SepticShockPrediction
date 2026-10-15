
import vitaldb
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

caseids = (
    pd.read_csv(RESULTS / "ppg_art_candidate_caseids.csv")["caseid"]
    .head(20)
    .astype(int)
    .tolist()
)

rows = []

for caseid in caseids:
    try:
        tracks = vitaldb.get_track_names([caseid])
        names = tracks.iloc[0]["tnames"]

        rows.append({
            "caseid": caseid,
            "has_PPG": "SNUADC/PLETH" in names,
            "has_raw_ART": "SNUADC/ART" in names,
            "has_MAP": "Solar8000/ART_MBP" in names,
        })

    except Exception as e:
        rows.append({
            "caseid": caseid,
            "error": repr(e),
        })

df = pd.DataFrame(rows)
out = RESULTS / "map_availability_audit.csv"
df.to_csv(out, index=False)

print(df.to_string(index=False))
print("\nSummary:")
for col in ["has_PPG", "has_raw_ART", "has_MAP"]:
    if col in df:
        print(f"{col}: {int(df[col].sum())}/{len(df)}")

print("\nSaved:", out)
