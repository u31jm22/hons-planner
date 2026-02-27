#!/bin/bash -l
#SBATCH --job-name=fd_grid
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=compute
#SBATCH --time=08:00:00
#SBATCH --output=logs/fd_grid_%j.out
#SBATCH --error=logs/fd_grid_%j.err

echo "Started FD grid on $(hostname)"
date

HONS_DIR="$HOME/hons-llm-heuristics"
FD_DIR="$HOME/fast-downward"
OUT_DIR="$HONS_DIR/results_fd"

mkdir -p "$OUT_DIR"

cd "$HONS_DIR"
module load python/3.11.7

DOMAINS="gripper depots blocksworld logistics"
PROBLEMS="p01 p02 p03 p04 p05 p06 p07 p08 p09 p10"

for domain in $DOMAINS; do
  for prob in $PROBLEMS; do
    DOM_PDDL="${HONS_DIR}/domains/${domain}/domain.pddl"
    PROB_PDDL="${HONS_DIR}/domains/${domain}/${prob}.pddl"
    LOG="${OUT_DIR}/fd_seq-opt-lmcut_${domain}_${prob}.log"

    echo "Running FD seq-opt-lmcut on ${domain}/${prob} (600s limit)..."
    timeout 600 python3 "${FD_DIR}/fast-downward.py" \
      --alias seq-opt-lmcut \
      "$DOM_PDDL" "$PROB_PDDL" > "$LOG" 2>&1
    echo "Finished (or timed out) ${domain}/${prob}"
  done
done

echo "FD grid completed"
date

