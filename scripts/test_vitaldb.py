import pandas as pd

clinical = pd.read_csv("https://api.vitaldb.net/cases")
labs = pd.read_csv("https://api.vitaldb.net/labs")

print("CLINICAL COLUMNS")
print(clinical.columns.tolist())

print("\nMISSINGNESS IN KEY COLUMNS")
key_columns = [
    c for c in [
        "caseid", "age", "death_inhosp", "optype",
        "preop_htn", "preop_dm", "preop_hb",
        "preop_cr", "intraop_ebl", "intraop_uo"
    ] if c in clinical.columns
]
print(clinical[key_columns].isna().mean().sort_values())

print("\nLAB TEST FREQUENCIES")
print(labs["name"].value_counts().head(30).to_string())

print("\nLAB RESULTS SAMPLE")
print(labs.head(5).to_string(index=False))
