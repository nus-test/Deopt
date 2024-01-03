from collections import defaultdict
from copy import deepcopy
import networkx as nx
import queue

# class PrecedenceGraph:
class DependenceGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

        self.cycle_node_base_number = 10000
        self.negative_edges = list()

    def add_node(self, node_id):
        self.graph.add_node(node_id)

    # each edge means u will influence v
    def add_edge(self, source, dest):
        self.graph.add_edge(source, dest)

    def add_negative_edge(self, source, dest):
        self.negative_edges.append((source, dest))

    def is_node_in_circle(self, query_node):
        cycles = list(nx.recursive_simple_cycles(self.graph))
        for cycle in cycles:
            if query_node in cycle:
                return True
        return False

    def get_all_influenced_node(self, query_node, result = None):
        if result == None:
            result = list()
        if query_node in result:
            return []
        result.append(query_node)
        for child in list(self.graph.successors(query_node)):
            if not child in result:
                self.get_all_influenced_node(child, result)

        return deepcopy(result)

    def get_the_closure_cycle_nodes(self, graph, query_node):
        def inter(a, b):
            return list(set(a) & set(b))
        if self.is_node_in_circle(query_node):
            cycles = list(nx.recursive_simple_cycles(graph))
            result = []
            for cycle in cycles:
                if query_node in cycle:
                    result.extend(cycle)
            for cycle in cycles:
                if inter(cycle, result):
                    result.extend(cycle)
            return list(set(result))
        else:
            return []

    def get_precedence_graph_of_query_node(self, query_node):
        all_influenced_node = self.get_all_influenced_node(query_node)
        subgraph = self.graph.subgraph(all_influenced_node)
        acyclic_subgraph = nx.DiGraph(subgraph)
        
        cycle_node_map = defaultdict(set)

        entry_node = query_node

        cycles = list(nx.simple_cycles(acyclic_subgraph))
        while len(cycles) > 0:
            new_node_number = self.cycle_node_base_number + len(cycle_node_map)
            cycle_node_map[new_node_number].update(set(cycles[0]))
            for node in cycles[0]:
                new_edges = []
                for edge in list(acyclic_subgraph.in_edges(node)):
                    if edge[0] not in cycles[0]:
                        new_edges.append((edge[0], new_node_number))
                        # acyclic_subgraph.add_edge(edge[0], new_node_number)
                for edge in list(acyclic_subgraph.out_edges(node)):
                    if edge[1] not in cycles[0]:
                        new_edges.append((new_node_number, edge[1]))
                        # acyclic_subgraph.add_edge(new_node_number, edge[1])
                for edge in new_edges:
                    acyclic_subgraph.add_edge(edge[0], edge[1])
                acyclic_subgraph.remove_node(node)
            if not acyclic_subgraph.has_node(new_node_number):
                acyclic_subgraph.add_node(new_node_number)
            if entry_node in cycles[0]:
                entry_node = new_node_number
            cycles = list(nx.simple_cycles(acyclic_subgraph))
        
        node_layers = defaultdict(int)
        node_layers[entry_node] = 0
        
        # BFS
        bfs_queue = queue.Queue()
        for child in acyclic_subgraph.successors(entry_node):
            bfs_queue.put(child)
        while not bfs_queue.empty():
            current_node = bfs_queue.get()
            parent_layer = -1
            for parent in acyclic_subgraph.predecessors(current_node):
                if not parent in node_layers:
                    parent_layer = -1
                    break
                else:
                    if parent_layer < node_layers[parent]:
                        parent_layer = node_layers[parent]
            if parent_layer == -1:
                bfs_queue.put(current_node)
            else:
                node_layers[current_node] = parent_layer + 1
                for child in acyclic_subgraph.successors(current_node):
                    bfs_queue.put(child)

        max_layer = -1
        for key in node_layers.keys():
            max_layer = max(max_layer, node_layers[key])

        layer_result = []
        for i in range(max_layer +1):
            layer_result.append([])

        for key in node_layers.keys():
            layer_result[node_layers[key]].append(key)

        return layer_result, cycle_node_map, all_influenced_node

    def get_precedence_graph_of_whole_graph(self):
        acyclic_subgraph = nx.DiGraph(self.graph)
        entry_node = 0
        cycle_node_map = defaultdict(set)

        cycles = list(nx.simple_cycles(acyclic_subgraph))
        while len(cycles) > 0:
            new_node_number = self.cycle_node_base_number + len(cycle_node_map)
            cycle_node_map[new_node_number].update(set(cycles[0]))
            for node in cycles[0]:
                new_edges = []
                for edge in list(acyclic_subgraph.in_edges(node)):
                    if edge[0] not in cycles[0]:
                        new_edges.append((edge[0], new_node_number))
                        # acyclic_subgraph.add_edge(edge[0], new_node_number)
                for edge in list(acyclic_subgraph.out_edges(node)):
                    if edge[1] not in cycles[0]:
                        new_edges.append((new_node_number, edge[1]))
                        # acyclic_subgraph.add_edge(new_node_number, edge[1])
                for edge in new_edges:
                    acyclic_subgraph.add_edge(edge[0], edge[1])
                acyclic_subgraph.remove_node(node)
            if not acyclic_subgraph.has_node(new_node_number):
                acyclic_subgraph.add_node(new_node_number)
            if entry_node in cycles[0]:
                entry_node = new_node_number
            cycles = list(nx.simple_cycles(acyclic_subgraph))
        
        node_layers = defaultdict(int)
        
        # BFS
        bfs_queue = queue.Queue()
        for node, in_degree in acyclic_subgraph.in_degree():
            if in_degree == 0:
                bfs_queue.put(node)
                node_layers[node] = 0
        if bfs_queue.empty():
            bfs_queue.put(entry_node)
            node_layers[entry_node] = 0
        while not bfs_queue.empty():
            current_node = bfs_queue.get()
            parent_layer = -1
            if current_node in node_layers and node_layers[current_node] == 0:
                for child in acyclic_subgraph.successors(current_node):
                    bfs_queue.put(child)
                continue
            for parent in acyclic_subgraph.predecessors(current_node):
                if not parent in node_layers:
                    parent_layer = -1
                    break
                else:
                    if parent_layer < node_layers[parent]:
                        parent_layer = node_layers[parent]
            if parent_layer == -1:
                bfs_queue.put(current_node)
            else:
                node_layers[current_node] = parent_layer + 1
                for child in acyclic_subgraph.successors(current_node):
                    bfs_queue.put(child)

        max_layer = -1
        for key in node_layers.keys():
            max_layer = max(max_layer, node_layers[key])

        layer_result = []
        for i in range(max_layer +1):
            layer_result.append([])

        for key in node_layers.keys():
            layer_result[node_layers[key]].append(key)

        return layer_result, cycle_node_map

    def get_real_value_of_node(self, cycle_node_map, node_number):
            if node_number < self.cycle_node_base_number:
                return [node_number]
            else:
                result = []
                for real_number in cycle_node_map[node_number]:
                    if real_number < self.cycle_node_base_number:
                        result.append(real_number)
                    else:
                        result.extend(self.get_real_value_of_node(cycle_node_map, real_number))
                return result
        
    def get_ignored_facts_list(self, node_layers, current_layer, cycle_node_map):
        result = []
        for layer, nodes in enumerate(node_layers):
            if layer > current_layer:
                for node_number in nodes:
                    result.extend(self.get_real_value_of_node(cycle_node_map, node_number))
        return result

    def contain_negative_edge(self, node_list):
        for edge in self.negative_edges:
            if edge[0] in node_list and edge[1] in node_list:
                return True
        return False

    def get_cycles(self):
        return list(nx.recursive_simple_cycles(self.graph))
    def get_cycles_length(self):
        cycles = self.get_cycles()
        length_list = [len(c) for c in cycles]
        return length_list