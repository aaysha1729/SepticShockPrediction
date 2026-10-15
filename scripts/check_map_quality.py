
import vitaldb
import pandas as pd
import numpy as np
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
    data = vitaldb.load_case(
        caseid,
        ["Solar8000/ART_MBP"],
        interval=1
    )

    values = np.asarray(data[:, 0], dtype=float)
    valid = np.isfinite(values) & (values >= 20) & (values <= 200)

    rows.append({
        "caseid": caseid,
        "total_samples": len(values),
        "valid_samples": int(valid.sum()),
        "valid_percent": round(100 * valid.mean(), 2),
        "below_20": int((np.isfinite(values) & (values < 20)).sum()),
        "above_200": int((np.isfinite(values) & (values > 200)).sum())
    })

df = pd.DataFrame(rows)
df.to_csv(RESULTS / "map_quality_audit.csv", index=False)

print(df.to_string(index=False))
print("\nMean valid percentage:", round(df["valid_percent"].mean(), 2))
print("Saved:", RESULTS / "map_quality_audit.csv")
