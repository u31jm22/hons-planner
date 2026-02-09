import logging
import sys
import argparse
import glob
import os
import gc
import re
import yaml
# import importlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mpl_colors
from typing import List, Type

# TODO Clean this up and not rely in specific imports
from pddl.benchmark import PlanningBenchmark
# from pddl.heuristic_planner import HeuristicPlanner
from pddl.intention import IntentionPlanner, HeuristicPlannerWrapper
from pddl.delete_relaxation_h import MaxHeuristic, FastForwardHeuristic
# from pddl.pddl_preprocessor import PyperPreprocessor
from pddl.pddl_preprocessor import RPGReachabilityPreprocessor


def load_class(name: str) -> Type:
    """Loads a class by its full name (e.g. bdiplan.agent.BasicBDIAgent), and returns a reference to it. This is meant to work like Java's reflection API.

    Args:
        name (str): Class Name

    Returns:
        Type: The loaded class
    """
    # components = name.split('.')
    # mod = importlib.import_module('.'.join(components[:-1]))
    # clazz = getattr(mod, components[-1])
    # return clazz
    components = name.split('.')
    mod = __import__(".".join(components[:-1]))
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def load_yaml(yaml_path: str):

    with open(yaml_path, 'r') as yaml_file:  # TODO Refactor this into another method?
        yaml_config = yaml.load(yaml_file, Loader=yaml.FullLoader)
        planner_pars = None
        heuristic_pars = None
        planner_class = None
        heuristic_class = None
        if yaml_config:
            if 'planner_class' in yaml_config:
                planner_class = load_class(yaml_config['planner_class'])
            else:
                raise Exception("Missing planner_class")
            if 'planner_pars' in yaml_config:
                planner_pars = yaml_config['planner_pars']
            else:
                raise Exception('Missing planner_pars')
            if 'heuristic_class' in yaml_config:
                heuristic_class = load_class(yaml_config['heuristic_class'])
            else:
                raise Exception("Missing heuristic_class")
            if 'heuristic_pars' in yaml_config:
                heuristic_pars = yaml_config['heuristic_pars']
            else:
                raise Exception('Missing planner_pars')
        else:
            raise Exception('Invalid Configuration file')
        return planner_class, heuristic_class, planner_pars, heuristic_pars


