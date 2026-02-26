"""
Pipeline for generating, evaluating, and selecting LLM-generated heuristic candidates
(for new LLM experiments).
"""
import json
import subprocess
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


def is_trivial_goal_count(code: str) -> bool:
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


def strip_markdown_fences(text: str) -> str:
    text = re.sub(r"```python\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    return text.strip()


def extract_h_function(response: str) -> str:
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


def compile_check(code: str) -> Tuple[bool, str]:
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
    This version is for new LLM experiments; existing results stay as they are.
    """

    def __init__(self, model, project_root: Path):
        self.model = model
        self.project_root = project_root
        self.domains_dir = project_root / "domains"
        self.experiments_dir = project_root / "experiments"
        self.llm_dir = project_root / "llm"

        self.experiments_dir.mkdir(exist_ok=True)
        (self.llm_dir / "candidates").mkdir(exist_ok=True)

    def generate_candidates(self, domain_name: str, num_candidates: int = 5):
        domain_path = self.domains_dir / domain_name / "domain.pddl"
        if not domain_path.exists():
            raise FileNotFoundError(f"Domain not found: {domain_path}")

        domain_pddl = domain_path.read_text()

        candidates = []
        for i in range(num_candidates):
            print(f"Generating candidate {i + 1}/{num_candidates} for {domain_name}...")
            prompt = self._build_prompt(domain_name=domain_name, domain_pddl=domain_pddl, variant_id=i)
            code = self._generate_heuristic_code(prompt)

            candidates.append({
                "id": f"{domain_name}_candidate_{i + 1}",
                "code": code,
                "prompt_variant": i,
                "domain": domain_name,
            })

        out_json = self.llm_dir / "candidates" / f"{domain_name}_candidates.json"
        out_json.write_text(json.dumps(candidates, indent=2))
        print(f"Saved {num_candidates} candidates to {out_json}")
        return candidates

    def _generate_heuristic_code(self, prompt: str) -> str:
        """
        Ask LLM to generate heuristic code with retries + filters.
        """
        max_retries = 6

        for attempt in range(1, max_retries + 1):
            try:
                response = self.model.predict(prompt)
                code = extract_h_function(response)

                if "def h(" not in code:
                    print(f"  Warning: no def h(...) found (attempt {attempt}), retrying...")
                    continue
                if "return" not in code:
                    print(f"  Warning: no return found (attempt {attempt}), retrying...")
                    continue

                ok, err = compile_check(code)
                if not ok:
                    print(f"  Warning: candidate does not compile (attempt {attempt}): {err}")
                    continue

                if is_trivial_goal_count(code):
                    print(f"  Warning: trivial goal-count detected (attempt {attempt}), retrying...")
                    continue

                return code

            except Exception as e:
                print(f"  Error (attempt {attempt}): {e}")

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

    def _build_prompt(self, domain_name: str, domain_pddl: str, variant_id: int) -> str:
        """
        Strong prompt with domain notes and diversity hints.
        """
        dn = domain_name.lower()
        domain_notes = ""

        if dn == "gripper":
            domain_notes = """
You are a highly skilled professor in AI planning and a proficient Python programmer.
Your task is to design a domain-dependent heuristic for the classical planning domain "Gripper".

The planner represents states and goals as follows:
- state: a frozenset of tuples like
    ('at-robby', 'rooma'),
    ('at', 'ball1', 'rooma'),
    ('carry', 'ball2', 'left'),
    ('free', 'right'), etc.
- goals: (positive_goals, negative_goals), each a frozenset of tuples,
  e.g. ('at', 'ball1', 'roomb') meaning ball1 should end up in roomb.

You must implement the following Python function:

    def h(state, goals):
        \"\"\"
        Domain-specific heuristic for the Gripper domain.
        state: frozenset of ground predicates describing the current world.
        goals: (positive_goals, negative_goals), each a frozenset of ground predicates.
        Returns: a non-negative int or float estimating the remaining number of actions
                 needed to reach a goal state from the current state.
        The heuristic must be deterministic and must not modify state or goals.
        It must run quickly and avoid any form of search.
        \"\"\"

High-level guidance for the heuristic:
1. Interpret the goal:
   - identify, for each ball, its desired destination room from positive_goals.
2. From the current state, determine:
   - the current room of the robot,
   - for each ball, whether it is already at its goal room,
   - which balls are currently carried in the left or right gripper, and which grippers are free.
3. For balls that are not yet at their goal room, estimate:
   - whether the robot must move from its current room to the ball's room,
   - whether it must pick up the ball (respecting the two-gripper capacity),
   - whether it must move to the goal room,
   - whether it must drop the ball there.
4. Combine these estimates into a single heuristic value:
   - roughly count the remaining moves, picks, and drops,
   - take into account that the robot has two grippers and can sometimes carry two balls per trip.
"""

        elif dn == "blocksworld":
            domain_notes = """
Domain notes (Blocksworld):
Predicates:
- ('on', x, y) : block x is on y
- ('ontable', x) : block x is on the table
- ('clear', x) : no block on x
- ('holding', x) : robot arm holds x
- ('handempty',) : robot arm is empty
Typical actions: pickup, putdown, stack, unstack.

Heuristic design hints:
- Focus on blocks that are not yet in their goal position or have the wrong block on top.
- Penalise blocks that are "buried" under wrong blocks which must be moved out of the way.
- For each block:
  - If it is already on the correct support with the correct tower above it, cost 0.
  - If it is on the wrong support or has wrong blocks above, estimate unstack moves + stack moves needed.
- Use the structure of ('on', ...), ('ontable', ...), and ('clear', ...) to approximate tower corrections, not just count goal literals.
"""

        elif dn == "depots":
            domain_notes = """
You are a highly skilled professor in AI planning and a proficient Python programmer.
Your task is to design a domain-dependent heuristic for the classical planning domain "Depots".

The planner represents states and goals as follows:
- state: a frozenset of tuples like ('at', 'crate1', 'depot0'),
         ('in', 'crate2', 'truck0'),
         ('at-truck', 'truck0', 'distributor1'),
         ('clear', 'crate3'), etc.
- goals: (positive_goals, negative_goals), each a frozenset of tuples in the same format.

You must implement the following Python function:

    def h(state, goals):
        \"\"\"
        Domain-specific heuristic for the Depots domain.
        state: frozenset of ground predicates describing the current world.
        goals: (positive_goals, negative_goals), each a frozenset of ground predicates.
        Returns: a non-negative int or float estimating the remaining number of actions
                 needed to reach a goal state from the current state.
        The heuristic must be deterministic and must not modify state or goals.
        It must run quickly and avoid any form of search.
        \"\"\"

High-level guidance for the heuristic:
1. Interpret the goal: for each crate, identify its desired destination location in positive_goals.
2. From the current state, determine for each crate:
   - where it is (on the ground at some location, in a truck, on another crate, etc.),
   - whether it is already at its goal location.
3. For crates that are not yet at their goal, estimate:
   - how many load/unload operations are needed,
   - whether a truck must drive between locations, and count such moves,
   - any extra steps needed to clear blocking crates or free hoists.
4. Combine these estimates into a single heuristic value:
   - sum contributions over all crates,
   - optionally add small extra costs when trucks or hoists are far from useful positions.
"""

        elif dn == "logistics":
            domain_notes = """
Domain notes (Logistics):
Predicates:
- ('at', obj, loc) : package or vehicle at a location
- ('in', pkg, vehicle) : package loaded in a vehicle
Typical actions: load, unload, drive-truck, fly-airplane.

Heuristic design hints:
- Focus on packages that are not yet at their goal locations.
- For each such package, estimate:
  - 1 load + 1 unload if it is at a location served by the correct vehicle,
  - plus some number of drives/flights if it must travel via multiple locations/vehicles.
- Distinguish:
  - packages already at their goal location (cost 0),
  - packages in the correct vehicle but not yet unloaded,
  - packages at completely wrong locations.
- Count loads/unloads and movements of vehicles that actually bring packages closer to their goal; avoid counting moves that leave all packages at the same distance from their goals.
"""

        elif dn == "transport":
            domain_notes = """
Domain notes (Transport):
Predicates:
- ('at', obj, loc) : object or vehicle at a location
- ('in', pkg, veh) : package loaded in a vehicle
- ('road', loc1, loc2) : road between locations (if present)
Vehicles carry packages along roads; typical actions: load, unload, drive.

Heuristic design hints:
- Focus on packages that are not yet at their goal locations.
- For each such package, estimate:
  - 1 load + 1 unload if a vehicle at the same location can take it directly to its goal,
  - plus some number of drives along the road network if it must travel via intermediate locations.
- Distinguish:
  - packages already at their goal location (cost 0),
  - packages in the correct vehicle but not yet unloaded,
  - packages at locations with no direct road to the goal (may need multiple drives).
- Use ('road', ...), ('at', ...), and ('in', ...) to approximate the number of load/unload and drive actions remaining, rather than just counting goal predicates.
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

        user = (
            "You will receive the PDDL domain and the Python state representation.\n"
            "Write a domain-aware heuristic h(state, goals) using predicates/structure to estimate remaining cost.\n\n"
            "Python representation:\n"
            "- state is frozenset of ground atoms tuples like ('at-robby', 'rooma'), "
            "('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')\n"
            "- goals is (positive_goals, negative_goals), each a frozenset of tuples\n\n"
            f"PDDL Domain:\n{domain_pddl}\n\n{domain_notes}\n\n"
            "Return ONLY the Python function h(state, goals) as valid Python code, with no explanations or markdown.\n"
        )

        diversity = [
            "\n# Diversity hint: try batching/ceil trips with capacity 2.\n",
            "\n# Diversity hint: incorporate robot room vs source rooms.\n",
            "\n# Diversity hint: treat carried balls differently from at(ball, room).\n",
            "\n# Diversity hint: approximate pick/drop + move counts.\n",
            "\n# Diversity hint: avoid any goal-count-like set difference.\n",
        ][variant_id % 5]

        return system + "\n" + user + diversity

    def evaluate_candidate(self, candidate: Dict[str, Any], training_problems):
        domain_name = candidate["domain"]
        candidate_id = candidate["id"]

        candidate_file = self.llm_dir / "candidates" / f"{candidate_id}.py"
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
            print(f"  Testing {candidate_id} on {prob}...")
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

    def _run_planner_with_candidate(self, domain_name: str, problem_file: str, candidate_py_file: Path):
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
                    "90",
                ],
                capture_output=True,
                text=True,
                timeout=95,
            )

            output = result.stdout.strip()
            if output.startswith("SUCCESS"):
                parts = output.split()
                expansions = int(parts[1])
                t = float(parts[2])
                return True, expansions, t
            return False, 0, 0.0

        except Exception as e:
            print(f"    Error running planner: {e}")
            return False, 0, 0.0

    def select_best_candidate(self, domain_name: str, evaluation_results, model_name: Optional[str] = None):
        """
        Select the best candidate by:
          1) maximising coverage,
          2) minimising avg_expansions,
          3) then minimising avg_time.
        Attach model_name so the selection JSON knows which model produced it.
        """
        if not evaluation_results:
            return None

        sorted_results = sorted(
            evaluation_results,
            key=lambda r: (-r["coverage"], r["avg_expansions"], r["avg_time"]),
        )
        best = sorted_results[0]
        best_with_model = dict(best)
        best_with_model["model_name"] = model_name

        print(f"\n=== Best candidate for {domain_name} ({model_name}) ===")
        print(f"ID: {best_with_model['candidate_id']}")
        print(f"Coverage: {best_with_model['coverage']}")
        print(f"Avg Expansions: {best_with_model.get('avg_expansions', 'N/A')}")
        print(f"Avg Time: {best_with_model.get('avg_time', 'N/A')}")

        return best_with_model
