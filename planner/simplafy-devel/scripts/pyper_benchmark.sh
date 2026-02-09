#!/bin/bash -l

## We need to submit this using the logged in options because otherwise I cannot access pre-configured conda environments
## Don't forget to run this script with sbatch

#SBATCH --job-name=Planning-Benchmark
#SBATCH --nodes=8 # number of nodes
#SBATCH --cpus-per-task=1 # number of cores
#SBATCH --mem=64G # memory pool for all cores

#SBATCH --ntasks-per-node=1 # one job per node
#SBATCH -o slurm.planning.%j.out # STDOUT
#SBATCH -e slurm.planning.%j.err # STDERR

#SBATCH --mail-type=ALL
#SBATCH --mail-user=felipe.meneguzzi@abdn.ac.uk  # gets username from hpc env login (change as appropriate)


# This assumes pyperplan's benchmarks are in /tmp
HPCNAME="maxlogin1.int.maxwell.abdn.ac.uk"        # change as appropriate by typing echo $HOSTNAME into HPC terminal
HPCMAXEXEC="23:10:00"                   # maximum slurm run time in hh:mm:ss
echo "Started running on $(hostname)"
date
# Load modules if running on HPC
if [ "$HOSTNAME" == ${HPCNAME} ]; then
    echo "*** RUNNING ON HPC ***"
    module load miniconda3
    module load git
    conda activate simplafy 
elif [ -n "$SLURM_JOB_ID" ]; then
    echo "*** RUNNING ON HPC - USING SLURM ***"
    module load miniconda3
    module load git
    conda activate simplafy
else
    echo "*** RUNNING LOCALLY - SLURM WILL NOT BE USED ***"
    # conda activate simplafy
    conda activate py_heu 
fi

echo $CONDA_DEFAULT_ENV
echo $CONDA_PREFIX

pushd ..

export PYTHONPATH=PYTHONPATH:`pwd`/src

# dirs=$(find ./tmp -type f -name "domain.pddl" -exec dirname {} \; | sort -u)
dirs=$(find ./tmp -type f \( -name "domain.pddl" -o -name "domain[0-9][0-9].pddl" \) \
       -exec dirname {} \; | sort -u)

# Loop through each unique directory that contains domain.pddl
# find ./tmp -type f -name "domain.pddl" -exec dirname {} \; | sort -u | while read -r dir; do
for dir in $dirs; do
    echo "Processing directory: $dir"
    
    # Change to the directory
    # cd "$dir" || continue
    # pwd
    
    # Run your command here
    # Example: run a script or a planner
    echo "Running command in $dir"
    # ./your-command-here.sh
    # or
    # planner domain.pddl problem.pddl > output.txt

    # output_file="$task_output_dir/$domain_name-$task_name-simplafy.txt"
    output_file="$dir/output-simplafy.txt"
    error_file="$dir/output-simplafy.err"

    if [ -n "$SLURM_JOB_ID" ]; then
        echo "Running SimPlaFy VIA HPC CLUSTER on domain: $domain_file, task: $task_file, output $output_file ..."
        # srun --time="$HPCMAXEXEC" python -m simplafy -he lmcut -s astar -p -v "$domain_file" "$task_file" > "$output_file" 2>&1
        srun -o "$output_file" -e "$error_file" --time="$HPCMAXEXEC" python -m pddl.run_benchmark -v -p -o $dir -d $dir scripts/baseline-ff.yaml scripts/baseline-lm.yaml scripts/baseline-lmcut.yaml scripts/baseline-max.yaml &
    else
        echo "Running SimPlaFy LOCALLY on domain: $domain_file, task: $task_file, output $output_file ..."
        # python -m simplafy -he lmcut -s astar -p -v "$domain_file" "$task_file" > "$output_file" 2>&1
        python -m pddl.run_benchmark -v -p -o $dir -d $dir scripts/baseline-ff.yaml scripts/baseline-lm.yaml scripts/baseline-lmcut.yaml scripts/baseline-max.yaml > "$output_file" 2> "$error_file" &
    fi

    # srun --time="$HPCMAXEXEC" python -m pddl.run_benchmark -p -o $dir -d $dir scripts/baseline-ff.yaml scripts/baseline-lm.yaml scripts/baseline-lmcut.yaml scripts/baseline-max.yaml
    # python -m pddl.run_benchmark -p -o $dir -d $dir scripts/baseline-ff.yaml scripts/baseline-lm.yaml scripts/baseline-lmcut.yaml scripts/baseline-max.yaml

    # Return to the original directory
    # cd - > /dev/null
done

wait
echo "Execution Completed!"