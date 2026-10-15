
import vitaldb
import numpy as np

caseid = 1

data = vitaldb.load_case(
    caseid,
    ["Solar8000/ART_MBP"],
    interval=1
)

values = np.asarray(data[:, 0], dtype=float)

print("Total samples:", len(values))
print("NaN samples:", int(np.isnan(values).sum()))
print("Finite samples:", int(np.isfinite(values).sum()))

finite = values[np.isfinite(values)]

if len(finite):
    print("Minimum:", float(finite.min()))
    print("Maximum:", float(finite.max()))
    print("Percentiles:", np.percentile(
        finite, [0, 1, 5, 25, 50, 75, 95, 99, 100]
    ))

    print("\nFirst 50 finite values:")
    print(finite[:50])

print("\nMost frequent raw values:")
unique_values, counts = np.unique(values, return_counts=True)
order = np.argsort(counts)[::-1]

for i in order[:20]:
    print(f"{unique_values[i]}: {counts[i]} samples")

print("\nInvalid-code counts:")
for code in [-9, -8, -7, -6, -5, -4, -3, -2, -1, 0]:
    print(f"{code}: {int(np.sum(values == code))}")
