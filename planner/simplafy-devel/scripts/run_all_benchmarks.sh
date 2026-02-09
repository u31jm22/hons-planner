#!/bin/bash -l

## We need to submit this using the logged in options because otherwise I cannot access pre-configured conda environments
## Don't forget to run this script with sbatch
# ===================================================================================================================
#                                           SLURM Configuration
# -------------------------------------------------------------------------------------------------------------------

# Slurm Configuration --> taken from Aidan Durrant's GitHub page but can be modified to run on Maxwell if necessary.

#SBATCH --job-name=SimPlaFy-Benchmark
#SBATCH --nodes=9                       # number of nodes
#SBATCH --cpus-per-task=1               # number of cores
#SBATCH --mem=32G                       # memory pool for all cores
#SBATCH --ntasks-per-node=1             # one job per node
#SBATCH --partition=uoa-compute 
#SBATCH -o slurm.planning.%j.out                 # STDOUT
#SBATCH -e slurm.planning.%j.err                 # STDERR
#SBATCH --mail-type=ALL 
#SBATCH --mail-user=felipe.meneguzzi@abdn.ac.uk  # gets username from hpc env login (change as appropriate)

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
    conda activate simplafy 
elif [ -n "$SLURM_JOB_ID" ]; then
    echo "*** RUNNING ON HPC - USING SLURM ***"
    module load miniconda3
    module load git
    conda activate simplafy
else
    echo "*** RUNNING LOCALLY - SLURM WILL NOT BE USED ***"
fi

shopt -s expand_aliases

# Allows use of either python3 or python keywords on the PATH -- useful if multiple versions of python are installed.
if command -v python &>/dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        alias python=python
    else
        if command -v python3 &>/dev/null; then
            alias python=python3
        else
            echo "*** ERROR! Python 3 is required but not found. ***"
            exit 1
        fi
    fi
elif command -v python3 &>/dev/null; then
    alias python=python3
else
    echo "*** ERROR! No Python interpreter found. ***"
    exit 1
fi

pushd ..

export PYTHONPATH=PYTHONPATH:`pwd`/src

# Create output directory within simplafy folder --> both sets of benchmarks output to tmp.
output_dir="tmp"
mkdir -p "$output_dir"

# ===================================================================================================================
#                                           Function calls
# -------------------------------------------------------------------------------------------------------------------

