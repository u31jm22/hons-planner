# scripts/run_logistics_baseline.sh
#!/usr/bin/env bash
set -e

HEURISTIC="${1:-max}"

cd "$(dirname "$0")/.."

for i in 01 02 03 04 05; do
  echo "Running logistics p${i} with ${HEURISTIC}"
  python planner/run_single.py \
    --domain domains/logistics/domain.pddl \
    --problem domains/logistics/p${i}.pddl \
    --heuristic "${HEURISTIC}" \
    --verbose \
    > "experiments/logistics_p${i}_${HEURISTIC}.txt"
done

python analysis/summarise_logistics.py
