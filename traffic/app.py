import pygame
import random
from sys import exit
import city_graph as ts
import utility_func as utility_func

pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Traffic")

# Load images
city_surface = pygame.image.load("traffic/images/city.jpg").convert()
vehicle_surface = pygame.image.load("traffic/images/redcar.png").convert_alpha()

# Transform images
city_surface = pygame.transform.scale(city_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
vehicle_surface = pygame.transform.scale(vehicle_surface, (40, 40))

# List to store active vehicles
vehicles = []
spawn_timer = 0  # Timer for controlling vehicle spawn interval
SPAWN_INTERVAL = 2000  # 2 seconds

class Vehicle:
    def __init__(self, path, image):
        # Store the original unshifted path
        self.original_path = path[:]  
        # Create a shifted path for lane driving
        self.path = self.shift_path(path)
        self.show_path = False
        self.facing = 'F'
        self.path_color = str(random.choice(['red','blue','green','cyan','yellow','purple']))
        self.current_index = 0
        self.original_surface = image
        self.surface = image.copy()
        self.x, self.y = self.path[0]
        #self.original_x,self.original_y = self.original_path
        self.rect = self.surface.get_rect(center=(self.x, self.y))
        
        # Set initial rotation based on the first movement direction using the original path
        if len(self.original_path) > 1:
            self.set_initial_direction(self.original_path[0], self.original_path[1])
        
        print("Before path", self.original_path)
        print("After shifted path", self.path)

    def compute_offset_vector(self,A, B, offset=10):
        """
        Given two points A and B (assumed to form an axis-aligned segment),
        return the offset vector that shifts the segment to the left lane.
        
        For vertical segments:
        - Moving downward (increasing y): left is east, so offset = (offset, 0)
        - Moving upward: left is west, so offset = (-offset, 0)
        
        For horizontal segments:
        - Moving right (increasing x): left is north, so offset = (0, -offset)
        - Moving left: left is south, so offset = (0, offset)
        """
        ax, ay = A
        bx, by = B
        if ax == bx:  # vertical segment
            if by > ay:  # moving downward
                return (offset, 0)
            else:         # moving upward
                return (-offset, 0)
        elif ay == by:  # horizontal segment
            if bx > ax:  # moving right
                return (0, -offset)
            else:         # moving left
                return (0, offset)
        else:
            # For non-axis-aligned segments, you may need a more general solution.
            return (0, 0)

    def shift_path(self,path, offset=10):
        """
        Given a centerline path (a list of coordinate tuples), compute a new path
        for the left lane.
        
        For the first and last nodes, simply shift by the offset of the first/last segment.
        For intermediate nodes (junctions), compute the shifted coordinate as the intersection
        of the offset lines of the incoming and outgoing segments.
        """
        n = len(path)
        if n == 0:
            return []
        
        new_path = []
        
        # First node: shift using the first segment's offset.
        if n > 1:
            v = self.compute_offset_vector(path[0], path[1], offset)
            new_path.append((path[0][0] + v[0], path[0][1] + v[1]))
        else:
            new_path.append(path[0])
        
        # Intermediate nodes:
        for i in range(1, n - 1):
            A = path[i - 1]
            B = path[i]
            C = path[i + 1]
            # Compute the offset vector for the segment before and after the node.
            v_in = self.compute_offset_vector(A, B, offset)
            v_out = self.compute_offset_vector(B, C, offset)
            
            # If the segments are collinear, they should have the same offset.
            if (A[0] == B[0] and B[0] == C[0]) or (A[1] == B[1] and B[1] == C[1]):
                new_B = (B[0] + v_in[0], B[1] + v_in[1])
            else:
                # For perpendicular segments, use the incoming offset for the x-coordinate
                # and the outgoing offset for the y-coordinate.
                new_B = (B[0] + v_in[0], B[1] + v_out[1])
            new_path.append(new_B)
        
        # Last node: shift using the last segment's offset.
        if n > 1:
            v = self.compute_offset_vector(path[-2], path[-1], offset)
            new_path.append((path[-1][0] + v[0], path[-1][1] + v[1]))
        else:
            new_path.append(path[-1])
        
        return new_path

    def set_initial_direction(self, start, next_pos):
        """Set initial rotation based on first movement direction using the original path."""
        start_x, start_y = start
        next_x, next_y = next_pos

        if next_x > start_x:  # Moving right
            angle = -90
            self.facing = 'R'
        elif next_x < start_x:  # Moving left
            angle = 90
            self.facing = 'L'
        elif next_y > start_y:  # Moving down
            angle = 180
            self.facing = 'D'
        else:  # Moving up (default)
            angle = 0
            self.facing = 'U'

        self.surface = pygame.transform.rotate(self.original_surface, angle)
        self.rect = self.surface.get_rect(center=self.rect.center)

    def update_position(self):
        target_x, target_y = self.path[self.current_index + 1]
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery

        if abs(dx) > 0:
            self.rect.centerx += 1 if dx > 0 else -1
        elif abs(dy) > 0:
            self.rect.centery += 1 if dy > 0 else -1

        if (self.rect.centerx, self.rect.centery) == (target_x, target_y):
            self.current_index += 1  # Move to next waypoint
            
            # Use the original path to determine if a rotation is needed.
            if self.current_index < len(self.original_path) - 1:
                # Only rotate if the direction truly changes.
                if self.current_index > 0:
                    prev = self.original_path[self.current_index - 1]
                    curr = self.original_path[self.current_index]
                    nxt = self.original_path[self.current_index + 1]

                    current_dir = (curr[0] - prev[0], curr[1] - prev[1])
                    next_dir = (nxt[0] - curr[0], nxt[1] - curr[1])

                    if current_dir != next_dir:
                        self.rotate_vehicle(curr, nxt)
                else:
                    self.rotate_vehicle(self.original_path[self.current_index],
                                        self.original_path[self.current_index + 1])

    def rotate_vehicle(self, current_point, next_point):
        """Rotate based on the vector from current_point to next_point."""
        current_x, current_y = current_point
        next_x, next_y = next_point

        if next_x > current_x:  # rightward
            angle = -90
            new_facing = 'R'
        elif next_x < current_x:  # leftward
            angle = 90
            new_facing = 'L'
        elif next_y > current_y:  # downward
            angle = 180
            new_facing = 'D'
        else:  # upward
            angle = 0
            new_facing = 'U'

        # Only rotate if the facing direction changes.
        if new_facing != self.facing:
            self.surface = pygame.transform.rotate(self.original_surface, angle)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.facing = new_facing

    def has_reached_destination(self):
        return self.current_index >= len(self.path) - 1

    def draw(self, screen):
        if self.show_path:
            for i in range(0, len(self.path) - 1):

                # pygame.draw.line(
                #     surface=screen,
                #     color=self.path_color,
                #     start_pos=(self.rect.centerx, self.rect.centery),
                #     end_pos=self.original_path[self.current_index + 1],
                #     width=10)
                
                pygame.draw.line(
                    surface=screen,
                    color=self.path_color,
                    start_pos=self.original_path[i],
                    end_pos=self.original_path[i +1],
                    width=8)
                
        screen.blit(self.surface, self.rect)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)




