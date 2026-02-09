#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import re
import os
import matplotlib.pyplot as plt
from enum import StrEnum
from typing import Iterable, Iterator

# TODO Refactor these classes to use the enum instead
# right now I'm just using it to keep track of the stats I'm keeping
Stats = StrEnum('Stats', ['nodes', 'nodes_first', 'h_calls', 'action_space', 'time', 'queue_time', 'h_time', 'time_last'])


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class InstanceStats:

    def __init__(self, domain_name="problem.pddl", problem_name="pb.pddl", stat_names: Iterable[str] = [s for s in Stats]):
        self.domain_name = domain_name
        self.problem_name = problem_name
        # self.nodes = 0
        # self.nodes_first = 0
        # self.h_calls = 0
        # self.h_time = 0
        # self.action_space = 0
        # self.time = 0
        # self.queue_time = 0
        self.stat_data = dict()
        for stat in stat_names:
            self.stat_data[stat] = 0

    def __getattr__(self, name):
        if hasattr(Stats, name):
            return self.stat_data[name]
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if hasattr(Stats, name):
            self.stat_data[name] = value
        else:
            super().__setattr__(name, value)

    def __getitem__(self, key: str) -> object:
        return self.stat_data[key]

    def __setitem__(self, key: str, value: float):
        self.stat_data[key] = value

    def __contains__(self, item):
        return item in self.stat_data

    def __iter__(self) -> Iterator:
        return iter(self.stat_data)

    def __str__(self):
        header = "Domain, Problem"
        data = "%s, %s" % (self.domain_name, self.problem_name)
        for stat_name in self.stat_data.keys():
            header += ", {}".format(stat_name)
            data += ",{:.2f}".format(self.stat_data[stat_name])
        return header+"\n"+data

    def __repr__(self):
        return str(self)


class PlanningBenchmark(metaclass=Singleton):

    def __init__(self, output_folder: str = '.', file_suffix: str = ''):
        self.stat_instances = {}
        self._output_folder = output_folder
        self._file_suffix = file_suffix

    def get_filename(self, domain_name: str, data_name: str, extra_suffix: str = "", extension: str = 'pdf'):
        filename = "%s/%s-%s-%s-%s.%s" % (self._output_folder, domain_name, data_name, self._file_suffix, extra_suffix, extension)
        return filename

    def filename_to_id(self, filename: str) -> str:
        domain_name = None
        if re.search(r'^domain\d{2}\.pddl$', os.path.basename(filename)) and filename.find('/') != -1:
            domain_name = filename[filename.find('/')+1:filename.rfind('/')]
        else:
            domain_name = filename[filename.rfind('/')+1:]
        return domain_name

    def reset_stats(self):
        self.stat_instances = {}

    def get_instance(self, domain_name: str, problem_name: str):
        # Cleanup long file names
        domain_name = self.filename_to_id(domain_name)
        problem_name = self.filename_to_id(problem_name)
        if domain_name not in self.stat_instances.keys():
            self.stat_instances[domain_name] = {}
        domain = self.stat_instances[domain_name]

        if problem_name not in domain:
            domain[problem_name] = InstanceStats(domain_name, problem_name)
        return domain[problem_name]

    def get_stats(self, domain_name, stat='time', xaxis='action', approach=None):
        domain_name = self.filename_to_id(domain_name)
        y = [instance[stat] for k, instance in self.stat_instances[domain_name].items()]

        if xaxis == 'action':
            x = [instance.action_space for k, instance in self.stat_instances[domain_name].items()]
        elif xaxis == 'problem':
            # # Recall that the whole rigamarole below is to find the final file name
            # x = [instance.problem_name[instance.problem_name.rfind('/')+1:] for k, instance in self.stat_instances[domain_name].items()]
            x = [instance.problem_name for k, instance in self.stat_instances[domain_name].items()]

        return x, y

    def table_stat(self, domain_name, stat='time', xaxis='action', label='', approach=None):
        domain_name = self.filename_to_id(domain_name)
        with open(self.get_filename(domain_name, stat, '', 'csv'), mode='w') as csv_file:
            x, y = self.get_stats(domain_name, stat, xaxis)
            for i, j in zip(x, y):
                csv_file.write("{}, {}\n".format(i, j))
            csv_file.close()

    def plot_stat(self, domain_name, stat='time', xaxis='action', label='', approach=None):
        domain_name = self.filename_to_id(domain_name)
        if label == '':
            label = '%s: %s by %s (%s)' % (xaxis, stat, domain_name, approach)

        if stat == 'time':
            y = [instance.time for k, instance in self.stat_instances[domain_name].items()]
        elif stat == 'nodes':
            y = [instance.node for k, instance in self.stat_instances[domain_name].items()]
        elif stat == 'h_calls':
            y = [instance.problem_name[instance.problem_name.rfind('/')+1:] for k, instance in self.stat_instances[domain_name].items()]
        plt.figure()

        if xaxis == 'action':
            # for instance in self.stat_instances[domain_name]:
            #     print(instance)
            x = [instance.action_space for k, instance in self.stat_instances[domain_name].items()]
            plt.plot(x, y, label=label)
            # plt.plot(x, y, xlabel='\# Actions', ylabel='Time (s)', label='Actions vs Time')
        elif xaxis == 'problem':
            x = [instance.problem_name for k, instance in self.stat_instances[domain_name].items()]
            # plt.bar(x,y, xlabel='Problem', ylabel='Time (s)', label='Problems vs Time')
            plt.bar(x, y, label=label)
        # plt.show(block=False)
        plt.show()
