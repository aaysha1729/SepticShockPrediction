
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
    try:
        # Load MAP at one sample per second
        data = vitaldb.load_case(
            caseid,
            ["Solar8000/ART_MBP"],
            interval=1
        )

        if data is None or len(data) == 0:
            rows.append({
                "caseid": caseid,
                "status": "No data returned"
            })
            continue

        map_values = np.asarray(data[:, 0], dtype=float)
        valid = map_values[np.isfinite(map_values)]

        # Exclude clearly implausible values for this preliminary audit
        valid = valid[(valid >= 20) & (valid <= 200)]

        # At 1 Hz, 60 consecutive samples represent about one minute
        below_65 = np.isfinite(map_values) & (map_values < 65)
        below_65 &= (map_values >= 20)

        # Count runs of consecutive below-threshold samples
        padded = np.r_[False, below_65, False]
        changes = np.diff(padded.astype(int))
        starts = np.where(changes == 1)[0]
        ends = np.where(changes == -1)[0]
        run_lengths = ends - starts

        qualifying_runs = run_lengths >= 60

        rows.append({
            "caseid": caseid,
            "status": "OK",
            "samples": len(map_values),
            "valid_MAP_samples": len(valid),
            "valid_MAP_percent": round(
                100 * len(valid) / len(map_values), 2
            ) if len(map_values) else 0,
            "min_MAP": round(float(np.min(valid)), 2)
                if len(valid) else np.nan,
            "max_MAP": round(float(np.max(valid)), 2)
                if len(valid) else np.nan,
            "minutes_below_65_total": round(
                float(np.sum(below_65)) / 60, 2
            ),
            "runs_below_65_for_60s": int(
                np.sum(qualifying_runs)
            )
        })

    except Exception as e:
        rows.append({
            "caseid": caseid,
            "status": f"ERROR: {e}"
        })

df = pd.DataFrame(rows)
out = RESULTS / "hypotension_event_audit.csv"
df.to_csv(out, index=False)

print(df.to_string(index=False))
print("\nCases with at least one qualifying run:")
if "runs_below_65_for_60s" in df.columns:
    print(
        int((df["runs_below_65_for_60s"].fillna(0) > 0).sum()),
        "out of", len(df)
    )

print("\nSaved:", out)
