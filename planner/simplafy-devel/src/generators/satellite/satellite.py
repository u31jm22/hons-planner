#!/usr/bin/env python3

"""
Satellite Domain PDDL Problem Generator (Python Version)
Based on original C++ version (satgen.cc).
https://github.com/AI-Planning/pddl-generators/tree/main/satellite
Supports STRIPS, NUMERIC, SIMPLETIME, TIMED, COMPLEX domain types.

Command-line usage:
  satellite.py [-T <d>|-u|-s|-t|-n|-c|-h] <seed> <#s> <#i> <#m> <#t> <#o>

Arguments:
  <seed>    : random seed
  <#s>      : number of satellites
  <#i>      : max instruments per satellite
  <#m>      : number of modes
  <#t>      : number of targets
  <#o>      : number of observations

Flags:
  -u        : untyped problem
  -s        : simple-time
  -t        : timed
  -n        : numeric
  -c        : complex
  -h        : hard metric
  -T <val>  : data tightness in [0, 1)
"""

import sys
import random
import argparse
import shutil
import math
from enum import Enum
from abc import ABC, abstractmethod
import copy


# Global enums and variables
class ProbTypes(Enum):
    STRIPS = 0
    NUMERIC = 1
    SIMPLETIME = 2
    TIMED = 3
    COMPLEX = 4


class TypeStatus(Enum):
    ON = 0
    OFF = 1


class MetricSort(Enum):
    HARD = 0
    EASY = 1

# Global variables
prob_type = ProbTypes.STRIPS
typing = TypeStatus.ON
metric_type = MetricSort.EASY
tightness = 0.3


def rnd_int(limit):
    """Random integer from 0 to limit-1"""
    return random.randint(0, limit - 1)


def rnd_float():
    """Random float from 0.0 to 1.0"""
    return random.random()


class ProblemObject(ABC):
    """Abstract base class for all problem objects"""
    class OutStatus(Enum):
        OBJECT = 0
        INIT = 1
        GOAL = 2

    out_status = OutStatus.OBJECT

    @abstractmethod
    def object(self, output):
        pass

    @abstractmethod
    def init(self, output):
        pass

    @abstractmethod
    def goal(self, output):
        pass

    def write(self, output):
        if self.out_status == ProblemObject.OutStatus.OBJECT:
            self.object(output)
        elif self.out_status == ProblemObject.OutStatus.INIT:
            self.init(output)
        elif self.out_status == ProblemObject.OutStatus.GOAL:
            self.goal(output)

    @classmethod
    def set_objects(cls):
        cls.out_status = cls.OutStatus.OBJECT

    @classmethod
    def set_inits(cls):
        cls.out_status = cls.OutStatus.INIT

    @classmethod
    def set_goals(cls):
        cls.out_status = cls.OutStatus.GOAL


class Direction(ProblemObject):
    """Base class for directions (targets and observations)"""

    id_counter = 0
    all_directions = []

    def __init__(self):
        self.my_id = Direction.id_counter
        Direction.id_counter += 1
        self.nm = ""
        self.slew_times = []

        # Generate slew times to all previous directions
        for i in range(self.my_id):
            a = rnd_float() * 100.0
            b = rnd_float() * 100.0
            self.slew_times.append(abs(a - b))

    def name(self):
        return self.nm

    def object(self, output):
        output.append(f"\t{self.name()}")
        if typing == TypeStatus.ON:
            output.append(" - direction")
        output.append("\n")

    def init(self, output):
        if typing == TypeStatus.OFF:
            output.append(f"\t(direction {self.name()})\n")

        if prob_type in [ProbTypes.TIMED, ProbTypes.COMPLEX, ProbTypes.NUMERIC]:
            for i in range(self.my_id):
                slew_time = f"{self.slew_times[i]:.4f}"
                output.append(f"\t(= (slew_time {self.name()} {Direction.all_directions[i].name()}) {slew_time})\n")
                output.append(f"\t(= (slew_time {Direction.all_directions[i].name()} {self.name()}) {slew_time})\n")

    def goal(self, output):
        pass


