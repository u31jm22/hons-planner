#!/usr/bin/env bash
set -e

HEURISTIC="${1:-max}"
SPLIT="${2:-all}"  # all | train | test

cd "$(dirname "$0")/.."

if [ "$SPLIT" = "train" ]; then
  INSTANCES="01 02 03"
elif [ "$SPLIT" = "test" ]; then
  INSTANCES="04 05"
else
  INSTANCES="01 02 03 04 05"
fi

for i in $INSTANCES; do
  echo "Running blocksworld p${i} with ${HEURISTIC} (${SPLIT} set)"
  python planner/run_single.py \
    --domain domains/blocksworld/domain.pddl \
    --problem domains/blocksworld/p${i}.pddl \
    --heuristic "${HEURISTIC}" \
    --verbose \
    > "experiments/blocksworld_p${i}_${HEURISTIC}.txt"
done

