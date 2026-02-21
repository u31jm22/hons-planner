#!/bin/bash

echo "=== Testing Blocksworld ==="
for prob in p04 p05; do
  echo "--- $prob ---"
  echo "FF:"
  python planner/run_single.py --domain domains/blocksworld/domain.pddl --problem domains/blocksworld/${prob}.pddl --heuristic ff --verbose 2>/dev/null | grep -E "Expansions|Time"
  echo "LLM:"
  python llm/evaluate_candidate.py --domain domains/blocksworld/domain.pddl --problem domains/blocksworld/${prob}.pddl --candidate llm/candidates/blocksworld_candidate_2.py
done

echo ""
echo "=== Testing Logistics ==="
for prob in p04 p05; do
  echo "--- $prob ---"
  echo "FF:"
  python planner/run_single.py --domain domains/logistics/domain.pddl --problem domains/logistics/${prob}.pddl --heuristic ff --verbose 2>/dev/null | grep -E "Expansions|Time"
  echo "LLM:"
  python llm/evaluate_candidate.py --domain domains/logistics/domain.pddl --problem domains/logistics/${prob}.pddl --candidate llm/candidates/logistics_candidate_1.py
done

echo ""
echo "=== Gripper already done ==="