class Target(Direction):
    """Target direction (Star or GroundStation)"""

    types = ["Star", "GroundStation"]
    count = 0

    def __init__(self):
        super().__init__()
        self.type = rnd_int(2)
        Target.count += 1
        self.nm = f"{Target.types[self.type]}{self.my_id}"
        Direction.all_directions.append(copy.deepcopy(self))

    @classmethod
    def how_many(cls):
        return cls.count

    def __eq__(self, other):
        return isinstance(other, Target) and self.my_id == other.my_id


class Mode(ProblemObject):
    """Instrument mode"""

    supported_modes = []
    types = ["infrared", "image", "spectrograph", "thermograph"]
    id_counter = 0

    def __init__(self):
        self.my_id = Mode.id_counter
        Mode.id_counter += 1
        self.type = rnd_int(4)
        Mode.supported_modes.append(False)

    @classmethod
    def how_many(cls):
        return cls.id_counter

    def __eq__(self, other):
        return isinstance(other, Mode) and self.my_id == other.my_id

    def name(self):
        return f"{Mode.types[self.type]}{self.my_id}"

    def supported(self):
        Mode.supported_modes[self.my_id] = True

    def object(self, output):
        output.append(f"\t{Mode.types[self.type]}{self.my_id}")
        if typing == TypeStatus.ON:
            output.append(" - mode")
        output.append("\n")

    def init(self, output):
        if typing == TypeStatus.OFF:
            output.append(f"\t(mode {Mode.types[self.type]}{self.my_id})\n")

        if prob_type in [ProbTypes.NUMERIC, ProbTypes.COMPLEX]:
            for obs in Observation.all_observations:
                data_size = obs.get_data_size(self.my_id)
                output.append(f"\t(= (data {obs.name()} {Mode.types[self.type]}{self.my_id}) {data_size})\n")

    def goal(self, output):
        pass

    def is_supported(self):
        return Mode.supported_modes[self.my_id]


