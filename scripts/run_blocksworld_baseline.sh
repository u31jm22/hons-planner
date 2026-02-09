#!/bin/bash
set -e
cd "$(dirname "$0")/.."

for i in 01 02 03 04 05; do
  for h in add ff max; do
    echo "Running blocksworld p$i with $h"
    python -m planner.run_single \
      --domain domains/blocksworld/domain.pddl \
      --problem domains/blocksworld/p${i}.pddl \
      --heuristic $h \
      > experiments/blocksworld_p${i}_${h}.txt
  done
done

python analysis/summarise_blocksworld.py
