
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
file = ROOT / "results" / "multi_case_signal_audit.csv"

df = pd.read_csv(file)
df = df[df["status"] == "loaded"].copy()

print("Cases audited:", df["caseid"].nunique())
print("Tracks audited:", len(df))

print("\nDuration by track (hours):")
print(
    df.groupby("track")["duration_hours_approx"]
      .describe()
      .round(2)
      .to_string()
)

print("\nMissing fraction by track:")
print(
    df.groupby("track")["missing_fraction"]
      .describe()
      .round(4)
      .to_string()
)

print("\nCases with both tracks:")
pivot = df.pivot(index="caseid", columns="track", values="samples")
required = ["SNUADC/PLETH", "SNUADC/ART"]
if all(c in pivot.columns for c in required):
    both = pivot.dropna(subset=required)
    print("Both signals loaded:", len(both))
    print(both.to_string())
else:
    print("One or both expected tracks are absent.")

print("\nReminder: these checks do not establish clinical outcome labels.")
