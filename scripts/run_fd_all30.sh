#!/bin/bash -l
#SBATCH --job-name=fd_all30
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=compute
#SBATCH --time=24:00:00
#SBATCH --output=logs/fd_all30_%j.out
#SBATCH --error=logs/fd_all30_%j.err

# ============================================================
# scripts/run_fd_all30.sh
#
# Runs Fast Downward seq-opt-lmcut on all 30 instances per
# domain and collects results into:
#   results/<domain>_lmcut_all30.csv
#
# Can be submitted as a SLURM job:
#   sbatch scripts/run_fd_all30.sh
# or run directly:
#   bash scripts/run_fd_all30.sh
# ============================================================

set -euo pipefail

echo "=============================="
echo "fd_all30 started on $(hostname)"
date
echo "=============================="

HONS_DIR="${HOME}/hons-llm-heuristics"
FD_BIN="${HOME}/fast-downward/fast-downward.py"
LOGS_DIR="${HONS_DIR}/results_fd_all30"
RESULTS_DIR="${HONS_DIR}/results"
TIMEOUT=600  # seconds per problem

mkdir -p "${LOGS_DIR}" "${RESULTS_DIR}"

cd "${HONS_DIR}"

# Ensure python is available (on MacLeod with module system)
if command -v module &>/dev/null; then
    module load python/3.11.7 2>/dev/null || true
fi

DOMAINS="blocksworld gripper logistics miconic depots rovers"

for domain in $DOMAINS; do
    inst_file="${HONS_DIR}/domains/${domain}/all_instances.txt"
    dom_pddl="${HONS_DIR}/domains/${domain}/domain.pddl"
    out_csv="${RESULTS_DIR}/${domain}_lmcut_all30.csv"

    if [ ! -f "$inst_file" ]; then
        echo "[SKIP] $domain — no all_instances.txt"
        continue
    fi

    echo ""
    echo "=== $domain ==="

    mapfile -t problems < <(grep -v '^\s*$' "$inst_file")

    # Write CSV header if file doesn't exist
    if [ ! -f "$out_csv" ]; then
        echo "domain,problem,heuristic,model,coverage,expansions,search_time,plan_length" > "$out_csv"
    fi

    for prob in "${problems[@]}"; do
        prob_pddl="${HONS_DIR}/domains/${domain}/${prob}"
        log_file="${LOGS_DIR}/fd_lmcut_${domain}_${prob%.pddl}.log"

        # Skip if already in CSV
        if grep -q ",$prob," "$out_csv" 2>/dev/null; then
            echo "  [SKIP] $domain/$prob already in CSV"
            continue
        fi

        if [ ! -f "$prob_pddl" ]; then
            echo "  [SKIP] $prob_pddl not found"
            continue
        fi

        echo "  Running FD lmcut on $domain/$prob ..."
        timeout "${TIMEOUT}" python3 "${FD_BIN}" \
            --alias seq-opt-lmcut \
            "${dom_pddl}" "${prob_pddl}" > "${log_file}" 2>&1 || true

        # Parse log immediately and append row to CSV
        python3 - <<PYEOF >> "$out_csv"
import re, sys

log_path = "${log_file}"
domain   = "${domain}"
prob     = "${prob}"

try:
    text = open(log_path, errors="ignore").read()
except FileNotFoundError:
    print(f"{domain},{prob},lmcut,fd,0,,,")
    sys.exit(0)

coverage = 1 if "Solution found." in text else 0

m = re.search(r"Expanded\s+(\d+)\s+state", text)
expansions = m.group(1) if m else ""

m = re.search(r"Search time:\s*([0-9.]+)s", text)
search_time = m.group(1) if m else ""

m = re.search(r"Plan length:\s*(\d+)\s+step", text)
plan_length = m.group(1) if m else ""

print(f"{domain},{prob},lmcut,fd,{coverage},{expansions},{search_time},{plan_length}")
PYEOF

        echo "    Done (coverage=$(tail -1 "$out_csv" | cut -d, -f5))"
    done

    echo "  Written: $out_csv ($(tail -n +2 "$out_csv" | wc -l) rows)"
done

echo ""
echo "=============================="
echo "fd_all30 completed"
date
echo "=============================="
