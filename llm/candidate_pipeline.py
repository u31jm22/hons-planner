"""
Pipeline for generating, evaluating, and selecting LLM-generated heuristic candidates.
"""
import json
import subprocess
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


def is_trivial_goal_count(code):
    """
    Heuristically detect trivial goal-count-style heuristics.
    Returns True if the code should be rejected as too simple.
    """
    lowered = code.lower()

    # Clearly forbidden patterns
    forbidden_patterns = [
        r"len\s*\(\s*positive_goals\s*-\s*state\s*\)",
        r"len\s*\(\s*positive_goals\s*-\s*set\s*\(\s*state\s*\)\s*\)",
        r"len\s*\(\s*positive_goals\s*\.difference\s*\(",
        r"sum\s*\(\s*1\s*for\s+g\s+in\s+positive_goals\s+if\s+g\s+not\s+in\s+state\s*\)",
        r"sum\s*\(\s*\[\s*1\s*for\s+g\s+in\s+positive_goals\s+if\s+g\s+not\s+in\s+state\s*\]\s*\)",
        r"unsatisfied_goals\s*=\s*len\s*\(\s*positive_goals\s*-\s*state\s*\)",
        r"remaining_goals\s*=\s*positive_goals\s*-\s*state",
    ]
    for pat in forbidden_patterns:
        if re.search(pat, lowered):
            return True

    # Token-based weak detector for "return <only len/abs/int/float of state/goals>"
    no_comments = re.sub(r"#.*", "", code)
    no_ws = re.sub(r"\s+", "", no_comments)

    if "defh(state,goals):" in no_ws:
        body = no_ws.split("defh(state,goals):", 1)[1]
    elif "defh(" in no_ws:
        body = no_ws.split("defh(", 1)[1]
    else:
        body = no_ws

    if "return" in body:
        ret_part = body.split("return", 1)[1]
        ret_part = ret_part.split("def", 1)[0]
        tokens = re.split(r"[^a-zA-Z0-9_]+", ret_part)
        tokens = [t for t in tokens if t]

        allowed_tokens = {
            "len", "abs", "int", "float",
            "positive_goals", "negative_goals", "state",
            "g", "0", "1", "2", "3", "4", "5",
        }

        if tokens and all(t in allowed_tokens for t in tokens):
            return True

    return False