def spawn_vehicle():
    """Spawn a vehicle with a random source & destination (only edge nodes)."""
    global vehicles,vehicle_surface
    source, destination = utility_func.random_spawn_edge()
    path = ts.shortest_coord(source=source, destination=destination)
    


    if path:
        new_vehicle = Vehicle(path,vehicle_surface)
        vehicles.append(new_vehicle)


while True:
    screen.blit(city_surface, (0, 0))

    # Handle vehicle spawning at intervals
    current_time = pygame.time.get_ticks()
    if current_time - spawn_timer > SPAWN_INTERVAL:
        spawn_vehicle()
        spawn_timer = current_time  # Reset spawn timer

    # Update & draw vehicles
    for vehicle in vehicles[:]:  # Iterate over a copy of the list to allow removal
        vehicle.update_position()

        if vehicle.has_reached_destination():
            vehicles.remove(vehicle)  # Remove vehicle when it reaches destination
        else:
            vehicle.draw(screen)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.MOUSEMOTION:
            #print(pygame.mouse.get_pos())
            pass

        if event.type == pygame.MOUSEBUTTONDOWN:
            for vehicle in vehicles[:]:
                if vehicle.check_click(event.pos):
                    print("Clicked")
                    vehicle.show_path= not vehicle.show_path


    pygame.display.update()
    clock.tick(144)
