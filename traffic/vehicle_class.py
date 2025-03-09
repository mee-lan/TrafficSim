import random
import pygame
from city_graph import shortest_coord

vehicles = []
my_vehicle = []
vehicle_id_counter = 0

class Vehicle:
    def __init__(self, node_path, coord_path, image):
        global vehicle_id_counter
        self.id = vehicle_id_counter
        vehicle_id_counter += 1
        self.node_path = node_path[:]  # List of intersection nodes (e.g., ['A', 'D', 'J'])
        self.original_path = coord_path[:]  # List of coordinates
        self.path = self.shift_path(coord_path)
        self.show_path = False
        self.facing = 'F'
        self.speed = 1.2
        self.collideflag = False
        self.pushback_active = False
        self.pushback_distance = 0
        self.pushback_speed = 1.2
        self.path_color = random.choice(['green', 'yellow', 'orange'])
        self.current_index = 0
        self.old_rect = None
        self.original_surface = image
        self.surface = image.copy()
        self.x, self.y = self.path[0]
        self.lookahead_rect = self.surface.get_rect(center=(self.x, self.y))
        self.rect = self.surface.get_rect(center=(self.x, self.y))
        
        if len(self.original_path) > 1:
            self.set_initial_direction(self.original_path[0], self.original_path[1])

    def get_current_edge(self):
        """Return the current undirected edge the vehicle is on."""
        if self.current_index < len(self.node_path) - 1:
            node1 = self.node_path[self.current_index]
            node2 = self.node_path[self.current_index + 1]
            return tuple(sorted((node1, node2)))
        return None

    def check_ahead(self, safety_distance):
        if self.facing == 'R':
            self.lookahead_rect = pygame.Rect(self.rect.centerx, self.rect.top + 6,  
                                        safety_distance, self.rect.height - 20) 
        elif self.facing == 'L':
            self.lookahead_rect = pygame.Rect(self.rect.centerx - safety_distance,
                                        self.rect.top + 6, safety_distance, self.rect.height - 20)
        elif self.facing == 'U':
            self.lookahead_rect = pygame.Rect(self.rect.left + 6, self.rect.centery - safety_distance,
                                        self.rect.width - 20, safety_distance)
        elif self.facing == 'D':
            self.lookahead_rect = pygame.Rect(self.rect.left + 6, self.rect.centery,
                                        self.rect.width - 20, safety_distance)
        else:
            self.lookahead_rect = self.rect.copy()

    def compute_offset_vector(self, A, B, offset=12):
        ax, ay = A
        bx, by = B
        if ax == bx:
            if by > ay:
                return (offset, 0)
            else:
                return (-offset, 0)
        elif ay == by:
            if bx > ax:
                return (0, -offset)
            else:
                return (0, offset)
        else:
            return (0, 0)

    def shift_path(self, path, offset=18):
        n = len(path)
        if n == 0:
            return []
        
        new_path = []
        if n > 1:
            v = self.compute_offset_vector(path[0], path[1], offset)
            new_path.append((path[0][0] + v[0], path[0][1] + v[1]))
        else:
            new_path.append(path[0])
        
        for i in range(1, n - 1):
            A = path[i - 1]
            B = path[i]
            C = path[i + 1]
            v_in = self.compute_offset_vector(A, B, offset)
            v_out = self.compute_offset_vector(B, C, offset)
            if (A[0] == B[0] and B[0] == C[0]) or (A[1] == B[1] and B[1] == C[1]):
                new_B = (B[0] + v_in[0], B[1] + v_in[1])
            else:
                new_B = (B[0] + v_in[0], B[1] + v_out[1])
            new_path.append(new_B)
        
        if n > 1:
            v = self.compute_offset_vector(path[-2], path[-1], offset)
            new_path.append((path[-1][0] + v[0], path[-1][1] + v[1]))
        else:
            new_path.append(path[-1])
        
        return new_path

    def set_initial_direction(self, start, next_pos):
        start_x, start_y = start
        next_x, next_y = next_pos
        if next_x > start_x:
            angle = -90
            self.facing = 'R'
        elif next_x < start_x:
            angle = 90
            self.facing = 'L'
        elif next_y > start_y:
            angle = 180
            self.facing = 'D'
        else:
            angle = 0
            self.facing = 'U'
        self.surface = pygame.transform.rotate(self.original_surface, angle)
        self.rect = self.surface.get_rect(center=self.rect.center)

    def start_pushback(self, max_distance=5):
        self.pushback_active = True
        self.pushback_distance = max_distance
        self.speed = 0
        self.collideflag = True
        print(f"Vehicle {self.id} at {self.rect.center} started pushback")

    def update_pushback(self):
        if self.pushback_active and self.pushback_distance > 0:
            push_step = min(self.pushback_speed, self.pushback_distance)
            if self.facing == 'R':
                self.rect.centerx -= push_step
            elif self.facing == 'L':
                self.rect.centerx += push_step
            elif self.facing == 'U':
                self.rect.centery += push_step
            elif self.facing == 'D':
                self.rect.centery -= push_step
            self.pushback_distance -= push_step
            if self.pushback_distance <= 0:
                self.pushback_active = False
                print(f"Vehicle {self.id} at {self.rect.center} completed pushback")

    def checkcollission(self):
        self.check_ahead(100)
        collision_detected = False
        all_vehicles = my_vehicle + vehicles
        
        for vehicle in all_vehicles:
            if vehicle is not self:
                if self.lookahead_rect.colliderect(vehicle.rect):
                    collision_detected = True
                    if self.rect.colliderect(vehicle.rect):
                        if self.id < vehicle.id and not self.pushback_active:
                            self.start_pushback(max_distance=8)
                    else:
                        if self.id < vehicle.id and not self.pushback_active:
                            self.speed = 0
                            self.collideflag = True
                            print(f"Vehicle {self.id} at {self.rect.center} stopped due to near collision with Vehicle {vehicle.id}")
        
        if not collision_detected and self.collideflag and not self.pushback_active:
            self.speed = 1.2
            self.collideflag = False
            print(f"Vehicle {self.id} at {self.rect.center} resumed movement")

    def update_position(self):
        self.checkcollission()
        if self.pushback_active:
            self.update_pushback()
        elif self.speed > 0:
            if self.current_index < len(self.path) - 1:
                target_x, target_y = self.path[self.current_index + 1]
                dx = target_x - self.rect.centerx
                dy = target_y - self.rect.centery
                if abs(dx) <= self.speed and abs(dy) <= self.speed:
                    # Reached the target point (intersection)
                    self.rect.centerx, self.rect.centery = target_x, target_y
                    self.current_index += 1
                    if self.current_index < len(self.node_path) - 1:
                        # Recalculate path from current node to destination
                        current_node = self.node_path[self.current_index]
                        destination = self.node_path[-1]
                        new_node_path, new_coord_path = shortest_coord(source=current_node, destination=destination)
                        if new_node_path:
                            self.node_path = new_node_path
                            self.original_path = new_coord_path
                            self.path = self.shift_path(new_coord_path)
                            self.current_index = 0  # Reset to start of new path
                            self.rotate_vehicle(self.original_path[0], self.original_path[1])
                else:
                    # Move towards the target
                    if abs(dx) > self.speed:
                        self.rect.centerx += self.speed if dx > 0 else -self.speed
                    elif abs(dy) > self.speed:
                        self.rect.centery += self.speed if dy > 0 else -self.speed

    def rotate_vehicle(self, current_point, next_point):
        current_x, current_y = current_point
        next_x, next_y = next_point
        if next_x > current_x:
            angle = -90
            new_facing = 'R'
        elif next_x < current_x:
            angle = 90
            new_facing = 'L'
        elif next_y > current_y:
            angle = 180
            new_facing = 'D'
        else:
            angle = 0
            new_facing = 'U'
        if new_facing != self.facing:
            self.surface = pygame.transform.rotate(self.original_surface, angle)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.facing = new_facing

    def has_reached_destination(self):
        return self.current_index >= len(self.path) - 1

    def draw(self, screen):
        if self.show_path:
            for i in range(self.current_index, len(self.path) - 2):
                if self.facing == 'U':
                    centerx = self.rect.centerx + 12
                    centery = self.rect.centery - 22
                elif self.facing == 'D':
                    centerx = self.rect.centerx - 12
                    centery = self.rect.centery + 22
                elif self.facing == 'L':
                    centerx = self.rect.centerx - 22
                    centery = self.rect.centery - 12
                elif self.facing == 'R':
                    centerx = self.rect.centerx + 22
                    centery = self.rect.centery + 12

                pygame.draw.circle(screen, self.path_color, (centerx, centery), 6, 20)
                pygame.draw.line(screen, self.path_color, (centerx, centery),
                                self.original_path[self.current_index + 1], 12)
                pygame.draw.line(screen, self.path_color, self.original_path[i + 1],
                                self.original_path[i + 2], 10)
               # pygame.draw.rect(screen,'red',self.lookahead_rect)

        screen.blit(self.surface, self.rect)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)