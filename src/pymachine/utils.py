import logging
import os

import networkx as nx
from networkx.readwrite import json_graph

from pymachine.machine import Machine

def ensure_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

class MachineTraverser():
    @staticmethod
    def get_nodes(machine, exclude_words=[]):
        traverser = MachineTraverser()
        # logging.info('getting nodes for: {0}'.format(machine.printname()))
        return traverser._get_nodes(machine, depth=0,
                                    exclude_words=set(exclude_words))

    def __init__(self):
        self.seen_for_nodes = set()

    def _get_nodes(self, machine, depth, exclude_words=set()):
        if machine in self.seen_for_nodes:
            return
        self.seen_for_nodes.add(machine)
        name = machine.printname()
        # logging.info(u'traversing: {0}'.format(name))
        if not name.isupper() and name not in exclude_words:
            yield name

        for part in machine.partitions:
            for submachine in part:
                for node in self._get_nodes(submachine, depth=depth+1,
                                            exclude_words=exclude_words):
                    yield node
        for parent, _ in machine.parents:
            for node in self._get_nodes(parent, depth=depth+1,
                                        exclude_words=exclude_words):
                yield node

class MachineGraph:
    @staticmethod
    def create_from_machines(iterable, max_depth=None, whitelist=None,
                             strict=False):
        g = MachineGraph()
        g.seen = set()
        # logging.debug('whitelist: {}'.format(whitelist))
        for machine in iterable:
            g._get_edges_recursively(machine, max_depth, whitelist,
                                     strict=strict)

        return g

    def _get_edges_recursively(self, machine, max_depth, whitelist,
                               strict=False, depth=0):
        # pn = machine.printname()
        # logging.info(u'getting edges for machine: {}'.format(pn))
        # logging.info("{0}".format(machine.partitions))
        #  if pn.isupper():
        #      if depth >= 2:
        #          return
        if machine in self.seen or (max_depth is not None and
                                    depth > max_depth):
            return
        self.seen.add(machine)
        # if printname == 'from':
        #     logging.info('from machine: {0}'.format(machine))
        edges = set()
        neighbours = set()
        for color, part in enumerate(machine.partitions):
            for machine2 in part:
                if machine2 in self.seen:
                    continue
                neighbours.add(machine2)
                edges.add((machine, machine2, color))
        for parent, color in machine.parents:
            if parent in self.seen:
                continue
            neighbours.add(parent)
            edges.add((parent, machine, color))

        for machine1, machine2, color in edges:
            printname1 = machine1.printname()
            printname2 = machine2.printname()
            if (whitelist is not None and printname1 not in whitelist and
                    printname2 not in whitelist):
                continue
            elif whitelist is None or (printname1 in whitelist and
                                       printname2 in whitelist):
                self.add_edge(
                    machine1.unique_name(), machine2.unique_name(), color)

        for neighbour in neighbours:
            self._get_edges_recursively(
                neighbour, max_depth, whitelist, depth=depth+1)

    def __init__(self):
        self.G = nx.MultiDiGraph()

    def add_edge(self, node1, node2, color):
        # logging.debug(u'adding edge: {} -> {}'.format(node1, node2))
        self.G.add_nodes_from([node1, node2])
        self.G.add_edge(node1, node2, color=color)

    def to_dict(self):
        return json_graph.adjacency.adjacency_data(self.G)

    @staticmethod
    def from_dict(d):
        return json_graph.adjacency.adjacency_graph(d)

    def to_dot(self):
        lines = [u'digraph finite_state_machine {', '\tdpi=100;']
        # lines.append('\tordering=out;')
        # sorting everything to make the process deterministic
        node_lines = []
        for node in self.G.nodes_iter():
            d_node = Machine.d_clean(node)
            printname = Machine.d_clean(d_node.split('_')[0])
            node_lines.append(u'\t{0} [shape = circle, label = "{1}"];'.format(
                d_node, printname).replace('-', '_'))
        lines += sorted(node_lines)
        edge_lines = []
        for node1, adjacency in self.G.adjacency_iter():
            d_node1 = Machine.d_clean(node1)
            for node2, edges in adjacency.iteritems():
                d_node2 = Machine.d_clean(node2)
                for i, attributes in edges.iteritems():
                    edge_lines.append(
                        u'\t{0} -> {1} [ label = "{2}" ];'.format(
                            d_node1.replace('-', '_'),
                            d_node2.replace('-', '_'), attributes['color']))
        lines += sorted(edge_lines)
        lines.append('}')
        return u'\n'.join(lines)

def harmonic_mean(seq):
    try:
        length = float(len(seq))
    except TypeError:  # must be a generator
        return harmonic_mean(list(seq))
    if length == 0:
        return 0.0

    try:
        return length / sum((1.0/e for e in seq))
    except ZeroDivisionError:
        return 0.0


def average(seq):
    try:
        length = float(len(seq))
    except TypeError:  # must be a generator
        return average(list(seq))
    if length == 0:
        return 0.0
    total = 0.0
    for element in seq:
        try:
            total += element
        except TypeError:
            raise Exception("can't add this to a float: {0}".format(
                repr(element)))
    return total / length
    # return sum(seq) / float(len(seq))

def my_max(seq, default=0.0):
    try:
        return max(seq)
    except ValueError:
        return default

def min_jaccard(seq1, seq2, log=False):
    set1, set2 = map(set, (seq1, seq2))
    shorter_length = min(len(set1), len(set2))
    intersection = set1 & set2
    if not intersection:
        return 0
    else:
        sim = float(len(intersection)) / shorter_length
        if log:
            logging.info(u'set1: {0}, set2: {1}'.format(set1, set2))
            logging.info(u'shared: {0}'.format(intersection))
            logging.info('sim: {0}'.format(sim))
        return sim

def jaccard(seq1, seq2, log=False):
    set1, set2 = map(set, (seq1, seq2))
    union = set1 | set2
    intersection = set1 & set2
    if not intersection:
        return 0
    else:
        sim = float(len(intersection)) / len(union)
        if log:
            logging.info(u'set1: {0}, set2: {1}'.format(set1, set2))
            logging.info(u'shared: {0}'.format(intersection))
            logging.info('sim: {0}'.format(sim))
        return sim
