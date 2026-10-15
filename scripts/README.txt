VitalDB Feasibility Audit

Copy vitaldb_feasibility_audit.py into your existing project's scripts/ folder.
Run from the VS Code integrated terminal at the project root:

    python3 -m pip install vitaldb pandas
    python3 scripts/vitaldb_feasibility_audit.py

Outputs are saved in results/: JSON audit report, clinical missingness CSV,
lab-test frequencies CSV, and candidate PPG+arterial-pressure case IDs CSV.

This reads public metadata and checks track availability. It does not download
waveforms or prove septic-shock labels, signal quality, or research novelty.
