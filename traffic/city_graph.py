
import heapq
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
    graph = {}
    for node in adjlist:
        graph[node] = {}
        for neighbor in adjlist[node]:
            weight = calculate_weight(coordinates[node], coordinates[neighbor])
            graph[node][neighbor] = weight
    return graph

def dynamic_weight(u, v, base_weight):
    edge = tuple(sorted((u, v)))  # Undirected edge, sorted for consistency
    num_vehicles = vehicle_counts.get(edge, 0)
    alpha = 2  # Congestion factor
    return base_weight * (1 + alpha * num_vehicles)

def dijkstra(graph, source, destination):
    """
    Custom Dijkstra's algorithm to find the shortest path between source and destination.
    Returns the shortest path as a list of nodes.
    """
    # Initialize distances with infinity for all nodes except source
    distances = {node: float('inf') for node in graph}
    distances[source] = 0
    
    # Previous node in the shortest path
    previous = {node: None for node in graph}
    
    # Priority queue to store (distance, node)
    pq = [(0, source)]
    
    # Set to keep track of visited nodes
    visited = set()
    
    while pq:
        # Get the node with the smallest distance
        current_distance, current_node = heapq.heappop(pq)
        
        # If we've reached the destination, reconstruct and return the path
        if current_node == destination:
            path = []
            while current_node:
                path.append(current_node)
                current_node = previous[current_node]
            return path[::-1]  # Reverse to get path from source to destination
        
        # Skip if already visited
        if current_node in visited:
            continue
        
        # Mark as visited
        visited.add(current_node)
        
        # Explore neighbors
        for neighbor, base_weight in graph[current_node].items():
            if neighbor in visited:
                continue
            
            # Calculate dynamic weight considering congestion
            weight = dynamic_weight(current_node, neighbor, base_weight)
            distance = current_distance + weight
            
            # If we found a shorter path, update it
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    # If destination is unreachable
    return None

def shortest_coord(source='A', destination='AA'):
    graph = build_graph(adjlist, coordinates)
    shortest_path_nodes = dijkstra(graph, source, destination)
    
    if shortest_path_nodes:
        shortest_path_coords = [coordinates[node] for node in shortest_path_nodes]
        print("Shortest path:", shortest_path_nodes)
        return shortest_path_nodes, shortest_path_coords
    else:
        print(f"No path found from {source} to {destination}")
        return [], []
    
