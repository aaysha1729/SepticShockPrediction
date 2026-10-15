
import vitaldb
import numpy as np
import pandas as pd
from pathlib import Path

# Test case with PPG and arterial pressure
caseid = 1
track_names = ["SNUADC/PLETH", "SNUADC/ART"]

print(f"Loading signals for case {caseid}...")

try:
    # interval=1 means one sample per second
    data = vitaldb.load_case(
        caseid,
        track_names,
        interval=1
    )

    print("Array shape:", data.shape)

    results = []

    for i, track in enumerate(track_names):
        signal = data[:, i]
        valid = np.isfinite(signal)

        results.append({
            "caseid": caseid,
            "track": track,
            "samples": len(signal),
            "valid_samples": int(valid.sum()),
            "missing_fraction": float(1 - valid.mean()),
            "min_value": float(np.nanmin(signal)) if valid.any() else None,
            "max_value": float(np.nanmax(signal)) if valid.any() else None,
        })

    df = pd.DataFrame(results)

    output_dir = Path(__file__).resolve().parents[1] / "results"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "case1_signal_audit.csv"
    df.to_csv(output_file, index=False)

    print("\nSignal audit:")
    print(df.to_string(index=False))
    print("\nSaved to:", output_file)

except Exception as e:
    print("Error:", repr(e))
