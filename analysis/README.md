# Analysis Scripts — How to Run

All commands are run from the **project root** (`~/hons-llm-heuristics`).

---

## 1. Run the Full Experimental Grid (MacLeod)

### Classical baselines + LLM heuristics (all 30 instances, all domains, all models)
```bash
sbatch scripts/run_all30_full.slurm
```
Runs `ff`, `add`, `max` and LLM heuristics for `gpt-4o-mini`, `gpt-4.1-mini`, `gpt-4.1`, `llama`
across all 6 domains × 30 instances each.  
Results → `results/<domain>_<heuristic>_all30.csv`

### FD LM-Cut baseline (all 30 instances, all domains)
```bash
sbatch scripts/run_fd_all30.sh
# or locally:
bash scripts/run_fd_all30.sh
```
Results → `results/<domain>_lmcut_all30.csv`

---

## 2. LLaMA via LM Studio (local Mac only)

The `llama` model runs through LM Studio's OpenAI-compatible API.

1. Start LM Studio and load your LLaMA model.
2. Make sure the server is running at `http://localhost:1234/v1`.
3. Run locally (not on MacLeod):
```bash
source venv/bin/activate
for domain in blocksworld gripper logistics miconic depots rovers; do
  python -m planner.run_grid \
    --domain $domain \
    --mode llm-selected \
    --model llama \
    --instances-file all_instances.txt \
    --output-csv results/${domain}_llama_llm_all30.csv
done
```

---

## 3. Regenerate LLM Candidates for a New Model/Domain

To regenerate candidates (e.g. for `gpt-4.1` on `rovers`):
```bash
export OPENAI_API_KEY=sk-...
python llm/run_candidate_pipeline.py rovers --model-name gpt-4.1
```
This writes `llm/candidates/rovers_selected_gpt-4.1.json`.

For LLaMA via LM Studio (local only):
```bash
python - <<EOF
from llm.lmstudio_wrapper import LMStudioModel
from llm.candidate_pipeline_new import CandidatePipeline
from pathlib import Path
import json

model = LMStudioModel(model="llama3", base_url="http://localhost:1234/v1")
pipeline = CandidatePipeline(model=model, project_root=Path("."))
candidates = pipeline.generate_candidates("rovers", num_candidates=5)
results = [pipeline.evaluate_candidate(c, ["p01.pddl","p02.pddl","p03.pddl","p04.pddl","p05.pddl"]) for c in candidates]
best = pipeline.select_best_candidate("rovers", results, model_name="llama")
json.dump(best, open("llm/candidates/rovers_selected_llama.json","w"), indent=2)
EOF
```

---

## 4. Dataset Statistics

```bash
python analysis/dataset_stats.py
```
Outputs:
- `analysis/dataset_section.md` — Markdown table for README/notes
- `analysis/dataset_section.tex` — LaTeX section (`\input{analysis/dataset_section}`)

---

## 5. Aggregate Results

```bash
python analysis/aggregate_all30.py
```
Reads all `results/*_all30.csv` files and writes `results/summary_all30.csv`.

---

## 6. Generate LaTeX Tables

```bash
python analysis/aggregate_all30.py   # ensure summary_all30.csv is up to date
python analysis/generate_latex_tables.py
```
Writes `analysis/tables.tex`. In your thesis:
```latex
\input{analysis/tables}
```

---

## 7. Generate Plots

```bash
python analysis/plot_results.py
```
Writes PNGs to `figures/`:
- `figures/coverage.png`
- `figures/expansions.png`
- `figures/search_time.png`
- `figures/plan_length_ratio.png`

---

## File Naming Convention

| Pattern | Description |
|---|---|
| `results/<domain>_ff_all30.csv` | FF baseline, all 30 instances |
| `results/<domain>_add_all30.csv` | Additive heuristic |
| `results/<domain>_max_all30.csv` | Max heuristic |
| `results/<domain>_lmcut_all30.csv` | FD LM-Cut (optimal, from FD logs) |
| `results/<domain>_gpt-4o-mini_llm_all30.csv` | LLM heuristic, gpt-4o-mini |
| `results/<domain>_gpt-4.1-mini_llm_all30.csv` | LLM heuristic, gpt-4.1-mini |
| `results/<domain>_gpt-4.1_llm_all30.csv` | LLM heuristic, gpt-4.1 |
| `results/<domain>_llama_llm_all30.csv` | LLM heuristic, LLaMA via LM Studio |

Domains: `blocksworld`, `gripper`, `logistics`, `miconic`, `depots`, `rovers`

---

## Dependencies

```bash
pip install openai matplotlib pandas   # pandas optional, matplotlib for plots
```
The virtual environment on MacLeod already has `openai` installed.