# Run tasks for each directory...
run_tasks_for_directory() {
    # Get the directory name.
    local dir="$1"
    echo "Processing directory: $dir ..."

    # Collect domain name from directory.
    domain_name=$(basename $dir)

    # Mac and Linux use different ways to map files... this accounts for both.
    # Identifies domain and problem sets within a directory.
    if [[ "$(uname)" == "Linux" ]]; then
        mapfile -t domains < <(find "$dir" -maxdepth 4 \( -name "domain*.pddl" -o -name "$domain_name*.pddl" \) | sort)
        mapfile -t tasks   < <(find "$dir" -maxdepth 4 \( -name "pb*.pddl" -o -name "task*.pddl" \) | sort)
    elif [[ "$(uname)" == "Darwin" ]]; then
        domains=()
        while IFS= read -r line; do
            domains+=( "$line" )
        done < <(find "$dir" -maxdepth 4 \( -name "domain*.pddl" -o -name "$domain_name*.pddl" \) | sort)

        tasks=()
        while IFS= read -r line; do
            tasks+=( "$line" )
        done < <(find "$dir" -maxdepth 4 \( -name "pb*.pddl" -o -name "task*.pddl" \) | sort)
    else
        echo "*** ERROR! Unsupported Operating System: $(uname) ***"
    fi

    # If we found domain and problem sets...
    if [ ${#domains[@]} -gt 0 ] && [ ${#tasks[@]} -gt 0 ]; then
        if [ ${#domains[@]} -eq 1 ]; then
            # Iterate through each task in the domain...
            for task_file in "${tasks[@]}"; do
                # Collect domain and task names from the args passed in...
                domain_file="${domains[0]}"
                domain_name=$(basename "${domain_file%/*}")
                task_name=$(basename "$task_file" .pddl)
                task_output_dir="$output_dir/domains/$domain_name/$task_name"

                # Create an output directory for each task, and an individual txt file for cmd output.
                mkdir -p "$task_output_dir"
                output_file="$task_output_dir/$domain_name-$task_name-simplafy.txt"

                # Run simplafy via srun if on HPC, else call python normally.
                if [ -n "$SLURM_JOB_ID" ]; then
                    echo "Running SimPlaFy VIA HPC CLUSTER on domain: $domain_file, task: $task_file, output $output_file ..."
                    srun --time="$HPCMAXEXEC" python -m simplafy -he lmcut -s astar -p -v "$domain_file" "$task_file" > "$output_file" 2>&1
                else
                    echo "Running SimPlaFy LOCALLY on domain: $domain_file, task: $task_file, output $output_file ..."
                    python -m simplafy -he lmcut -s astar -p -v "$domain_file" "$task_file" > "$output_file" 2>&1
                fi
            done
        fi
    else
        echo "*** ERROR! No domain or task files found in directory $dir ***"
    fi
}


# ===================================================================================================================
#                                           Main execution tasks
# -------------------------------------------------------------------------------------------------------------------


# Default execution type if no flags passed into the shell script.
EXEC_TYPE="all"

while [[ $# -gt 0 ]]; do
    # --alltasks runs the SimPlaFy planner on all domains/problems contained in examples folder.
    # --benchmark runs the benchmarking scripts, first generate_benchmark.sh then planning-benchmark.sh
    # --exclude takes an unlimited number of params, each param is a domain within examples folder to be EXCLUDED on this run.
    case "$1" in
        --alltasks)
            echo "Running all tasks in /examples only, no internal benchmarks"
            EXEC_TYPE="alltasks"
            ;;
        --benchmark)
            echo "Running internal benchmarks only, no tasks in /examples"
            EXEC_TYPE="benchmark"
            ;;
        --default)
            EXEC_TYPE="all"
            ;;
        --exclude)
            shift
            while [[ $# -gt 0 && "$1" != --* ]]; do
                exclude_domains+=("$1")
                shift
            done
            continue
            ;;
        -*)
            echo "Unknown option $1"
            exit 1
            ;;
        *)
            ;;
    esac
    shift
done

# If we're running SimPlaFy on all example domain and problem sets, then
if [[ "${EXEC_TYPE}" == "all" || "${EXEC_TYPE}" == "alltasks" ]]; then
    # Report to user what domains will be excluded
    if [[ ${#exclude_domains[@]} -gt 0 ]]; then
        echo "Excluding the following domains: ${exclude_domains[@]}"
    fi

    # Define exactly what domains will be analysed.
    directories=()
    exclude_domains=()

    while IFS= read -r dir_path; do
        # Exclude intention planning domain/problems by default - we do NOT handle these in here.
        if [[ "$dir_path" == "./src/examples/intention"* ]]; then
            continue
        fi

        # Check for domains passed in using the --exclude flag.
        domain_name=$(basename "$dir_path")
        skip_domain=false
        for ex in "${exclude_domains[@]}"; do
            if [[ "$domain_name" == "$ex" ]]; then
                skip_domain=true
                break
            fi
        done
        if $skip_domain; then
            continue
        fi

        # Return subfolders - for example if we include pyper's domains as
        # a subfolder this'll pick these domains up too.
        if ! find "$dir_path" -mindepth 1 -maxdepth 1 -type d | grep -q .; then
            directories+=( "$dir_path" )
        fi
    done < <(find ./src/examples -mindepth 1 -type d)

    # display what directories were selected
    echo "Selected directories:"
    printf '%s\n' "${directories[@]}"
    echo ""

    # run simplafy on each directory using function previously defined
    for dir in "${directories[@]}"; do
        run_tasks_for_directory "$dir"
    done

    echo "*** Finished running domain examples! ***"
fi

# If we're running the benchmarking component of SimPlaFy, then
if [[ "${EXEC_TYPE}" == "all" || "${EXEC_TYPE}" == "benchmark" ]]; then
    cd scripts

    # Run benchmarking shell scripts using srun if on HPC else run normally.
    if [ -n "$SLURM_JOB_ID" ]; then
        echo "Running generate_benchmark.sh on SLURM..."
        srun bash generate_benchmark.sh 2>&1

        echo "Running planning-benchmark.sh on SLURM..."
        srun bash planning-benchmark.sh 2>&1
    else
        echo "Running generate_benchmark.sh ..."
        bash generate_benchmark.sh
        
        echo "Running planning-benchmark.sh ..."
        bash planning-benchmark.sh
    fi
    echo "*** Finished running benchmarks! ***"
fi

echo "Execution Completed!"
