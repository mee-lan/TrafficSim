import networkx as nx
from consts import vehicle_counts

coordinates = {
    "A": (144, 0), "B": (540, 0), "C": (912, 0), "D": (144, 138), "E": (540, 138),
    "F": (912, 138), "G": (912, 278), "H": (1080, 278), "I": (0, 278), "J": (144, 278),
    "K": (144, 432), "L": (294, 432), "M": (294, 278), "N": (646, 278), "O": (646, 576),
    "P": (912, 576), "Q": (1080, 576), "R": (0, 576), "S": (144, 576), "T": (452, 432),
    "U": (452, 714), "V": (0, 714), "W": (0, 906), "X": (144, 906), "Y": (144, 984),
    "Z": (452, 984), "AA": (144, 1080), "BB": (540, 1080), "CC": (540, 984),
    "DD": (646, 984), "EE": (912, 984), "FF": (912, 1080), "GG": (912, 906),
    "HH": (912, 714), "II": (1080, 714), "JJ": (1080, 906)
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
        edge = tuple(sorted((u, v)))  # Undirected edge, so sort for consistency
        num_vehicles = vehicle_counts[edge]
        distance = d['weight']  # Static Manhattan distance
        alpha = 1.5  # Congestion factor; adjust as needed
        return distance * (1 + alpha * num_vehicles)
    
    shortest_path_nodes = nx.shortest_path(road_graph, source, destination, weight=dynamic_weight)
    shortest_path_coords = [coordinates[node] for node in shortest_path_nodes]
    print("Shortest path:", shortest_path_nodes)
    return shortest_path_nodes, shortest_path_coords