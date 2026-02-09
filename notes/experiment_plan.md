# Experiment Plan

## Domains

- Blocksworld (4-op variant used in planner repo)
- Logistics (IPC-style variant in `domains/logistics`)

## Instances

- Blocksworld:
  - Training: p01, p02, p03
  - Test:     p04, p05
- Logistics:
  - Training: p01, p02, p03
  - Test:     p04, p05

## Heuristics

- Baselines:
  - max  (MaxHeuristic)
  - add  (AdditiveHeuristic)
  - ff   (FastForwardHeuristic)
- LLM-based:
  - Multiple candidate LLMGeneratedHeuristic functions per domain
  - One selected “best” LLM heuristic per domain based on training tasks

## Metrics

- Coverage: number of tasks solved within time/step limits
- Node expansions: `# Expansions` from planner logs
- Runtime: `Search Time` in seconds from planner logs

## Training-phase procedure (per domain)

1. Generate N candidate heuristics using `llm/generate_heuristic.py`.
2. For each candidate, run planner on training tasks with:
   - greedy best-first search using that heuristic (current A* max-cost=1 setup).
3. Record coverage, expansions, search time.
4. Select the best candidate based on:
   - highest coverage,
   - then lowest total node expansions (tie-breaker),
   - then lowest total runtime (secondary tie-breaker).

## Test-phase procedure (per domain)

1. Fix:
   - max, add, ff (baseline heuristics),
   - the selected LLM heuristic for that domain.
2. Run each heuristic on all test tasks.
3. Collect metrics into `blocksworld_summary.csv` and `logistics_summary.csv`
   (one row per problem × heuristic).

## Compute constraints

- Runs on laptop for development; larger batches via MacLeod (SLURM) with:
  - per-task time limit T (e.g. 60s),
  - per-task memory limit as per cluster defaults.

## Selected LLM heuristics (training-based)

- Blocksworld:
  - N candidates = 5
  - Selected candidate: id = 2 (highest coverage, lowest total_expansions)
