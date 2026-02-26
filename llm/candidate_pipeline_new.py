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
    lowered = code.lower()
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
    try:
        compile(code, "andidate>", "exec")
        return True, ""
    except Exception as e:
        return False, str(e)


class CandidatePipeline:

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
            if code is None:
                print(f"  Skipping candidate {i + 1} - could not generate valid code.")
                continue
            candidates.append({
                "id": f"{domain_name}_candidate_{i + 1}",
                "code": code,
                "prompt_variant": i,
                "domain": domain_name,
            })
        out_json = self.llm_dir / "candidates" / f"{domain_name}_candidates.json"
        out_json.write_text(json.dumps(candidates, indent=2))
        print(f"Saved {len(candidates)} candidates to {out_json}")
        return candidates

    def _generate_heuristic_code(self, prompt: str) -> str:
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
        print("  All retries exhausted - no valid non-trivial candidate generated.")
        return None

    def _build_prompt(self, domain_name: str, domain_pddl: str, variant_id: int) -> str:
        dn = domain_name.lower()

        if dn == "gripper":
            domain_notes = """Domain: Gripper (robot with two grippers moves balls between rooms).

State atoms: ('at-robby', room), ('at', ball, room), ('carry', ball, gripper), ('free', gripper).
Goals: positive_goals contains ('at', ball, room) targets.

Heuristic idea:
- For each goal ball not yet at its target room:
  - If carried in wrong room: +1 move to goal, +1 drop.
  - If on floor in wrong room: +1 move to ball (if robot not there), +1 pick, +1 move to goal, +1 drop.
- If 2+ grippers free, small discount for batching.
- Sum over all goal balls.

Example correct heuristic (do NOT copy exactly, write your own variation):

def h(state, goals):
    positive_goals, negative_goals = goals
    robot_room = next((a[1] for a in state if a[0] == 'at-robby'), None)
    ball_room = {a[1]: a[2] for a in state if a[0] == 'at'}
    carried = {a[1]: a[2] for a in state if a[0] == 'carry'}
    free_grippers = sum(1 for a in state if a[0] == 'free')
    goal_room = {g[1]: g[2] for g in positive_goals if g[0] == 'at'}
    cost = 0
    for ball, target in goal_room.items():
        cur = robot_room if ball in carried else ball_room.get(ball)
        if cur == target:
            if ball in carried:
                cost += 1
            continue
        if ball in carried:
            cost += 1 + 1
        else:
            cost += (1 if robot_room != cur else 0) + 1 + 1 + 1
    if free_grippers >= 2 and cost > 0:
        cost -= 1
    return float(max(0, cost))
"""

        elif dn == "blocksworld":
            domain_notes = """Domain: Blocksworld (robot arm stacks and unstacks blocks).

State atoms: ('on', x, y), ('ontable', x), ('clear', x), ('holding', x), ('handempty',).
Goals: positive_goals contains ('on', x, y) and ('ontable', x) targets.

Heuristic idea:
- For each unsatisfied ('on', x, y) goal:
  - Cost at least 2 (unstack x + restack onto y).
  - Add cost for blocks buried above x (each needs unstack + putdown).
  - Add cost if y is not clear (needs clearing first).
- Sum over all unsatisfied goal literals.

Example correct heuristic (do NOT copy exactly, write your own variation):

def h(state, goals):
    positive_goals, negative_goals = goals
    on = {a[1]: a[2] for a in state if a[0] == 'on'}
    clear = {a[1] for a in state if a[0] == 'clear'}
    ontable = {a[1] for a in state if a[0] == 'ontable'}
    cost = 0
    for g in positive_goals:
        if g[0] == 'on':
            x, y = g[1], g[2]
            if on.get(x) == y:
                continue
            cost += 2
            if y not in clear and y not in ontable:
                cost += 1
            cost += sum(2 for b, s in on.items() if s == x)
        elif g[0] == 'ontable':
            x = g[1]
            if x in ontable:
                continue
            cost += 2
    return float(cost)
"""

        elif dn == "depots":
            domain_notes = """Domain: Depots (trucks, hoists, crates, depots and distributors).

State atoms:
- ('at', crate, loc): crate on ground at location.
- ('in', crate, truck): crate loaded in truck.
- ('at-truck', truck, loc): truck at location.
- ('on', crate, surface): crate stacked on surface.
- ('clear', x): nothing on top of x.
- ('lifting', hoist, crate): hoist lifting crate.
- ('available', hoist): hoist is free.

Goals: positive_goals contains ('at', crate, location) targets.

Heuristic idea:
- For each goal crate not yet at target:
  - Case A: already at goal on ground -> 0.
  - Case B: in truck -> unload(1) + drive if needed(1) + drop(1).
  - Case C: on ground wrong place -> load(1) + drive(1) + drop(1).
  - Case D: stacked -> unstack(1) + as Case C.
  - Case E: unknown -> cost 4.
- Add +1 if no hoist available at current location.
- Sum over all goal crates.

Example correct heuristic (do NOT copy exactly, write your own variation):

def h(state, goals):
    positive_goals, negative_goals = goals
    crate_at = {}
    crate_in = {}
    crate_on = {}
    truck_at = {}
    available_hoists = set()
    hoists_at = {}
    for atom in state:
        if atom[0] == 'at':
            crate_at[atom[1]] = atom[2]
        elif atom[0] == 'in':
            crate_in[atom[1]] = atom[2]
        elif atom[0] == 'on':
            crate_on[atom[1]] = atom[2]
        elif atom[0] == 'at-truck':
            truck_at[atom[1]] = atom[2]
        elif atom[0] == 'available':
            available_hoists.add(atom[1])
        elif atom[0] == 'at-hoist':
            hoists_at[atom[1]] = atom[2]
    avail_hoist_locs = {hoists_at[h] for h in available_hoists if h in hoists_at}
    cost = 0
    for g in positive_goals:
        if g[0] != 'at':
            continue
        crate, target = g[1], g[2]
        if crate_at.get(crate) == target:
            continue
        if crate in crate_in:
            truck = crate_in[crate]
            tloc = truck_at.get(truck)
            cost += 1
            if tloc != target:
                cost += 1
            cost += 1
        elif crate in crate_on:
            cur = crate_at.get(crate, None)
            cost += 1
            cost += 1
            if cur != target:
                cost += 1
            cost += 1
        elif crate in crate_at:
            cur = crate_at[crate]
            cost += 1
            if cur != target:
                cost += 1
            cost += 1
            if cur not in avail_hoist_locs:
                cost += 1
        else:
            cost += 4
    return float(cost)
"""

        elif dn == "logistics":
            domain_notes = """Domain: Logistics (trucks and planes move packages between locations).

State atoms: ('at', obj, loc), ('in', pkg, vehicle).
Goals: positive_goals contains ('at', pkg, location) targets.

Heuristic idea:
- For each goal package not yet at target:
  - If already at goal -> 0.
  - If in vehicle: unload(1) + drive/fly if needed(1) + drop(1).
  - If on ground wrong place: load(1) + drive/fly(1) + drop(1).
  - If no vehicle at package location: +1 to bring one.
- Sum over all goal packages.

Example correct heuristic (do NOT copy exactly, write your own variation):

def h(state, goals):
    positive_goals, negative_goals = goals

def h(state, goals):
    positive_goals, negative_goals = goals
    obj_at = {a[1]: a[2] for a in state if a[0] == 'at'}
    pkg_in = {a[1]: a[2] for a in state if a[0] == 'in'}
    vehicles_at = {}
    for obj, loc in obj_at.items():
        if obj.startswith('truck') or obj.startswith('airplane') or obj.startswith('plane'):
            vehicles_at.setdefault(loc, []).append(obj)
    cost = 0
    for g in positive_goals:
        if g[0] != 'at':
            continue
        pkg, target = g[1], g[2]
        if obj_at.get(pkg) == target:
            continue
        if pkg in pkg_in:
            vehicle = pkg_in[pkg]
            vloc = obj_at.get(vehicle)
            cost += 1
            if vloc != target:
                cost += 1
            cost += 1
        else:
            cur = obj_at.get(pkg)
            if cur is None:
                cost += 4
                continue
            cost += 1
            if cur != target:
                cost += 1
            cost += 1
            if not vehicles_at.get(cur):
                cost += 1
    return float(cost)
"""

        elif dn == "transport":
            domain_notes = """Domain: Transport (vehicles move packages along roads).

State atoms: ('at', obj, loc), ('in', pkg, veh), ('road', loc1, loc2).
Goals: positive_goals contains ('at', pkg, location) targets.

Heuristic idea:
- For each goal package not yet at target:
  - If in vehicle: unload(1) + drives(1+) + drop(1).
  - If on ground: load(1) + drives(1+) + drop(1).
  - Use ('road', ...) to estimate number of drives needed.
- Sum over all goal packages.

Example correct heuristic (do NOT copy exactly, write your own variation):

def h(state, goals):
    positive_goals, negative_goals = goals
    obj_at = {a[1]: a[2] for a in state if a[0] == 'at'}
    pkg_in = {a[1]: a[2] for a in state if a[0] == 'in'}
    roads = {(a[1], a[2]) for a in state if a[0] == 'road'}
    cost = 0
    for g in positive_goals:
        if g[0] != 'at':
            continue
        pkg, target = g[1], g[2]
        if obj_at.get(pkg) == target:
            continue
        if pkg in pkg_in:
            vehicle = pkg_in[pkg]
            vloc = obj_at.get(vehicle)
            cost += 1
            if vloc != target:
                cost += 1 if (vloc, target) in roads else 2
            cost += 1
        else:
            cur = obj_at.get(pkg)
            if cur is None:
                cost += 4
                continue
            cost += 1
            if cur != target:
                cost += 1 if (cur, target) in roads else 2
            cost += 1
    return float(cost)
"""

        else:
            domain_notes = ""

        system = (
            "You are an expert in classical planning and PDDL acting as a Python code generator for heuristic functions.\n"
            "Write a single Python function h(state, goals) that computes a domain-aware heuristic.\n\n"
            "Constraints:\n"
            "- Output only valid Python code for h(state, goals).\n"
            "- No imports, no I/O, no randomness, no external modules.\n"
            "- Must always return a non-negative int or float.\n"
            "- Linear time: no search, no simulating successors.\n"
            "- NOT trivial goal-count: no len(positive_goals - state), no sum(1 for g in positive_goals if g not in state).\n"
            "- Must contain real domain-aware logic: loops, conditionals, arithmetic.\n"
        )

        user = (
            "Write a domain-aware heuristic h(state, goals) for the domain below.\n\n"
            "State: frozenset of ground atom tuples e.g. ('at-robby', 'rooma'), ('at', 'ball1', 'rooma').\n"
            "Goals: (positive_goals, negative_goals), each a frozenset of tuples.\n\n"
            f"PDDL Domain:\n{domain_pddl}\n\n{domain_notes}\n\n"
            "Return ONLY the Python function h(state, goals), no markdown, no explanations.\n"
        )

        diversity = [
            "\n# Diversity hint: try batching trips where possible.\n",
            "\n# Diversity hint: incorporate vehicle or robot current location explicitly.\n",
            "\n# Diversity hint: treat objects in vehicles differently from those on the ground.\n",
            "\n# Diversity hint: approximate pick/load/drop counts carefully.\n",
            "\n# Diversity hint: avoid any goal-count-like set difference.\n",
        ][variant_id % 5]

        return system + "\n" + user + diversity

    def evaluate_candidate(self, candidate, training_problems):
        domain_name = candidate["domain"]
        candidate_id = candidate["id"]
        candidate_file = self.llm_dir / "candidates" / f"{candidate_id}.py"
        candidate_file.write_text(candidate["code"])
        results = {"candidate_id": candidate_id, "coverage": 0, "total_expansions": 0,
                   "total_time": 0.0, "solved": [], "failed": []}
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

    def _run_planner_with_candidate(self, domain_name, problem_file, candidate_py_file):
        domain_path = self.domains_dir / domain_name / "domain.pddl"
        problem_path = self.domains_dir / domain_name / problem_file
        eval_script = self.llm_dir / "evaluate_candidate.py"
        try:
            result = subprocess.run(
                [sys.executable, str(eval_script),
                 "--domain", str(domain_path),
                 "--problem", str(problem_path),
                 "--candidate", str(candidate_py_file),
                 "--timeout", "90"],
                capture_output=True, text=True, timeout=95,
            )
            output = result.stdout.strip()
            if output.startswith("SUCCESS"):
                parts = output.split()
                return True, int(parts[1]), float(parts[2])
            return False, 0, 0.0
        except Exception as e:
            print(f"    Error running planner: {e}")
            return False, 0.0, 0.0

    def select_best_candidate(self, domain_name, evaluation_results, model_name=None):
        if not evaluation_results:
            return None
        sorted_results = sorted(
            evaluation_results,
            key=lambda r: (-r["coverage"], r["avg_expansions"], r["avg_time"]),
        )
        best = dict(sorted_results[0])
        best["model_name"] = model_name
        print(f"\n=== Best candidate for {domain_name} ({model_name}) ===")
        print(f"ID: {best['candidate_id']}")
        print(f"Coverage: {best['coverage']}")
        print(f"Avg Expansions: {best.get('avg_expansions', 'N/A')}")
        print(f"Avg Time: {best.get('avg_time', 'N/A')}")
        return best