def strip_markdown_fences(text):
    text = re.sub(r"```python\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    return text.strip()


def extract_h_function(response):
    """
    Extract a `def h(state, goals): ...` function from a model response.
    """
    response = strip_markdown_fences(response)
    lines = response.splitlines()

    start = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("def h("):
            start = i
            break

    if start is None:
        return response.strip()

    code_lines = []
    base_indent = len(lines[start]) - len(lines[start].lstrip())

    for j in range(start, len(lines)):
        line = lines[j]
        if j == start:
            code_lines.append(line.rstrip())
            continue

        indent = len(line) - len(line.lstrip())

        stripped = line.lstrip()
        if indent <= base_indent and (stripped.startswith("def ") or stripped.startswith("class ")):
            break

        code_lines.append(line.rstrip())

    return "\n".join(code_lines).strip()


def compile_check(code):
    """
    Compile candidate code in-memory. Return (ok, error_message).
    """
    try:
        compile(code, "<candidate>", "exec")
        return True, ""
    except Exception as e:
        return False, str(e)


class CandidatePipeline:
    """
    Generates multiple candidate heuristics per domain and selects the best.
    """

    def __init__(self, model, project_root):
        self.model = model
        self.project_root = project_root
        self.domains_dir = project_root / "domains"
        self.experiments_dir = project_root / "experiments"
        self.llm_dir = project_root / "llm"

        self.experiments_dir.mkdir(exist_ok=True)
        (self.llm_dir / "candidates").mkdir(exist_ok=True)

    def generate_candidates(self, domain_name, num_candidates=5):
        domain_path = self.domains_dir / domain_name / "domain.pddl"
        if not domain_path.exists():
            raise FileNotFoundError("Domain not found: {}".format(domain_path))

        domain_pddl = domain_path.read_text()

        candidates = []
        for i in range(num_candidates):
            print("Generating candidate {}/{} for {}...".format(i + 1, num_candidates, domain_name))
            prompt = self._build_prompt(domain_name=domain_name, domain_pddl=domain_pddl, variant_id=i)
            code = self._generate_heuristic_code(prompt, domain_name=domain_name)

            candidates.append({
                "id": "{}_candidate_{}".format(domain_name, i + 1),
                "code": code,
                "prompt_variant": i,
                "domain": domain_name,
            })

        out_json = self.llm_dir / "candidates" / "{}_candidates.json".format(domain_name)
        out_json.write_text(json.dumps(candidates, indent=2))
        print("Saved {} candidates to {}".format(num_candidates, out_json))
        return candidates

    def _generate_heuristic_code(self, prompt, domain_name):
        """
        Ask LLM to generate heuristic code with retries + filters.
        """
        max_retries = 6

        for attempt in range(1, max_retries + 1):
            try:
                response = self.model.predict(prompt)
                code = extract_h_function(response)

                if "def h(" not in code:
                    print("  Warning: no def h(...) found (attempt {}), retrying...".format(attempt))
                    continue
                if "return" not in code:
                    print("  Warning: no return found (attempt {}), retrying...".format(attempt))
                    continue

                ok, err = compile_check(code)
                if not ok:
                    print("  Warning: candidate does not compile (attempt {}): {}".format(attempt, err))
                    continue

                if is_trivial_goal_count(code):
                    print("  Warning: trivial goal-count detected (attempt {}), retrying...".format(attempt))
                    continue

                return code

            except Exception as e:
                print("  Error (attempt {}): {}".format(attempt, e))

        # Fallback
        print("  Using fallback heuristic (goal-count) after retries exhausted")
        return (
            "def h(state, goals):\n"
            "    \"\"\"\n"
            "    Fallback heuristic: goal-count.\n"
            "    state: frozenset of tuples\n"
            "    goals: (positive_goals, negative_goals)\n"
            "    \"\"\"\n"
            "    positive_goals, negative_goals = goals\n"
            "    unsat = sum(1 for g in positive_goals if g not in state)\n"
            "    viol = sum(1 for g in negative_goals if g in state)\n"
            "    v = unsat + viol\n"
            "    return float(v) if v >= 0 else 0.0\n"
        )

    def _build_prompt(self, domain_name, domain_pddl, variant_id):
        """
        Strong prompt with domain notes and diversity hints.
        """
        domain_notes = ""
        if domain_name.lower() == "gripper":
            domain_notes = """
Domain notes (Gripper):
Predicates:
- ('at-robby', room) : robot location
- ('at', ball, room) : ball location
- ('carry', ball, gripper) : ball carried
- ('free', gripper) : gripper free
Typical actions: move, pick, drop
Robot moves between rooms (rooma/roomb). Two grippers => can carry up to 2 balls.
Heuristic should approximate remaining pick/drop actions + remaining moves/trips (batching balls by room).
"""
        elif domain_name.lower() == "blocksworld":
            domain_notes = """
Domain notes (Blocksworld):
Predicates:
- ('on', x, y) : block x is on y
- ('ontable', x) : block x is on the table
- ('clear', x) : no block on x
- ('holding', x) : robot arm holds x
- ('handempty',) : robot arm is empty
Typical actions: pickup, putdown, stack, unstack.
Heuristic should reason about blocks not yet in their goal positions and the number of moves to unstack/move them.
"""
        elif domain_name.lower() == "depots":
            domain_notes = """
Domain notes (Depots):
Predicates:
- ('at', truck/hoist, place) : truck or hoist location
- ('on', crate, surface) : crate stacked on surface
- ('in', crate, truck) : crate loaded in truck
- ('lifting', hoist, crate) : hoist currently lifting crate
- ('available', hoist) : hoist is free
- ('clear', surface) : surface has nothing on top
Typical actions: drive, lift, drop, load, unload.
Heuristic should count unplaced crates, estimate lifts/drops and truck drives needed.
"""
        elif domain_name.lower() == "logistics":
            domain_notes = """
Domain notes (Logistics):
Predicates:
- ('at', obj, loc) : package or vehicle at location
- ('in', pkg, vehicle) : package loaded in vehicle
Typical actions: load, unload, drive-truck, fly-airplane.
Heuristic should count undelivered packages and estimate loads/unloads + drives/flights needed.
"""
        elif domain_name.lower() == "transport":
            domain_notes = """
Domain notes (Transport):
Predicates:
- ('at', obj, loc) : object or vehicle at location
- ('in', pkg, veh) : package loaded in vehicle
- ('road', loc1, loc2) : road between locations (if present)
Vehicles carry packages along roads; typical actions: load, unload, drive.
Heuristic should approximate remaining load/unload actions and drives to move packages to goal locations.
"""

        system = """You are an expert in classical planning and PDDL acting as a Python code generator for heuristic functions.
Your task is to write a single Python function h(state, goals) that computes a domain-aware heuristic estimate of the remaining steps to reach the goal in a STRIPS-style planning problem.

Constraints:
- Output only valid Python code for the function h(state, goals).
- No imports, no I/O, no randomness, no external modules, no planner internals.
- Must be total: always returns a non-negative int or float.
- Time complexity at most linear in |state| + |goals| (no search, no simulating successor states).
- Must be domain-aware and NOT a trivial goal-count heuristic:
  - No len(positive_goals - state)
  - No sum(1 for g in positive_goals if g not in state) as the main logic
  - No simple reweighting of goal counts.
Output format:
def h(state, goals):
    \"\"\"
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at', 'ball1', 'rooma')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    \"\"\"
    # your code here
"""

        user = "You will receive the PDDL domain and the Python state representation.\nWrite a domain-aware heuristic h(state, goals) using predicates/structure to estimate remaining cost.\n\nPython representation:\n- state is frozenset of ground atoms tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')\n- goals is (positive_goals, negative_goals), each a frozenset of tuples\n\nPDDL Domain:\n{}\n\n{}\n\nReturn ONLY the Python function h(state, goals) as valid Python code, with no explanations or markdown.\n".format(domain_pddl, domain_notes)

        diversity = [
            "\n# Diversity hint: try batching/ceil trips with capacity 2.\n",
            "\n# Diversity hint: incorporate robot room vs source rooms.\n",
            "\n# Diversity hint: treat carried balls differently from at(ball, room).\n",
            "\n# Diversity hint: approximate pick/drop + move counts.\n",
            "\n# Diversity hint: avoid any goal-count-like set difference.\n",
        ][variant_id % 5]

        return system + "\n" + user + diversity

    def evaluate_candidate(self, candidate, training_problems):
        domain_name = candidate["domain"]
        candidate_id = candidate["id"]

        candidate_file = self.llm_dir / "candidates" / "{}.py".format(candidate_id)
        candidate_file.write_text(candidate["code"])

        results = {
            "candidate_id": candidate_id,
            "coverage": 0,
            "total_expansions": 0,
            "total_time": 0.0,
            "solved": [],
            "failed": [],
        }

        for prob in training_problems:
            print("  Testing {} on {}...".format(candidate_id, prob))
            success, expansions, t = self._run_planner_with_candidate(domain_name, prob, candidate_file)
            if success:
                results["coverage"] += 1
                results["total_expansions"] += expansions
                results["total_time"] += t
                results["solved"].append(prob)
            else:
                results["failed"].append(prob)

        if results["coverage"] > 0:
            results["avg_expansions"] = results["total_expansions"] / results["coverage"]
            results["avg_time"] = results["total_time"] / results["coverage"]
        else:
            results["avg_expansions"] = float("inf")
            results["avg_time"] = float("inf")

        return results



    def _run_planner_with_candidate(self, domain_name, problem_file, candidate_py_file):
        domain_path = self.domains_dir / domain_name / "domain.pddl"
        problem_path = self.domains_dir / domain_name / problem_file
        eval_script = self.llm_dir / "evaluate_candidate.py"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(eval_script),
                    "--domain",
                    str(domain_path),
                    "--problem",
                    str(problem_path),
                    "--candidate",
                    str(candidate_py_file),
                    "--timeout",
                    "300",
                ],
                capture_output=True,
                text=True,
                timeout=305,
            )

            output = result.stdout.strip()
            if output.startswith("SUCCESS"):
                parts = output.split()
                expansions = int(parts[1])
                t = float(parts[2])
                return True, expansions, t
            return False, 0, 0.0

        except Exception as e:
            print("    Error running planner: {}".format(e))
            return False, 0, 0.0

    def select_best_candidate(self, domain_name, evaluation_results):
        if not evaluation_results:
            return None

        sorted_results = sorted(
            evaluation_results,
            key=lambda r: (-r["coverage"], r["avg_expansions"], r["avg_time"]),
        )
        best = sorted_results[0]

        print("\n=== Best candidate for {} ===".format(domain_name))
        print("ID: {}".format(best["candidate_id"]))
        print("Coverage: {}".format(best["coverage"]))
        print("Avg Expansions: {}".format(best.get("avg_expansions", "N/A")))
        print("Avg Time: {}".format(best.get("avg_time", "N/A")))

        return best

