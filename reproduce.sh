#!/bin/sh
# A bounded sequence of single-worker child processes; no two run concurrently.
set -eu
OUT=${1:?Usage: sh reproduce.sh OUTPUT_DIRECTORY}
exec python reproduce.py "$OUT"

# reviewer-hardening-v1
# Deterministic, disjoint held-out validation. Resource timings are kept outside this result tree.
mkdir -p "$OUT_DIR/reviewer-hardening"
python case_study/run_case_study.py --output "$OUT_DIR/reviewer-hardening"
python reviewer_hardening/heldout_campaign.py --output "$OUT_DIR/reviewer-hardening"
python reviewer_hardening/input_robustness.py --root . --output "$OUT_DIR/reviewer-hardening"
