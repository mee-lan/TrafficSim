#This one is for generating random source and destination nodes to spawn vehicles randomly
import random
from city_graph import shortest_coord
from consts import red_car_surface,truck_surface,race_car_surface
from vehicle_class import Vehicle,my_vehicle,vehicle_id_counter,vehicles

adjlist = {
    'A': ['D'], 'B': ['E'], 'C': ['F'], 'D': ['A', 'E', 'J'], 'E': ['D', 'F', 'B'],
    'F': ['C', 'E', 'G'], 'G': ['F', 'H', 'P'], 'H': ['G'], 'I': ['J'], 'J': ['I', 'D', 'K'],
    'K': ['J', 'L', 'S'], 'L': ['K', 'M', 'T'], 'M': ['N', 'L'], 'N': ['M', 'O'],
    'O': ['N', 'P', 'DD'], 'P': ['G', 'Q', 'O'], 'Q': ['P'], 'R': ['S'], 'S': ['K', 'R'],
    'T': ['L', 'U'], 'U': ['T', 'V', 'Z'], 'V': ['U'], 'W': ['X'], 'X': ['W', 'Y'],
    'Y': ['X', 'Z', 'AA'], 'Z': ['CC', 'U', 'Y'], 'AA': ['Y'], 'BB': ['CC'], 'CC': ['DD','Z'],
    'DD': ['CC', 'EE'], 'EE': ['GG', 'DD', 'FF'], 'FF': ['EE'], 'GG': ['EE', 'HH', 'JJ'],
    'HH': ['II', 'GG'], 'II': ['HH'], 'JJ': ['GG']
}

# **Precompute edge nodes**
#only choose edge nodes -> bich dekhi randomly spawn vayo vane hawa dekhinxa
edge_nodes = [node for node in adjlist if len(adjlist[node]) == 1] # len == 1 meaning it is (edge node) so that vehicle doesn't spawn in (between of the city) and only from corner where node is connected to only one edge i.e len==1

def random_spawn_edge():
    #random selection of source & destination from precomputed edge nodes."""
    return random.sample(edge_nodes, 2)  # Pick two different edge nodes

def spawn_vehicle(source='NULL', destination='NULL'):
    global vehicles
    is_user_defined = False

    if source == 'NULL' and destination == 'NULL':
        is_user_defined = True
        source, destination = random_spawn_edge()

    path = shortest_coord(source=source, destination=destination)

    if path:
        vehicle = random.choice([red_car_surface, truck_surface, race_car_surface])
        new_vehicle = Vehicle(path, vehicle)

        if is_user_defined:
            my_vehicle.append(new_vehicle)
        else:
            new_vehicle.show_path = True
            vehicles.append(new_vehicle)

