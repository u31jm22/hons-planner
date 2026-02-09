import sys
import logging
import argparse
from typing import List
from pddl.pddl_planner import PDDLPlanner
from pddl.heuristic_planner import HeuristicPlanner, HeuristicRunner
from pddl.bfs_planner import BFSPlanner
from pddl.intention import IntentionPlanner
from pddl.heuristic import Heuristic
from pddl.delete_relaxation_h import AdditiveHeuristic, MaxHeuristic, DeleteRelaxationHeuristic, FastForwardHeuristic
from pddl.landmarkh import LMCutHeuristic, NaiveLandmarkHeuristic
from pddl.pddl_preprocessor import PyperPreprocessor


# flake8: noqa: C901
def main(argv: List):
    print("Running \'%s\'" % argv)

    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
                    prog='simplafy',
                    description='Runs the Simplafy planner',
                    epilog='Text at the bottom of help')
    parser.add_argument('pddl_domain')
    parser.add_argument('pddl_problem')
    # TODO Eventually redo this to dynamically choose the algorithm and heuristic
    parser.add_argument('-s', '--search',
                        choices=['astar', 'gbfs', 'ucs', 'lastar', 'iastar', 'honly'],
                        default='astar',
                        help='The search algorithm')
    parser.add_argument('-he', '--heuristic', 
                        choices=['hadd', 'hmax', 'ff', 'dr', 'lm', 'lmcut'], 
                        default='hmax', 
                        help='The heuristic, where applicable')
    parser.add_argument('-p', '--preprocess', action='store_true', help='Whether to preprocess the PDDL domains to remove irrelevant facts and operators')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args(argv[1:])

    heuristic: Heuristic = None
    planner: PDDLPlanner = None
    if args.heuristic == 'hadd':
        heuristic = AdditiveHeuristic()
    elif args.heuristic == 'hmax':
        heuristic = MaxHeuristic()
    elif args.heuristic == 'ff':
        heuristic = FastForwardHeuristic()
    elif args.heuristic == 'dr':
        heuristic = DeleteRelaxationHeuristic()
    elif args.heuristic == 'lm':
        heuristic = NaiveLandmarkHeuristic(verbose=args.verbose)
    elif args.heuristic == 'lmcut':
        heuristic = LMCutHeuristic(verbose=args.verbose)

    if args.search == 'astar':
        planner = HeuristicPlanner(heuristic=heuristic, verbose=args.verbose)
    elif args.search == 'gbfs':
        planner = None  # TODO Implement this
    elif args.search == 'ucs':
        planner = BFSPlanner(verbose=args.verbose)
    elif args.search == 'iastar':
        planner = IntentionPlanner(heuristic=heuristic, verbose=args.verbose)
    elif args.search == 'lastar':
        planner = IntentionPlanner(heuristic=heuristic, verbose=args.verbose)
    elif args.search == 'honly':
        planner = HeuristicRunner(heuristic=heuristic, verbose=args.verbose)
    
    preprocessor = None
    if args.preprocess:
        # preprocessor = RPGReachabilityPreprocessor()
        preprocessor = PyperPreprocessor()

    plan, time = planner.solve_file(args.pddl_domain, args.pddl_problem, preprocessor)

    print(plan)


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)