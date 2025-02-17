import networkx as nx

def calculate_weight(coord1, coord2):
    #Calculate  distance between two coordinates on basis of x and y axes
    x1, y1 = coord1
    x2, y2 = coord2
    return abs(x1 - x2) + abs(y1 - y2)

def build_graph(adjlist, coordinates):
    #To construct a weighted graph using adjacency list and coordinates.
    graph = nx.Graph()

    for node, neighbors in adjlist.items():
        for neighbor in neighbors:
            weight = calculate_weight(coordinates[node], coordinates[neighbor])
            graph.add_edge(node, neighbor, weight=weight)
    return graph

def adjust_lane_coordinates(path, coordinates):
    """Adjusts coordinates to maintain lane separation in movement."""
    adjusted_coords = []
    
    for i in range(len(path) - 1):
        node = path[i]
        next_node = path[i + 1]

        x, y = coordinates[node]
        next_x, next_y = coordinates[next_node]

        if x > next_x and y == next_y:  # Moving left
            adjusted_coords.append((x, y + 10))
        elif x < next_x and y == next_y:  # Moving right
            adjusted_coords.append((x, y - 10))
        elif x == next_x and y > next_y:  # Moving up
            adjusted_coords.append((x + 10, y))
        elif x == next_x and y < next_y:  # Moving down
            adjusted_coords.append((x - 10, y))

    return adjusted_coords

def shortest_coord(source='A', destination='AA'):
    """Finds the shortest path and applies lane adjustments."""
    coord=[]
    coordinates = {
        "A": (120, 0), "B": (450, 0), "C": (760, 0), "D": (120, 115), "E": (450, 115),
        "F": (760, 115), "G": (760, 232), "H": (900, 232), "I": (0, 232), "J": (120, 232),
        "K": (120, 360), "L": (245, 360), "M": (245, 232), "N": (538, 232), "O": (538, 480),
        "P": (760, 480), "Q": (900, 480), "R": (0, 480), "S": (120, 480), "T": (377, 360),
        "U": (377, 595), "V": (0, 595), "W": (0, 755), "X": (120, 755), "Y": (120, 820),
        "Z": (377, 820), "AA": (120, 900), "BB": (450, 900), "CC": (450, 820), "DD": (538, 820),
        "EE": (760, 820), "FF": (760, 900), "GG": (760, 755), "HH": (760, 595), "II": (900, 595),
        "JJ": (900, 755)
    }

    # Adjacency list
    adjlist = {
        'A': ['D'], 'B': ['E'], 'C': ['F'], 'D': ['A', 'E', 'J'], 'E': ['D', 'F', 'B'],
        'F': ['C', 'E', 'G'], 'G': ['F', 'H', 'P'], 'H': ['G'], 'I': ['J'], 'J': ['I', 'D', 'K'],
        'K': ['J', 'L', 'S'], 'L': ['K', 'M', 'T'], 'M': ['N', 'L'], 'N': ['M', 'O'],
        'O': ['N', 'P', 'DD'], 'P': ['G', 'Q', 'O'], 'Q': ['P'], 'R': ['S'], 'S': ['K', 'R'],
        'T': ['L', 'U'], 'U': ['T', 'V', 'Z'], 'V': ['U'], 'W': ['X'], 'X': ['W', 'Y'],
        'Y': ['X', 'Z', 'AA'], 'Z': ['CC', 'U', 'Y'], 'AA': ['Y'], 'BB': ['CC'], 'CC': ['DD','Z','BB'],
        'DD': ['CC', 'EE'], 'EE': ['GG', 'DD', 'FF'], 'FF': ['EE'], 'GG': ['EE', 'HH', 'JJ'],
        'HH': ['II', 'GG'], 'II': ['HH'], 'JJ': ['GG']
    }

    # Build the graph
    road_graph = build_graph(adjlist, coordinates)

    # Compute the shortest path
    shortest_path = nx.shortest_path(road_graph, source, destination, weight="weight")
    print("Shortest path:", shortest_path)

    for node in shortest_path:
        coord.append(coordinates[node])

    return coord

print(shortest_coord())

# Example usage
# shortest_coord('A', 'DD')
