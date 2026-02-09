#!/bin/bash

HPCNAME="maxlogin1.int.maxwell.abdn.ac.uk"        # change as appropriate by typing echo $HOSTNAME into HPC terminal
HPCMAXEXEC="00:10:00"                   # maximum slurm run time in hh:mm:ss

# ===================================================================================================================
#                                           Configure environment
# -------------------------------------------------------------------------------------------------------------------
echo "Started running on $(hostname)"
date

# Load modules if running on HPC
if [ "$HOSTNAME" == ${HPCNAME} ]; then
    echo "*** RUNNING ON HPC ***"
    module load miniconda3
    module load git
    module load texlive
    conda activate simplafy 
elif [ -n "$SLURM_JOB_ID" ]; then
    echo "*** RUNNING ON HPC - USING SLURM ***"
    module load miniconda3
    module load git
    module load texlive
    conda activate simplafy
else
    echo "*** RUNNING LOCALLY - SLURM WILL NOT BE USED ***"
    conda activate py_heu
fi

pushd ..

V=-v
P=-p
TIKZ=-t
OUT_DIR="tmp"
DOMAIN_DIR="tmp"
# EXCLUSIVE="--exclusive"
EXCLUSIVE=""
# MEMORY="--mem=48G"
PARTITION="--partition=uoa-compute"

mkdir $OUT_DIR

export PYTHONPATH=PYTHONPATH:`pwd`/src
HEURISTICS=("lm" "lmcut" "hmax" "hff")
DOMAINS=("prodcell" "blocksworld" "miconic" "satellite")

for h in "${HEURISTICS[@]}"; do
    echo "Running experiments for ${h}"
    mkdir "${OUT_DIR}/${h}"
    for domain in "${DOMAINS[@]}"; do
        echo "Launching benchmark for ${domain}"

        if [ "$HOSTNAME" == ${HPCNAME} ]; then
            SLURM_OUT="-o ${OUT_DIR}/${h}/slurm.intention.${domain}.%j.out"
            SLURM_ERR="-e ${OUT_DIR}/${h}/slurm.intention.${domain}.%j.err"
            # SLURM_OUT=""
            LABEL="${h}.${domain}"
            sbatch ${EXCLUSIVE} ${SLURM_OUT} ${MEMORY} ${PARTITION} --job-name="${LABEL}" scripts/intention-planning-slurm.sh $V $P $TIKZ -o ${OUT_DIR}/${h} -d ${DOMAIN_DIR}/${domain} scripts/intention-baseline-${h}.yaml scripts/intention-planner-${h}.yaml &
        else
            OUT="${OUT_DIR}/${h}/intention.${domain}.out"
            # echo "srun ${EXCLUSIVE} ${SLURM_OUT} python3 -m pddl.run_benchmark $V $P -o ${OUT_DIR}/${h} -d ${DOMAIN_DIR}/${domain} scripts/intention-baseline-${h}.yaml scripts/intention-planner-${h}.yaml"
            # srun ${EXCLUSIVE} ${SLURM_OUT} python3 -m pddl.run_benchmark $V $P -o ${OUT_DIR}/${h} -d ${DOMAIN_DIR}/${domain} scripts/intention-baseline-${h}.yaml scripts/intention-planner-${h}.yaml &
            python -m pddl.run_benchmark $V $P $TIKZ -o ${OUT_DIR}/${h} -d ${DOMAIN_DIR}/${domain} scripts/intention-baseline-${h}.yaml scripts/intention-planner-${h}.yaml > ${OUT}
        fi
    done
done