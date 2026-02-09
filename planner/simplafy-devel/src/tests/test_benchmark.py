#!/usr/bin/env python
# Four spaces as indentation [no tabs]
import os
import unittest
import pddl.run_benchmark
import generators.prodcell.prodcell as prodcell

from pddl.pddl_planner import PDDLPlanner
from pddl.bfs_planner import BFSPlanner
from pddl.heuristic_planner import HeuristicPlanner
from pddl.delete_relaxation_h import MaxHeuristic
from pddl.benchmark import PlanningBenchmark, InstanceStats, Stats
from tests.test_pddl_constants import TMP_FOLDER

import matplotlib.pyplot as plt
import heap_queue.priority_queue as hqueue


class TestBenchmark(unittest.TestCase):
    blocks = 'examples/blocksworld/blocksworld.pddl'
    blocks_pb = 'examples/blocksworld/pb%d.pddl'

    openstacks = 'examples/openstacks'

    @classmethod
    def setUpClass(cls) -> None:
        benchmark = PlanningBenchmark(output_folder='../tmp')
        assert benchmark is not None
        if not os.path.exists(TMP_FOLDER):  # Check we have the output folder created
            os.mkdir(TMP_FOLDER)
        if not os.path.exists(TMP_FOLDER+"/prodcell"):
            os.mkdir(TMP_FOLDER+"/prodcell")
        else:
            for file in os.listdir(TMP_FOLDER+'prodcell/'):
                os.remove(TMP_FOLDER+'prodcell/'+file)
        args = "prodcell.py -p 4 -fb 4 -tb 6 -b 2 -pb 1 -g 2 -f intention "+TMP_FOLDER+"/prodcell"
        prodcell.main(args.split())

    def test_singleton(self):
        instance1 = PlanningBenchmark(output_folder='../tmp')
        instance2 = PlanningBenchmark(output_folder='../tmp')
        self.assertEqual(instance1, instance2)

        stats1: InstanceStats = instance1.get_instance('blocks.pddl', 'pb1.pddl')
        stats2: InstanceStats = instance1.get_instance('blocks.pddl', 'pb1.pddl')
        self.assertEqual(stats1, stats2)

        stats3 = instance1.get_instance('blocks.pddl', 'pb3.pddl')
        self.assertNotEqual(stats1, stats3)

        with self.assertRaises(AttributeError):
            stats1.fail

        stats1[Stats.nodes] = 1
        self.assertEqual(1, stats1.nodes)
        self.assertIn(Stats.nodes, stats1)
        for stat in stats1:
            print(stat)
        self.assertIn("Domain, Problem, nodes, nodes_first, h_calls, action_space, time, queue_time, h_time", str(stats1))
        self.assertIn("blocks.pddl, pb1.pddl,1.00,0.00,0.00,0.00,0.00,0.00,0.00", repr(stats1))

    def test_stats(self):
        benchmark = PlanningBenchmark(output_folder='../tmp')
        for i in range(100):
            stats = benchmark.get_instance('blocks.pddl', 'pb%d.pddl' % i)
            stats.nodes = i * 1000
            stats.action_space = (i**2) * 10000
            stats.h_calls = stats.nodes * stats.action_space/2
            stats.time = stats.h_calls*3

        # benchmark.plot_stat('blocks.pddl')
        x, y = benchmark.get_stats('blocks.pddl')
        benchmark.reset_stats()

        planner: PDDLPlanner = None

        for i in range(1, 7):
            planner = HeuristicPlanner(heuristic=MaxHeuristic(stats=benchmark.get_instance(domain_name=TestBenchmark.blocks, problem_name=TestBenchmark.blocks_pb % i)), PriorityQueue=hqueue.ThreadSafePriorityQueue)
            planner.collect_benchmark = True
            print("Benchmarking Blocks world pb%i.pddl" % i)
            planner.solve_file(TestBenchmark.blocks, TestBenchmark.blocks_pb % i)

        hActions, hTime = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='time', approach='Heuristic')
        print('Actions x Time: %s' % [p for p in zip(hActions, hTime)])
        self.assertEqual(6, len(hActions))
        self.assertEqual([12, 24, 24, 40, 60, 84], hActions)
        hProblem, hTime = benchmark.get_stats(TestBenchmark.blocks, xaxis='problem', stat='time', approach='Heuristic')
        print('Problem x Time: %s' % [p for p in zip(hProblem, hTime)])
        hActions, hNodes = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat=Stats.nodes, approach='Heuristic')
        # self.assertEqual([3, 14, 12, 41, 80, 192], hNodes)
        # self.assertEqual([2, 4, 1, 13, 1, 1], hNodes) # TODO There's something wrong here
        # self.assertEqual([4, 16, 13, 75, 397, 2850], hNodes)  # These are the nodes I expect from using Python's thread safe (but not consistent) PriorityQueue
        self.assertEqual([4, 16, 13, 75, 401, 3232], hNodes)  # These are the nodes I expect from using a consistent PriorityQueue (my Implementation)
        print('Actions x Nodes: %s' % [p for p in zip(hActions, hNodes)])
        hActions, hCalls = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='h_calls', approach='Heuristic')
        print('Actions x Calls: %s' % [p for p in zip(hActions, hCalls)])

        # benchmark.plot_stat(TestBenchmark.blocks,xaxis='action',stat='time',approach='Heuristic')
        # benchmark.plot_stat(TestBenchmark.blocks, xaxis='problem', stat='time', approach='Heuristic')

        benchmark.reset_stats()

        planner = BFSPlanner()
        planner.collect_benchmark = True

        for i in range(1, 7):
            planner.solve_file(TestBenchmark.blocks, TestBenchmark.blocks_pb % i)

        # benchmark.plot_stat(TestBenchmark.blocks, xaxis='action', stat='time', approach='BFS')
        # benchmark.plot_stat(TestBenchmark.blocks, xaxis='problem', stat='time', approach='BFS')

        hActions2, hTime2 = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='time', approach='BFS')
        print('Actions x Time (BFS): %s' % [p for p in zip(hActions2, hTime2)])
        hProblem2, hTime2 = benchmark.get_stats(TestBenchmark.blocks, xaxis='problem', stat='time', approach='BFS')
        print('Problem x Time (BFS): %s' % [p for p in zip(hProblem2, hTime2)])
        hActions2, hNodes2 = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='nodes', approach='BFS')
        print('Actions x Nodes (BFS): %s' % [p for p in zip(hActions2, hNodes2)])
        hActions2, hCalls2 = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='h_calls', approach='BFS')
        print('Actions x Calls (BFS): %s' % [p for p in zip(hActions2, hCalls2)])

    def test_tables(self):
        benchmark = PlanningBenchmark(output_folder='../tmp')
        planner: PDDLPlanner = None

        for i in range(1, 7):
            planner = HeuristicPlanner(heuristic=MaxHeuristic(stats=benchmark.get_instance(domain_name=TestBenchmark.blocks, problem_name=TestBenchmark.blocks_pb % i)), PriorityQueue=hqueue.ThreadSafePriorityQueue)
            planner.collect_benchmark = True
            print("Benchmarking Blocks world pb%i.pddl" % i)
            planner.solve_file(TestBenchmark.blocks, TestBenchmark.blocks_pb % i)

        benchmark.table_stat(TestBenchmark.blocks, stat=Stats.time, xaxis='problem')
        expected_filename = benchmark.get_filename('blocksworld.pddl', Stats.time, '', 'csv')
        self.assertTrue(os.path.exists(expected_filename))

    @unittest.skip
    def test_graphs(self):  # pragma: no cover
        benchmark = PlanningBenchmark(output_folder='../tmp')
        for i in range(100):
            stats = benchmark.get_instance('blocks.pddl', 'pb%d.pddl' % i)
            stats.nodes = i * 1000
            stats.action_space = (i ** 2) * 10000
            stats.h_calls = stats.nodes * stats.action_space / 2
            stats.time = stats.h_calls * 3

        # benchmark.plot_stat('blocks.pddl')
        x, y = benchmark.get_stats('blocks.pddl')

        for i in range(1, 7):
            planner = HeuristicPlanner(heuristic=MaxHeuristic(
                stats=benchmark.get_instance(domain_name=TestBenchmark.blocks,
                                             problem_name=TestBenchmark.blocks_pb % i)), PriorityQueue=hqueue.ThreadSafePriorityQueue)
            planner.collect_benchmark = True
            print("Benchmarking Blocks world pb%i.pddl" % i)
            planner.solve_file(TestBenchmark.blocks, TestBenchmark.blocks_pb % i)

        hActions, hTime = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='time',
                                              approach='Heuristic')
        print('Actions x Time: %s' % [p for p in zip(hActions, hTime)])
        hProblem, hTime = benchmark.get_stats(TestBenchmark.blocks, xaxis='problem', stat='time',
                                              approach='Heuristic')
        print('Problem x Time: %s' % [p for p in zip(hProblem, hTime)])
        hActions, hNodes = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='nodes',
                                               approach='Heuristic')
        print('Actions x Nodes: %s' % [p for p in zip(hActions, hNodes)])
        hActions, hCalls = benchmark.get_stats(TestBenchmark.blocks, xaxis='action',
                                               stat='h_calls', approach='Heuristic')
        print('Actions x Calls: %s' % [p for p in zip(hActions, hCalls)])

        # benchmark.plot_stat(TestBenchmark.blocks,xaxis='action',stat='time',approach='Heuristic')
        # benchmark.plot_stat(TestBenchmark.blocks, xaxis='problem', stat='time', approach='Heuristic')

        benchmark.reset_stats()

        for i in range(1, 7):
            planner = BFSPlanner()
            planner.collect_benchmark = True
            planner.solve_file(TestBenchmark.blocks, TestBenchmark.blocks_pb % i)

        # benchmark.plot_stat(TestBenchmark.blocks, xaxis='action', stat='time', approach='BFS')
        # benchmark.plot_stat(TestBenchmark.blocks, xaxis='problem', stat='time', approach='BFS')

        hActions2, hTime2 = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='time',
                                                approach='BFS')
        print('Actions x Time (BFS): %s' % [p for p in zip(hActions2, hTime2)])
        hProblem2, hTime2 = benchmark.get_stats(TestBenchmark.blocks, xaxis='problem',
                                                stat='time',
                                                approach='BFS')
        print('Problem x Time (BFS): %s' % [p for p in zip(hProblem2, hTime2)])
        hActions2, hNodes2 = benchmark.get_stats(TestBenchmark.blocks, xaxis='action',
                                                 stat='nodes',
                                                 approach='BFS')
        print('Actions x Nodes (BFS): %s' % [p for p in zip(hActions2, hNodes2)])
        hActions2, hCalls2 = benchmark.get_stats(TestBenchmark.blocks, xaxis='action',
                                                 stat='h_calls', approach='BFS')
        print('Actions x Calls (BFS): %s' % [p for p in zip(hActions2, hCalls2)])

        benchmark.reset_stats()
        for i in range(1, 7):
            planner = HeuristicPlanner(heuristic=MaxHeuristic(
                stats=benchmark.get_instance(domain_name=TestBenchmark.blocks,
                                             problem_name=TestBenchmark.blocks_pb % i)), PriorityQueue=hqueue.PriorityQueue)
            planner.collect_benchmark = True
            print("Benchmarking Blocks world pb%i.pddl" % i)
            planner.solve_file(TestBenchmark.blocks, TestBenchmark.blocks_pb % i)

        hActions3, hTime3 = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='time', approach='Heuristic/Queue')
        print('Actions x Time: %s' % [p for p in zip(hActions, hTime)])
        hProblem3, hTime3 = benchmark.get_stats(TestBenchmark.blocks, xaxis='problem', stat='time', approach='Heuristic/Queue')
        print('Problem x Time: %s' % [p for p in zip(hProblem, hTime)])
        hActions3, hNodes3 = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='nodes', approach='Heuristic/Queue')
        print('Actions x Nodes: %s' % [p for p in zip(hActions, hNodes)])
        hActions3, hCalls3 = benchmark.get_stats(TestBenchmark.blocks, xaxis='action', stat='h_calls', approach='Heuristic/Queue')
        print('Actions x Calls: %s' % [p for p in zip(hActions, hCalls)])

        fig1 = plt.figure()
        ax1 = fig1.add_subplot()
        ax1.plot(hActions, hTime, label="h_max")
        ax1.plot(hActions2, hTime2, label="BFS")
        ax1.plot(hActions3, hTime3, label="h_max/queue")
        ax1.legend(loc='lower right')
        ax1.set_title("Time Performance")
        ax1.set_xlabel("Problem Actions")
        ax1.set_ylabel("Time (s)")
        plt.show()

        fig2 = plt.figure()
        ax2 = fig2.add_subplot()
        ax2.plot(hActions, hNodes, label="h_max")
        ax2.plot(hActions2, hNodes2, label="BFS")
        ax2.plot(hActions3, hNodes3, label="h_max/queue")
        ax2.legend(loc='lower right')
        ax2.set_title("Expanded Nodes")
        ax2.set_xlabel("Problem Actions")
        ax2.set_ylabel("Expanded Nodes")
        plt.show()

        fig4 = plt.figure()
        ax4 = fig4.add_subplot()
        ax4.plot(hActions, hCalls, label="h_max")
        ax4.plot(hActions2, hCalls2, label="BFS")
        ax4.plot(hActions3, hCalls3, label="h_max/queue")
        ax4.legend(loc='lower right')
        ax4.set_title("Heuristic Function Calls")
        ax4.set_xlabel("Problem Actions")
        ax4.set_ylabel("H Calls")
        plt.show()

        fig3 = plt.figure()
        ax3 = fig3.add_subplot()

        x = range(len(hProblem))  # the label locations
        width = 0.25  # the width of the bars

        rects1 = ax3.bar([xv - width / 3 for xv in x], hTime, width, label="h_max")
        rects2 = ax3.bar([xv + width / 3 for xv in x], hTime2, width, label="BFS")
        rects3 = ax3.bar([xv + width / 3 for xv in x], hTime3, width, label="h_max/Queue")

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax3.set_xlabel('Problem Name')
        ax3.set_ylabel('Time (s)')
        ax3.set_title('Problem')
        ax3.set_xticks(x)
        ax3.set_xticklabels(hProblem)
        ax3.legend()

        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                ax3.annotate('{:.4f}'.format(height),
                             xy=(rect.get_x() + rect.get_width() / 3, height),
                             xytext=(0, 3),  # 3 points vertical offset
                             textcoords="offset points",
                             ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)
        autolabel(rects3)

        fig3.tight_layout()
        plt.show()

    def test_run_benchmark(self):
        # TODO Prepare dataset
        command = "pddl.run_benchmark -v -o ../tmp -d ../tmp/prodcell ../scripts/baseline.yaml ../scripts/baseline-add.yaml".split()
        try:
            pddl.run_benchmark.main(command)
            self.assertTrue(True, "This should not error")
            # self.assertTrue(os.path.exists(TMP_FOLDER+"domain.pddl"))
        except Exception as e:
            self.assertFalse(True, "Exception %s should not happen" % e)

        # TODO Fix the test below
        # command = "pddl.run_benchmark -v -o ../tmp -d ../tmp/prodcell ../scripts/baseline.yaml".split()
        # try:
        #     pddl.run_benchmark.main(command)
        #     self.assertTrue(True, "This should not error")
        #     # self.assertTrue(os.path.exists(TMP_FOLDER+"domain.pddl"))
        # except Exception as e:
        #     self.assertFalse(True, "Exception %s should not happen" % e)

        command = "pddl.run_benchmark -v -o ../tmp -d %s ../scripts/baseline.yaml ../scripts/baseline-add.yaml" % TestBenchmark.openstacks
        command = command.split()
        try:
            pddl.run_benchmark.main(command)
            self.assertTrue(True, "This should not error")
            # self.assertTrue(os.path.exists(TMP_FOLDER+"domain.pddl"))
        except Exception as e:
            self.assertFalse(True, "Exception %s should not happen" % e)

    def test_load_configurations(self):
        planner_class, heuristic_class, planner_pars, heuristic_pars = pddl.run_benchmark.load_yaml('../scripts/baseline.yaml')
        self.assertEqual(planner_class, HeuristicPlanner)
        self.assertEqual(heuristic_class, MaxHeuristic)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