# flake8: noqa: C901
def main(argv: List):
    logging.basicConfig()
    logger = logging.getLogger()
    logger.warning("Running \'%s\'" % argv)

    parser = argparse.ArgumentParser(
                    prog='benchmark',
                    description='Runs benchmark on the Simplafy planner',
                    epilog='Text at the bottom of help')

    # TODO Generalise this to other configurations when I have time
    # parser.add_argument('dataset_path', help='Path to domain and problem files')
    parser.add_argument('-d', '--dataset', default='.', help='Path to domain and problem files')
    parser.add_argument('-o', '--output', default='./tmp', help='Path to output graphs')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-p', '--preprocess', action='store_true', help='Whether to preprocess the PDDL domains to remove irrelevant facts and operators')
    parser.add_argument('-f', '--format', action='store_true', default="svg")
    parser.add_argument('-t', '--tikz', action='store_true', default=False)
    parser.add_argument('configurations', nargs="*")
    args = parser.parse_args(argv[1:])

    if args.tikz: # pragma: no cover
        mpl.use("pgf")

    if args.verbose:
        print("Setting verbose output")
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.CRITICAL)

    benchmark = PlanningBenchmark()

    # if not os.path.isdir(args.dataset_path):
    if not os.path.isdir(args.dataset):
        raise FileNotFoundError("Dataset path %s not found :(" % args.dataset)
    else:
        dataset_path = args.dataset

    domain_name = dataset_path.split(sep=r'/')[-1]
    domain_file = dataset_path+'/'+domain_name+".pddl"
    ground_domain = False
    if not os.path.exists(domain_file):
        domain_file = dataset_path+'/domain.pddl'
        if not os.path.exists(dataset_path+"/domain.pddl"):
            ## Check for grounded domains
            if glob.glob(os.path.join(dataset_path, 'domain??.pddl')):
                logger.info("Domain %s is ground" % domain_name)
                ground_domain = True
                domain_file = None
            else:
                raise FileNotFoundError("No domain file found in dataset path %s" % dataset_path)

    # TODO Generalise the code below
    planner_classes = [
            HeuristicPlannerWrapper,
            IntentionPlanner
            ]
    heuristic_classes = [
        MaxHeuristic,
        MaxHeuristic
    ]
    if args.configurations:
        # print("Loading configurations: ", end="")
        logger.info("Loading configurations: ")
        planner_classes = []
        heuristic_classes = []
        for configuration in args.configurations:
            # print(f"{configuration} ", end="")
            logger.info(f"{configuration} ")
            if not os.path.exists(configuration): 
                raise FileNotFoundError("No configuration file at: %s" % configuration)
            planner_class, heuristic_class, planner_pars, heuristic_pars = load_yaml(configuration)
            planner_classes.append(planner_class)
            heuristic_classes.append(heuristic_class)
        # print(".")
        logger.info("Done")

    problems = dict()
    times = dict()
    nodes = dict()
    nodes_first = dict()
    h_calls = dict()
    h_time = dict()
    times_last = dict()
    queue_time = dict()
    approach_labels = []
    for PlannerClass, HeuristicClass in zip(planner_classes, heuristic_classes):
        benchmark.reset_stats()
        approach_name = f"{PlannerClass.__name__}({HeuristicClass.__name__})"
        approach_labels.append(approach_name)
        for filename in sorted(glob.glob(os.path.join(dataset_path, '*.pddl'))):
            # logger.info('Solving %s for domain %s' % (filename, domain_file))
            if ground_domain:
                # Ski specific domain file
                if re.search(r'^domain\d{2}\.pddl$', os.path.basename(filename)):
                    continue
                else:
                    match = re.match(r'^task(\d{2})\.pddl$', os.path.basename(filename))
                    if match:
                        number = match.group(1)
                        domain_file = dataset_path+'/domain%s.pddl' % number
                    else:
                        raise FileNotFoundError("Could not find corresponding domain for %" % filename)
            if domain_file in filename:
                # Skip the domain file
                continue

            # print('Solving %s for domain %s using %s' % (filename, domain_file, approach_name))
            logger.info('Solving %s for domain %s using %s' % (filename, domain_file, approach_name))

            # TODO Nasty hack to deal with regular planner

            stats = benchmark.get_instance(domain_file, filename)

            # heuristic = MaxHeuristic(stats=stats)
            # heuristic = FastForwardHeuristic(stats=stats)
            heuristic = HeuristicClass(stats=stats)
            preprocessor = None
            if args.preprocess:
                preprocessor = RPGReachabilityPreprocessor()
                # preprocessor = PyperPreprocessor()
            planner = PlannerClass(
                heuristic=heuristic,
                collect_stats=True,
                verbose=args.verbose)
            plan, time = planner.solve_file(domain_file, filename, preprocessor)

            heuristic = None
            planner = None
            gc.collect()  # Avoid using the GC during planning
        l_problems, l_times = benchmark.get_stats(domain_file, xaxis='problem', stat='time', approach=approach_name)
        l_problems, l_times_last = benchmark.get_stats(domain_file, xaxis='problem', stat='time_last', approach=approach_name)
        l_problems, l_nodes = benchmark.get_stats(domain_file, xaxis='problem', stat='nodes', approach=approach_name)
        l_problems, l_nodes_first = benchmark.get_stats(domain_file, xaxis='problem', stat='nodes_first', approach=approach_name)
        l_problems, l_hcalls = benchmark.get_stats(domain_file, xaxis='problem', stat='h_calls', approach=approach_name)
        l_problems, l_htime = benchmark.get_stats(domain_file, xaxis='problem', stat='h_time', approach=approach_name)
        l_problems, l_qtime = benchmark.get_stats(domain_file, xaxis='problem', stat='queue_time', approach=approach_name)

        problems[approach_name] = l_problems
        times[approach_name] = l_times
        nodes[approach_name] = l_nodes
        nodes_first[approach_name] = l_nodes_first
        h_calls[approach_name] = l_hcalls
        h_time[approach_name] = l_htime
        queue_time[approach_name] = l_qtime
        times_last[approach_name] = l_times_last

    # TODO Refactor this like I have in the BDI planner
    legend = 'upper left'

    # Create distinct colours for each line in graph...
    color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    colors = {
        label: color_cycle[i % len(color_cycle)]
        for i, label in enumerate(approach_labels)
    }

    table_x = ""
    for problem in problems[approach_labels[0]]:
        table_x += ', %s' % problem

    table_y = ""
    fig, ax = plt.subplots()
    ax.set_xlabel('Problem')
    ax.set_ylabel('Time (s)')
    ax.set_title('Cummulative Time')
    for approach_name in approach_labels:
        ax.plot(problems[approach_name], times[approach_name], label=approach_name, color=colors[approach_name])
        ax.plot(problems[approach_name], h_time[approach_name], label=approach_name+"H", linestyle='dashed', color=colors[approach_name])
        ax.plot(problems[approach_name], queue_time[approach_name], label=approach_name+"Q", linestyle='dotted', color=colors[approach_name])
        table_y += "\n"+approach_name
        for v in times[approach_name]:
            table_y += ', %s' % v
    ax.legend(loc=legend)
    fig.text(0.0, 0.0, f"%s" % args.configurations)
    logger.info("Saving to "+'%s/%s-time.%s' % (args.output, domain_name, args.format))
    fig.savefig('%s/%s-time.%s' % (args.output, domain_name, args.format))
    if args.tikz: # pragma: no cover
        logger.info("Saving to "+'%s/%s-time.%s' % (args.output, domain_name, "pgf"))
        fig.savefig('%s/%s-time.%s' % (args.output, domain_name, "pgf"))
    plt.close()
    logger.info("Saving to "+'%s/%s-time.%s' % (args.output, domain_name, 'csv'))
    with open('%s/%s-time.%s' % (args.output, domain_name, 'csv'), 'w') as f:
        f.write(table_x)
        f.write(table_y)
        f.close()
    
    table_y = ""
    fig, ax = plt.subplots()
    ax.set_xlabel('Problem')
    ax.set_ylabel('Time (s)')
    ax.set_title('Time Last')
    for approach_name in approach_labels:
        ax.plot(problems[approach_name], times_last[approach_name], label=approach_name, color=colors[approach_name])
        ax.plot(problems[approach_name], times[approach_name], label=approach_name+"T", linestyle='dashed', color=colors[approach_name])
        table_y += "\n"+approach_name
        for v in times_last[approach_name]:
            table_y += ', %s' % v
    ax.legend(loc=legend)
    fig.text(0.0, 0.0, f"%s" % args.configurations)
    fig.savefig('%s/%s-time-last.%s' % (args.output, domain_name, args.format))
    if args.tikz: # pragma: no cover
        fig.savefig('%s/%s-time-last.%s' % (args.output, domain_name, "pgf"))
        logger.info("Saving to "+'%s/%s-time-last.%s' % (args.output, domain_name, 'pgf'))
    plt.close()
    logger.info("Saving to "+'%s/%s-time-last.%s' % (args.output, domain_name, 'csv'))
    with open('%s/%s-time-last.%s' % (args.output, domain_name, 'csv'), 'w') as f:
        f.write(table_x)
        f.write(table_y)
        f.close()

    table_y = ""
    fig, ax = plt.subplots()
    ax.set_xlabel('Problem')
    ax.set_ylabel('Nodes')
    ax.set_title('Nodes to all goals')
    for approach_name in approach_labels:
        ax.plot(problems[approach_name], nodes[approach_name], label=approach_name, color=colors[approach_name])
        table_y += "\n"+approach_name
        for v in nodes[approach_name]:
            table_y += ', %s' % v
    a1 = str(approach_labels[0])
    a2 = str(approach_labels[1])
    extra_nodes = []
    for n1, n2 in zip(nodes[a2], nodes_first[a2]):
        extra_nodes.append(n1 - n2)
    ax.plot(problems[approach_name], extra_nodes, linestyle='dashed', label='Extra Effort', color='red')
    table_y += "\nExtra Effort"
    for v in extra_nodes:
        table_y += ', %s' % v
    ax.legend(loc=legend)
    fig.text(0.0, 0.0, f"%s" % args.configurations)
    logger.info("Saving to "+'%s/%s-nodes.%s' % (args.output, domain_name, args.format))
    fig.savefig('%s/%s-nodes.%s' % (args.output, domain_name, args.format))
    if args.tikz: # pragma: no cover
        logger.info("Saving to "+'%s/%s-nodes.%s' % (args.output, domain_name, 'pgf'))
        fig.savefig('%s/%s-nodes.%s' % (args.output, domain_name, "pgf"))
    plt.close()
    logger.info("Saving to "+'%s/%s-nodes.%s' % (args.output, domain_name, 'csv'))
    with open('%s/%s-nodes.%s' % (args.output, domain_name, 'csv'), 'w') as f:
        f.write(table_x)
        f.write(table_y)
        f.close()

    table_y = ""
    fig, ax = plt.subplots()
    ax.set_xlabel('Problem')
    ax.set_ylabel('Nodes First')
    ax.set_title('Nodes to first goal')
    for approach_name in approach_labels:
        ax.plot(problems[approach_name], nodes_first[approach_name], label=approach_name, color=colors[approach_name])
        table_y += "\n"+approach_name
        for v in nodes_first[approach_name]:
            table_y += ', %s' % v
    ax.legend(loc=legend)
    fig.text(0.0, 0.0, f"%s" % args.configurations)
    logger.info("Saving to "+'%s/%s-nodes-first.%s' % (args.output, domain_name, args.format))
    fig.savefig('%s/%s-nodes-first.%s' % (args.output, domain_name, args.format))
    if args.tikz: # pragma: no cover
        logger.info("Saving to "+'%s/%s-nodes-first.%s' % (args.output, domain_name, 'pgf'))
        fig.savefig('%s/%s-nodes-first.%s' % (args.output, domain_name, "pgf"))
    plt.close()
    logger.info("Saving to "+'%s/%s-nodes-first.%s' % (args.output, domain_name, 'csv'))
    with open('%s/%s-nodes-first.%s' % (args.output, domain_name, 'csv'), 'w') as f:
        f.write(table_x)
        f.write(table_y)
        f.close()

    table_y = ""
    fig, ax = plt.subplots()
    ax.set_xlabel('Problem')
    ax.set_ylabel('H Calls')
    ax.set_title('Cumulative Heuristic Calls')
    for approach_name in approach_labels:
        ax.plot(problems[approach_name], h_calls[approach_name], label=approach_name, color=colors[approach_name])
        table_y += "\n"+approach_name
        for v in h_calls[approach_name]:
            table_y += ', %s' % v
    ax.legend(loc=legend)
    fig.text(0.0, 0.0, f"%s" % args.configurations)
    logger.info("Saving to "+'%s/%s-h_calls.%s' % (args.output, domain_name, args.format))
    fig.savefig('%s/%s-h_calls.%s' % (args.output, domain_name, args.format))
    if args.tikz: # pragma: no cover
        logger.info("Saving to "+'%s/%s-h_calls.%s' % (args.output, domain_name, 'pgf'))
        fig.savefig('%s/%s-h_calls.%s' % (args.output, domain_name, "pgf"))
    plt.close()
    logger.info("Saving to "+'%s/%s-h_calls.%s' % (args.output, domain_name, 'csv'))
    with open('%s/%s-h_calls.%s' % (args.output, domain_name, 'csv'), 'w') as f:
        f.write(table_x)
        f.write(table_y)
        f.close()


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)
