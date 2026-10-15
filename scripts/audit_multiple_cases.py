
import vitaldb
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

candidate_file = RESULTS / "ppg_art_candidate_caseids.csv"
caseids = (
    pd.read_csv(candidate_file)["caseid"]
    .drop_duplicates()
    .head(20)
    .astype(int)
    .tolist()
)

tracks = ["SNUADC/PLETH", "SNUADC/ART"]
rows = []

for caseid in caseids:
    print(f"Checking case {caseid}...")

    try:
        data = vitaldb.load_case(caseid, tracks, interval=1)

        for i, track in enumerate(tracks):
            signal = data[:, i]
            valid = np.isfinite(signal)

            rows.append({
                "caseid": caseid,
                "track": track,
                "samples": len(signal),
                "duration_hours_approx": len(signal) / 3600,
                "valid_samples": int(valid.sum()),
                "missing_fraction": (
                    float(1 - valid.mean()) if len(signal) else None
                ),
                "min_value": (
                    float(np.min(signal[valid])) if valid.any() else None
                ),
                "max_value": (
                    float(np.max(signal[valid])) if valid.any() else None
                ),
                "status": "loaded"
            })

    except Exception as e:
        rows.append({
            "caseid": caseid,
            "track": None,
            "status": f"error: {e}"
        })

df = pd.DataFrame(rows)
output = RESULTS / "multi_case_signal_audit.csv"
df.to_csv(output, index=False)

print("\nAudit summary:")
print(df.to_string(index=False))
print("\nSaved:", output)
