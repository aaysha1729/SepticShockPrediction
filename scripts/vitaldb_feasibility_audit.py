"""
VitalDB feasibility audit.
Run from your VS Code project root:
    python3 scripts/vitaldb_feasibility_audit.py

Reads public metadata and checks track availability; does not download waveforms.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import traceback

import pandas as pd
import vitaldb

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

report = {
    "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Public metadata and track availability only; no waveform files downloaded.",
    "warnings": [
        "Track availability does not prove signal duration or quality.",
        "VitalDB is primarily intraoperative, not a confirmed septic-shock cohort.",
        "Lab row counts are measurements, not unique patient counts."
    ],
}

def save_csv(df, filename):
    path = RESULTS / filename
    df.to_csv(path, index=False)
    print(f"Saved: {path} ({len(df)} rows)")

def main():
    print("Loading public VitalDB metadata...")
    clinical = pd.read_csv("https://api.vitaldb.net/cases")
    labs = pd.read_csv("https://api.vitaldb.net/labs")

    report["clinical_shape"] = list(clinical.shape)
    report["lab_shape"] = list(labs.shape)
    report["clinical_columns"] = clinical.columns.tolist()
    report["lab_columns"] = labs.columns.tolist()
    print("Clinical shape:", clinical.shape)
    print("Lab shape:", labs.shape)

    key_cols = [
        "caseid", "age", "death_inhosp", "optype", "preop_htn",
        "preop_dm", "preop_hb", "preop_cr", "intraop_ebl", "intraop_uo"
    ]
    key_cols = [c for c in key_cols if c in clinical.columns]
    missingness = clinical[key_cols].isna().mean().rename("missing_fraction").reset_index()
    missingness = missingness.rename(columns={"index": "column"})
    save_csv(missingness, "clinical_key_missingness.csv")

    if {"name", "caseid"}.issubset(labs.columns):
        agg = {"caseid": "nunique"}
        if "result" in labs.columns:
            lab_frequency = labs.groupby("name").agg(
                measurement_count=("name", "size"),
                unique_cases=("caseid", "nunique"),
                missing_results=("result", lambda s: int(s.isna().sum()))
            ).reset_index().sort_values("measurement_count", ascending=False)
        else:
            lab_frequency = labs.groupby("name").agg(
                measurement_count=("name", "size"),
                unique_cases=("caseid", "nunique")
            ).reset_index().sort_values("measurement_count", ascending=False)
        save_csv(lab_frequency, "lab_test_frequencies.csv")
        report["top_30_lab_tests"] = lab_frequency.head(30).to_dict("records")

    print("Checking cases with both PPG and arterial-pressure tracks...")
    cases = [int(x) for x in vitaldb.find_cases(["SNUADC/PLETH", "SNUADC/ART"])]
    save_csv(pd.DataFrame({"caseid": cases}), "ppg_art_candidate_caseids.csv")
    report["ppg_art_candidate_count"] = len(cases)
    report["ppg_art_candidate_caseids_first_50"] = cases[:50]

    if "caseid" in clinical.columns:
        clinical_ids = set(pd.to_numeric(clinical["caseid"], errors="coerce").dropna().astype(int))
        report["candidate_cases_in_clinical_table"] = len(set(cases) & clinical_ids)
    if "caseid" in labs.columns:
        lab_ids = set(pd.to_numeric(labs["caseid"], errors="coerce").dropna().astype(int))
        report["candidate_cases_with_any_lab_record"] = len(set(cases) & lab_ids)

    report_path = RESULTS / "vitaldb_feasibility_report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print("\nAUDIT COMPLETE")
    print(json.dumps({
        "clinical_shape": report["clinical_shape"],
        "lab_shape": report["lab_shape"],
        "ppg_art_candidate_count": report["ppg_art_candidate_count"],
        "candidate_cases_in_clinical_table": report.get("candidate_cases_in_clinical_table"),
        "candidate_cases_with_any_lab_record": report.get("candidate_cases_with_any_lab_record"),
        "output_folder": str(RESULTS)
    }, indent=2))
    print("Note: usable signal duration/quality and valid clinical outcomes still need separate checks.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("AUDIT FAILED:", repr(exc))
        print(traceback.format_exc())
        raise
