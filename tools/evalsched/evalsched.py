#!/usr/bin/env python3

import argparse
import collections
import enum
import json
import logging
import random
import sched
import sys


TICK = 1 # millisecond


DEFAULT_RANDOM_SEED = 42
DEFAULT_DURATION_SECONDS = 600
DEFAULT_NODE_NUMBER = 1
DEFAULT_NODE_CAPACITY = 100
DEFAULT_EVENT_PRIO = 10 # lower priority are for mgmt events (start/stop)


def to_ticks(ts):
    return ts * 1000


class Time:
    def __init__(self, now=0.0):
        self._now = now

    def time(self):
        return self._now

    def sleep(self, amount):
        self._now += amount


class Event:
    def __init__(self, name, time, action):
        self._name = name
        self._time = time
        self._action = action
        self._created = self._time.time()

    def __str__(self):
        return 'from_vt=%s [%s]' % (
            self._created, self._name
        )

    def __call__(self):
#        logging.info('vt=%s calling %s', self._time.time(), str(self))
        res = self._action()
        logging.info('vt=%s %s -> [%s]', self._time.time(), str(self), res)
        return res


class Node:
    def __init__(self, name, capacity, time, skd, period):
        self._name = name
        self._capacity = capacity
        self._time = time
        self._skd = skd
        self._period = period
        self._clean = False if period > 0 else True
        self._node_updates = 0

    def __str__(self):
        return 'node %s clean=%s cap=%s update_period=%s' % (
                self._name, self._clean, self._capacity, self._period)

    @property
    def name(self):
        return self._name

    @property
    def capacity(self):
        return self._capacity

    @property
    def clean(self):
        return self._clean

    @property
    def dirty(self):
        return not self._clean

    def admit(self):
        self._clean = False
        self._capacity -= 1
        if self._period == 0:
            self._node_updates += 1
            self._skd.enter(TICK, DEFAULT_EVENT_PRIO,
                    Event('admit_update=%s' % self._name, self._time, self.update))

    def delete(self):
        self._clean = False
        self._capacity += 1
        if self._period == 0:
            self._node_updates += 1
            self._skd.enter(TICK, DEFAULT_EVENT_PRIO,
                    Event('delete_update=%s' % self._name, self._time, self.update))

    def update(self, delay=None):
        if delay is None:
            delay = self._period
        delay = to_ticks(delay)
        self._clean = True
        if self._period > 0:
            self._node_updates += 1
            self._skd.enter(delay, DEFAULT_EVENT_PRIO,
                    Event('timer_update=%s' % self._name, self._time, self.update))
        return self

    def results(self):
        return {
            "node_updates": self._node_updates,
        }


class SchedulingOutcome(enum.Enum):
    SUCCESS = 0
    FAILED_DIRTY = 1
    FAILED_CAPACITY = 2


class Scheduler:
    def __init__(self, rnd, time, nodes):
        self._rnd = rnd
        self._time = time
        self._nodes = nodes

    def schedule(self):
        all_nodes = self._nodes[:]

        clean_nodes = [node for node in all_nodes if node.clean]
        if not clean_nodes:
            return SchedulingOutcome.FAILED_DIRTY, None

        candidates = [node for node in clean_nodes if node.capacity > 0]
        if not candidates:
            return SchedulingOutcome.FAILED_CAPACITY, None

        node = self._rnd.choice(candidates)
        node.admit()
        return SchedulingOutcome.SUCCESS, node


class Cluster: 
    def __init__(self, rnd, time, skd, node_num, node_capacity, node_update_period):
        self._rnd = rnd
        self._time = time
        self._skd = skd
        self._nodes = []
        for num in range(node_num):
            node = Node("node%02d" % num, node_capacity, time, skd, node_update_period)
            if node_update_period > 0:
                node.update(self._rnd.randrange(node_update_period))
            self._nodes.append(node)
        self._kubesched = Scheduler(self._rnd, self._time, self._nodes)
        self._results = {
                k:0 for k in list(SchedulingOutcome)
        }
        self._pods = 0

    def __str__(self):
        return 'Cluster(\n%s\n)' % (
                '\n'.join('  ' + str(node) for node in self._nodes)
        )

    def create_pod(self, name, ts):
        self._pods += 1
        self._skd.enter(ts, DEFAULT_EVENT_PRIO,
            Event('request_pod=%s' % name, self._time, self._pod_event))

    def _pod_event(self):
        res, node = self._kubesched.schedule()
        self._results[res] += 1
        return node

    def results(self):
        node_updates = sum(
            node.results().get("node_updates", 0) for node in self._nodes
        )
        stats = {
            "pods": self._pods,
            "node_updates": node_updates,
            "pod_admissions": {
                "success": self._results[SchedulingOutcome.SUCCESS],
                "failed_dirty": self._results[SchedulingOutcome.FAILED_DIRTY],
                "failed_capacity":
                self._results[SchedulingOutcome.FAILED_CAPACITY],
            },
        }
        return stats


