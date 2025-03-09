import networkx as nx
from consts import vehicle_counts

coordinates = {
    "A": (133, 0), "B": (500, 0), "C": (844, 0), "D": (133, 128), "E": (500, 128),
    "F": (844, 128), "G": (844, 257), "H": (1000, 257), "I": (0, 257), "J": (133, 257),
    "K": (133, 400), "L": (272, 400), "M": (272, 257), "N": (598, 257), "O": (598, 533),
    "P": (844, 533), "Q": (1000, 533), "R": (0, 533), "S": (133, 533), "T": (418, 400),
    "U": (418, 661), "V": (0, 661), "W": (0, 839), "X": (133, 839), "Y": (133, 911),
    "Z": (418, 911), "AA": (133, 1000), "BB": (500, 1000), "CC": (500, 911),
    "DD": (598, 911), "EE": (844, 911), "FF": (844, 1000), "GG": (844, 839),
    "HH": (844, 661), "II": (1000, 661), "JJ": (1000, 839)
}

adjlist = {
    'A': ['D'], 'B': ['E'], 'C': ['F'], 'D': ['A', 'E', 'J'], 'E': ['D', 'F', 'B'],
    'F': ['C', 'E', 'G'], 'G': ['F', 'H', 'P'], 'H': ['G'], 'I': ['J'], 'J': ['I', 'D', 'K'],
    'K': ['J', 'L', 'S'], 'L': ['K', 'M', 'T'], 'M': ['N', 'L'], 'N': ['M', 'O'],
    'O': ['N', 'P', 'DD'], 'P': ['G', 'Q', 'O'], 'Q': ['P'], 'R': ['S'], 'S': ['K', 'R'],
    'T': ['L', 'U'], 'U': ['T', 'V', 'Z'], 'V': ['U'], 'W': ['X'], 'X': ['W', 'Y'],
    'Y': ['X', 'Z', 'AA'], 'Z': ['CC', 'U', 'Y'], 'AA': ['Y'], 'BB': ['CC'], 'CC': ['DD', 'Z', 'BB'],
    'DD': ['CC', 'EE'], 'EE': ['GG', 'DD', 'FF'], 'FF': ['EE'], 'GG': ['EE', 'HH', 'JJ'],
    'HH': ['II', 'GG'], 'II': ['HH'], 'JJ': ['GG']
}

def calculate_weight(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    return abs(x1 - x2) + abs(y1 - y2)

def build_graph(adjlist, coordinates):
    graph = nx.Graph()
    for node, neighbors in adjlist.items():
        for neighbor in neighbors:
            weight = calculate_weight(coordinates[node], coordinates[neighbor])
            graph.add_edge(node, neighbor, weight=weight)
    return graph

def shortest_coord(source='A', destination='AA'):
    road_graph = build_graph(adjlist, coordinates)
    
    def dynamic_weight(u, v, d):
        edge = tuple(sorted((u, v)))
        num_vehicles = vehicle_counts[edge]
        distance = d['weight']
        alpha = 3
        return distance * (1 + alpha * num_vehicles)
    
    shortest_path_nodes = nx.shortest_path(road_graph, source, destination, weight=dynamic_weight)
    shortest_path_coords = [coordinates[node] for node in shortest_path_nodes]
    print("Shortest path:", shortest_path_nodes)
    return shortest_path_nodes, shortest_path_coords