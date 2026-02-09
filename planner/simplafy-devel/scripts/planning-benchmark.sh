#!/bin/bash

pushd ..

export PYTHONPATH=PYTHONPATH:`pwd`/src

# python -m pddl.run_benchmark -p -o tmp tmp/prodcell
# python -m pddl.run_benchmark -p -o tmp tmp/blocksworld
# python -m pddl.run_benchmark -p -o tmp -d tmp/prodcell scripts/baseline-lm.yaml
# python -m pddl.run_benchmark -p -o tmp -d tmp/prodcell scripts/baseline.yaml scripts/baseline-add.yaml scripts/baseline-ff.yaml scripts/baseline-lm.yaml
# python -m pddl.run_benchmark -p -o tmp -d tmp/blocksworld scripts/baseline.yaml scripts/baseline-add.yaml scripts/baseline-ff.yaml scripts/baseline-lm.yaml
python -m pddl.run_benchmark -p -o ./tmp/prodcell -d tmp/prodcell scripts/baseline-ff.yaml scripts/baseline-lm.yaml scripts/baseline-lmcut.yaml scripts/baseline-max.yaml
python -m pddl.run_benchmark -p -o ./tmp/blocksworld -d tmp/blocksworld scripts/baseline-ff.yaml scripts/baseline-lm.yaml scripts/baseline-lmcut.yaml scripts/baseline-max.yaml