#!/bin/bash
set -e
cd "$(dirname "$0")/.."

for i in 01 02 03 04 05; do
  for h in add ff max; do
    echo "Running logistics p$i with $h"
    python -m planner.run_single \
      --domain domains/logistics/domain.pddl \
      --problem domains/logistics/p${i}.pddl \
      --heuristic $h \
      > experiments/logistics_p${i}_${h}.txt
  done
done

python analysis/summarise_logistics.py