def default_config():
    return {
        "random_seed": DEFAULT_RANDOM_SEED,
        "duration_seconds": DEFAULT_DURATION_SECONDS,
        "nodes": {
            "number": DEFAULT_NODE_NUMBER,
            "capacity": DEFAULT_NODE_CAPACITY,
        },
    }


def load_config(name=None):
    conf = {}
    conf.update(default_config())
    if name is not None:
        if name == '-':
            conf.update(json.load(sys.stdin))
        else:
            with open(name) as src:
                conf.update(json.load(src))
    return conf



def stop():
    raise StopIteration



def dist_from_string(arg):
    tokens = arg.split(',')
    if len(tokens) < 1:
        raise RuntimeError('bad distribution: %s' % arg)
    name, args = tokens[0].lower(), dict(tok.split('=') for tok in tokens[1:])
    if name == "burst":
        return DistBurst(**args)
    else:
        raise RuntimeError('unknown distribution')


class DistBurst:
    def __init__(self, **kwargs):
        self._count = int(kwargs.get('count', 1))  # how many bursts?
        self._duration = int(kwargs.get('duration', 10))  # how many pods per burst?
        self._delay = int(kwargs.get('delay', 1))  # how much time (ms) between pods in a single burst?
        self._period = int(kwargs.get('period', 0))  # how much time (ms) between bursts?

    def __str__(self):
        return (
            'burst,count={self._count},duration={self._duration},'
            'delay={self._delay},period={self._period}'
        ).format(self=self)

    def apply(self, cluster):
        if self._count > 1 and self._period == 0:
            raise ValueError("need valid period if count is greater than one")
        for cnt in range(self._count):
            for num in range(self._duration):
                dt = (cnt * self._period) + (self._delay * num)
                cluster.create_pod('pod-%03d-%03d' % (cnt, num), dt)


def _main():
    parser = argparse.ArgumentParser(prog='evalsched')
    parser.add_argument('-c', '--config', nargs='?', default='config.json',
                        help='cluster definition file path')
    parser.add_argument('-S', '--seed', nargs='?', metavar='S', type=int,
                        help='set random seed')
    parser.add_argument('-D', '--duration', nargs='?', metavar='secs', type=int,
                        help='set simulation duration (seconds)')
    parser.add_argument('-E', '--events', action='store_true',
                        help='dump simulation event log')
    parser.add_argument('dist', nargs='+', help='pod distribution')
    args = parser.parse_args()

    if args.duration is None:
        sys.stderr.write('missing simulation duration time value\n')
        sys.exit(1)

    logging.basicConfig(
            format='%(asctime)s %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            level=logging.DEBUG if args.events else logging.ERROR
    )

    conf = load_config(args.config)

    tm = Time()
    rnd = random.Random(args.seed)
    skd = sched.scheduler(tm.time, tm.sleep)
    nodes = conf['nodes']
    cluster = Cluster(rnd, tm, skd, nodes['number'], nodes['capacity'],
            nodes['update_period_seconds']) 
    logging.info(cluster)
    skd.enter(0, 0,
            Event('start', tm, lambda: 'seed=%s' % args.seed))
    skd.enter(to_ticks(args.duration), 0,
        Event('stop', tm, stop))

    try:
        for arg in args.dist:
            dist = dist_from_string(arg)
            logging.info('applying distribution: %s', str(dist))
            dist.apply(cluster)
    except ValueError as exc:
        sys.stderr.write(
                "failed applying dist %s: %s\n" % (
                    str(dist), str(exc)))
        sys.exit(1)

    try:
        skd.run()
    except StopIteration:
        pass

    print(json.dumps(cluster.results()))


if __name__ == "__main__":
    _main()