class Observation(Direction):
    """Observation direction"""

    types = ["Star", "Phenomenon", "Planet"]
    all_observations = []

    def __init__(self):
        super().__init__()
        self.type = rnd_int(3)
        self.interesting = True  # Always interesting to ensure goals exist
        self.images = []
        self.data_size = []

        # Select some modes for this observation
        ims = 1 + rnd_int(max(1, Mode.how_many() // 3))
        problem_instance = Problem.instance()
        if problem_instance:
            selected_modes = problem_instance.modes.select_several(ims)
            self.images = selected_modes

        self.nm = f"{Observation.types[self.type]}{self.my_id}"
        Direction.all_directions.append(copy.deepcopy(self))

        # Generate data sizes for all modes
        for i in range(Mode.how_many()):
            self.data_size.append(1 + rnd_int(int(1000 * tightness)))

        Observation.all_observations.append(copy.deepcopy(self))

    def get_data_size(self, md_num):
        if md_num < len(self.data_size):
            return self.data_size[md_num]
        return 0

    def goal(self, output):
        if self.interesting and metric_type == MetricSort.EASY:
            for mode in self.images:
                if mode.is_supported():
                    output.append(f"\t(have_image {self.name()} {mode.name()})\n")


class Selection:
    """Template class for selecting objects"""

    def __init__(self, items=None, n=0):
        if items is not None:
            self.choices = list(items)
        elif n > 0:
            self.choices = []
            for i in range(n):
                if hasattr(self, '_item_type'):
                    self.choices.append(self._item_type())
        else:
            self.choices = []
        self.sz = len(self.choices)

    def select_one(self):
        if self.sz == 0:
            return None
        return self.choices[rnd_int(self.sz)]

    def size(self):
        return self.sz

    def select_several(self, n, callback=None):
        selected = []
        original_choices = self.choices.copy()

        for i in range(min(n, self.sz)):
            if self.sz == 0:
                break
            item = self.select_one()
            self.choices = [x for x in self.choices if x != item]
            self.sz -= 1
            if callback:
                callback(item)
            selected.append(item)

        # Restore original choices
        self.choices = original_choices
        self.sz = len(self.choices)

        return selected

    def write(self, output):
        for choice in self.choices:
            choice.write(output)


class ModeSelection(Selection):
    def __init__(self, n=0):
        super().__init__()
        self._item_type = Mode
        for i in range(n):
            self.choices.append(Mode())
        self.sz = len(self.choices)


class TargetSelection(Selection):
    def __init__(self, n=0):
        super().__init__()
        self._item_type = Target
        for i in range(n):
            self.choices.append(Target())
        self.sz = len(self.choices)


class ObservationSelection(Selection):
    def __init__(self, n=0):
        super().__init__()
        self._item_type = Observation
        for i in range(n):
            self.choices.append(Observation())
        self.sz = len(self.choices)


class Problem:
    """Main problem class (singleton-like)"""

    DOMAIN = "generators/satellite/domain.pddl"

    instance_ref = None

    def __init__(self, ts, os, ms):
        Problem.instance_ref = self
        self.modes = ModeSelection(ms)
        self.targets = TargetSelection(ts)
        self.observations = ObservationSelection(os)

    @classmethod
    def instance(cls):
        return cls.instance_ref

    def write(self, output):
        self.modes.write(output)
        self.targets.write(output)
        self.observations.write(output)


def select_one_direction(targets, observations):
    """Select one direction from targets or observations"""
    total_size = targets.size() + observations.size()
    if total_size == 0:
        return None

    c = rnd_int(total_size)
    if c < targets.size():
        return targets.select_one()
    return observations.select_one()


class Instrument(ProblemObject):
    """Satellite instrument"""

    id_counter = 0

    def __init__(self):
        self.my_id = Instrument.id_counter
        Instrument.id_counter += 1
        self.calibration_times = []
        self.targets = []
        self.supported_modes = []
    
        # Select supported modes
        modes_count = 1 + rnd_int(3)
        problem_instance = Problem.instance()
        if problem_instance:
            selected_modes = problem_instance.modes.select_several(modes_count)
            self.supported_modes = selected_modes
            for mode in selected_modes:
                mode.supported()
    
        # Select calibration targets
        targs = 1 + rnd_int(max(1, Target.how_many() // 3))
        if problem_instance:
            self.targets = problem_instance.targets.select_several(targs)
            for i in range(len(self.targets)):
                self.calibration_times.append(100 * rnd_float())

    def name(self):
        return f"instrument{self.my_id}"

    def object(self, output):
        output.append(f"\tinstrument{self.my_id}")
        if typing == TypeStatus.ON:
            output.append(" - instrument")
        output.append("\n")

    def init(self, output):
        if typing == TypeStatus.OFF:
            output.append(f"\t(instrument instrument{self.my_id})\n")
    
        for mode in self.supported_modes:
            output.append(f"\t(supports instrument{self.my_id} {mode.name()})\n")
    
        for i, target in enumerate(self.targets):
            output.append(f"\t(calibration_target instrument{self.my_id} {target.name()})\n")
            if prob_type in [ProbTypes.COMPLEX, ProbTypes.TIMED]:
                cal_time = f"{self.calibration_times[i]:.3f}"
                output.append(f"\t(= (calibration_time instrument{self.my_id} {target.name()}) {cal_time})\n")

    def goal(self, output):
        pass


class Satellite(ProblemObject):
    """Satellite with instruments"""

    id_counter = 0

    def __init__(self, max_instruments):
        self.my_id = Satellite.id_counter
        Satellite.id_counter += 1
        self.instruments = []

        problem_instance = Problem.instance()
        if problem_instance:
            self.d = select_one_direction(problem_instance.targets, problem_instance.observations)
            self.end = select_one_direction(problem_instance.targets, problem_instance.observations)
        else:
            self.d = None
            self.end = None

        self.interesting = rnd_int(5) < 2
        self.fuel = 100 * (1 + rnd_float())

        # Create instruments
        insts = 1 + rnd_int(max_instruments)
        for i in range(insts):
            self.instruments.append(Instrument())

    def object(self, output):
        output.append(f"\tsatellite{self.my_id}")
        if typing == TypeStatus.ON:
            output.append(" - satellite")
        output.append("\n")

        for instrument in self.instruments:
            instrument.object(output)

    def init(self, output):
        if typing == TypeStatus.OFF:
            output.append(f"\t(satellite satellite{self.my_id})\n")

        for instrument in self.instruments:
            instrument.init(output)

        for instrument in self.instruments:
            output.append(f"\t(on_board {instrument.name()} satellite{self.my_id})\n")

        output.append(f"\t(power_avail satellite{self.my_id})\n")
        if self.d:
            output.append(f"\t(pointing satellite{self.my_id} {self.d.name()})\n")

        if prob_type in [ProbTypes.NUMERIC, ProbTypes.COMPLEX]:
            output.append(f"\t(= (data_capacity satellite{self.my_id}) 1000)\n")

        if prob_type == ProbTypes.NUMERIC:
            fuel_val = f"{self.fuel:.3f}"
            output.append(f"\t(= (fuel satellite{self.my_id}) {fuel_val})\n")

    def rnd_instrument(self):
        if self.instruments:
            return self.instruments[rnd_int(len(self.instruments))]
        return None

    def goal(self, output):
        if self.interesting and self.end:
            output.append(f"\t(pointing satellite{self.my_id} {self.end.name()})\n")


def do_metric():
    """Generate the metric specification"""
    if prob_type == ProbTypes.SIMPLETIME or prob_type == ProbTypes.TIMED:
        print("(:metric minimize (total-time))")
    elif prob_type == ProbTypes.NUMERIC:
        if metric_type == MetricSort.EASY:
            print("(:metric minimize (fuel-used))")
        else:
            print("(:metric maximize (data-stored))")
    elif prob_type == ProbTypes.COMPLEX:
        if metric_type == MetricSort.EASY:
            print("(:metric minimize (total-time))")
        else:
            print("(:metric maximize (data-stored))")


def main(argv):
    global typing, prob_type, metric_type, tightness

    parser = argparse.ArgumentParser(description='Generate PDDL satellite problems')
    parser.add_argument('--format', choices=['pddl', 'intention', 'both'], default='pddl', help='Output format')
    parser.add_argument('seed', type=int, help='Random seed')
    parser.add_argument('satellites', type=int, help='Number of satellites')
    parser.add_argument('instruments', type=int, help='Max instruments per satellite')
    parser.add_argument('modes', type=int, help='Number of modes')
    parser.add_argument('targets', type=int, help='Number of targets')
    parser.add_argument('observations', type=int, help='Number of observations')
    parser.add_argument('-u', '--untyped', action='store_true', help='Untyped')
    parser.add_argument('-s', '--simpletime', action='store_true', help='Simple-time')
    parser.add_argument('-t', '--timed', action='store_true', help='Timed')
    parser.add_argument('-n', '--numeric', action='store_true', help='Numeric')
    parser.add_argument('-c', '--complex', action='store_true', help='Complex')
    parser.add_argument('-a', '--hard', action='store_true', help='Hard metric')
    parser.add_argument('-d', '--desires', type=int, default=2, help='Number of desires to generate (of format is intention)')
    parser.add_argument('-T', '--tightness', type=float, default=0.3, help='Data tightness [0,1)')
    parser.add_argument('-o', '--output', type=str, help='Output file')

    args = parser.parse_args(argv[1:])

    generate_intention = args.format in ['intention', 'both']
    generate_pddl = args.format in ['pddl', 'both']

    if args.output:
        output_stream = open(args.output+"/pb%s.pddl" % args.satellites, 'w')
    else:
        output_stream = sys.stdout

    # Set global variables based on arguments
    if args.untyped:
        typing = TypeStatus.OFF
    if args.timed:
        prob_type = ProbTypes.TIMED
    elif args.simpletime:
        prob_type = ProbTypes.SIMPLETIME
    elif args.numeric:
        prob_type = ProbTypes.NUMERIC
    elif args.complex:
        prob_type = ProbTypes.COMPLEX

    if args.hard:
        metric_type = MetricSort.HARD

    tightness = args.tightness

    # Set random seed
    random.seed(args.seed)

    # Create problem
    pp = Problem(args.targets, args.observations, args.modes)

    # Create satellites
    satellites = []
    for i in range(args.satellites):
        satellites.append(Satellite(args.instruments))

    # Ensure all modes are supported
    all_modes = pp.modes.select_several(pp.modes.size())
    for mode in all_modes:
        if not mode.is_supported():
            s = rnd_int(len(satellites))
            satellites[s].supported_modes.append(mode)
            mode.supported()

    # Generate PDDL output
    output = []
    # output_string = ""

    print("(define (problem strips-sat-x-1)", file=output_stream)
    print("(:domain satellite)", file=output_stream)
    print("(:objects", file=output_stream)
    # print("(define (problem strips-sat-x-1)")
    # print("(:domain satellite)")
    # print("(:objects")

    # Objects
    ProblemObject.set_objects()
    for sat in satellites:
        sat.write(output)
    pp.write(output)
    print(''.join(output), end='', file=output_stream)
    print(")", file=output_stream)
    # print(''.join(output), end='')
    # print(")")

    # Initial state
    output.clear()
    # print("(:init")
    print("(:init", file=output_stream)
    ProblemObject.set_inits()
    for sat in satellites:
        sat.write(output)
    pp.write(output)

    if prob_type in [ProbTypes.NUMERIC, ProbTypes.COMPLEX]:
        output.append("\t(= (data-stored) 0)\n")
    if prob_type == ProbTypes.NUMERIC:
        output.append("\t(= (fuel-used) 0)\n")

    print(''.join(output), end='', file=output_stream)
    print(")", file=output_stream)

    # Goals
    output.clear()
    if generate_pddl:
        print("(:goal (and", file=output_stream)
        ProblemObject.set_goals()
        for sat in satellites:
            sat.write(output)
        pp.write(output)
        print(''.join(output), end='', file=output_stream)
        print("))", file=output_stream)

    output.clear()
    if generate_intention:
        print("(:desires", file=output_stream)
        ProblemObject.set_goals()
        pp.write(output)  # FIXME Hack to ensure we output observations exactly once
        satellites[0].write(output)
        print("(:desire (and", file=output_stream)
        print(''.join(output), end='', file=output_stream)
        print("))", file=output_stream)
        output.clear()
        satellites = satellites[1:]
        sps = math.ceil(args.satellites-1 / args.desires-1)  # Satellites per problem
        for desire in range(1, args.desires):
            for sat in satellites[0:sps]:
                sat.write(output)
            if output:
                print("(:desire (and", file=output_stream)
                print(''.join(output), end='', file=output_stream)
                print("))", file=output_stream)
            output.clear()
            satellites = satellites[sps:]

        # pp.write(output)  # FIXME Hack to ensure we output observations exactly once

        # for sat in satellites:
        #     sat.write(output)
        #     if output:
        #         print("(:desire (and", file=output_stream)
        #         print(''.join(output), end='', file=output_stream)
        #         print("))", file=output_stream)
        #     output.clear()
        print(")", file=output_stream)

    # Metric
    do_metric()
    print("\n)", file=output_stream)
    if args.output is not None:
        shutil.copy(Problem.DOMAIN, args.output+"/domain.pddl")


if __name__ == "__main__":  # pragma: no cover
    try:
        main(sys.argv)
    except Exception as e:
        print(e)
        sys.exit(-1)
