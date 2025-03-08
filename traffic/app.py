import pygame
import random
import os
from sys import exit
import math
import city_graph as ts
import utility_func as utility_func
from sound import load_and_play_city_sound, intro_sound, play_selected_sound
from city_graph import coordinates

pygame.init()

SCREEN_WIDTH = 1080  
SCREEN_HEIGHT = 1080  
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Traffic")

# Load font (scale font size from 22 to 26, i.e., 22 * 1.2)
font = pygame.font.Font('traffic/src/fonts/small_pixel.ttf', 26)
TEXT_COL = (255, 255, 255)  # White text color

# Load images
city_surface = pygame.image.load("traffic/src/images/city.jpg").convert()
truck_surface = pygame.image.load("traffic/src/images/truck.png").convert_alpha()
red_car_surface = pygame.image.load("traffic/src/images/redcar.png").convert_alpha()
race_car_surface = pygame.image.load("traffic/src/images/race_car.png").convert_alpha()
location_icon_surface = pygame.image.load("traffic/src/images/location_icon.png").convert_alpha()
menu_bar_surface = pygame.image.load("traffic/src/images/menu_bar.png").convert_alpha()

# Transform images (scale by 1.2)
city_surface = pygame.transform.scale(city_surface, (1080, 1080))  # 900 * 1.2
truck_surface = pygame.transform.scale(truck_surface, (26, 96))    # 22 * 1.2, 80 * 1.2
red_car_surface = pygame.transform.scale(red_car_surface, (22, 72))  # 18 * 1.2, 60 * 1.2
race_car_surface = pygame.transform.scale(race_car_surface, (22, 54))  # 18 * 1.2, 45 * 1.2
location_icon_surface = pygame.transform.scale(location_icon_surface, (60, 60))  # 50 * 1.2
menu_bar_surface = pygame.transform.scale(menu_bar_surface, (60, 60))  # 50 * 1.2

# List to store active vehicles
vehicles = []
my_vehicle = []
collided = []
source = None
destination = None

spawn_timer = 0
text_timer = 0
SPAWN_INTERVAL = 4000  # Remains in milliseconds, no scaling needed
vehicle_id_counter = 0

# Home screen function
def home_screen():
    global text_timer
    running = True
    city_sound = None
    intro_sfx = False

    while running:
        screen.fill((0, 0, 0))
        title_text = font.render("Traffic Simulation", True, TEXT_COL)
        start_text = font.render("Start", True, TEXT_COL)
        quit_text = font.render("Quit", True, TEXT_COL)

        if not intro_sfx:
            intro_sfx = True
            intro_sound()

        if text_timer < 50:
            screen.blit(title_text, (SCREEN_WIDTH//2 - 120, 360))  # 100 * 1.2 = 120, 300 * 1.2 = 360

        elif text_timer == 100:
            text_timer = 0
        
        text_timer += 1
        
        start_rect = pygame.Rect(SCREEN_WIDTH//2 - 78, 480, 180, 60)  # 65*1.2=78, 400*1.2=480, 150*1.2=180, 50*1.2=60
        quit_rect = pygame.Rect(SCREEN_WIDTH//2 - 48, 552, 120, 48)  # 40*1.2=48, 460*1.2=552, 100*1.2=120, 40*1.2=48
        
        pygame.draw.rect(screen, (50, 200, 50), start_rect)
        pygame.draw.rect(screen, (200, 50, 50), quit_rect)
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2 + 12, 492))  # 10*1.2=12, 410*1.2=492
        screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2 + 12, 564))  # 10*1.2=12, 470*1.2=564

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play_selected_sound()
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    if city_sound is None:
                        city_sound = load_and_play_city_sound()
                    running = False
                if quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    exit()

        pygame.display.update()
        clock.tick(100)

home_screen()

def draw_text(text, font, text_col):
    global text_timer
    if text_timer < 50:
        text_surf = font.render(text, True, text_col)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT * 0.03))  # 0.03 * 1080 = 32.4
        screen.blit(text_surf, text_rect)

    text_timer += 1
    if text_timer == 100:
        text_timer = 0

def draw_item(coords):
    loc_rect = location_icon_surface.get_rect(center=coords)
    screen.blit(location_icon_surface, loc_rect.topleft)

class UI:
    def __init__(self, surface, image, x, y):
        self.image = image
        self.surface = surface
        self.x = x
        self.y = y
        self.click_count = 0
        self.draw_location_icon = False
        self.source_coords = (-120, -120)  # -100 * 1.2
        self.source_node = None
        self.destination_node = None
        self.destination_coords = (-120, -120)  # -100 * 1.2
        self.is_menu_bar_open = False
        self.menu_icon_rect = self.surface.get_rect(topleft=(self.x, self.y))

    def render(self):
        screen.blit(self.surface, (self.x, self.y))
        if self.is_menu_bar_open:
            self.show_text()
        if self.draw_location_icon:
            draw_item(self.source_coords)
            draw_item(self.destination_coords)

    def handle_source_destination(self, pos):
        global source, destination
        if self.is_menu_bar_open:
            self.show_text()
        
        if not self.menu_icon_rect.collidepoint(event.pos):
            if self.click_count == 0:
                node = self.find_source_or_destination_node(pos)
                self.source_coords = coordinates[node]
                self.source_node = node
                self.click_count += 1
                self.draw_location_icon = True
            elif self.click_count == 1:
                node = self.find_source_or_destination_node(pos)
                self.destination_coords = coordinates[node]
                self.destination_node = node
                self.click_count = 0
                self.is_menu_bar_open = False
                source = self.source_coords
                destination = self.destination_coords
                spawn_vehicle(self.source_node, self.destination_node)
            else:
                print("some error occurred, clickcount", self.click_count)

            print("user clicked at x,y", pos)

    def find_source_or_destination_node(self, pos):
        min_dist = float('inf')
        nearest = None
        x, y = pos
        for node, (nx, ny) in coordinates.items():
            dist = math.sqrt((x - nx) ** 2 + (y - ny) ** 2)
            if dist < min_dist:
                min_dist = dist
                nearest = node
        return nearest

    def show_text(self):
        draw_text("Select Source And Destination", font, TEXT_COL)

    def reset_state(self):
        self.draw_location_icon = False
        self.source_coords = (-120, 1200)  # -100*1.2, 1000*1.2
        self.destination_coords = (-120, -120)  # -100*1.2
        self.click_count = 0

class Vehicle:
    def __init__(self, path, image):
        global vehicle_id_counter
        self.id = vehicle_id_counter
        vehicle_id_counter += 1
        self.original_path = path[:]
        self.path = self.shift_path(path)
        self.show_path = False
        self.facing = 'F'
        self.speed = 1.2  # 1 * 1.2
        self.collideflag = False
        self.pushback_active = False
        self.pushback_distance = 0
        self.pushback_speed = 1.8  # 1.5 * 1.2
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

    def check_ahead(self, safety_distance):
        if self.facing == 'R':
            self.lookahead_rect = pygame.Rect(self.rect.centerx, self.rect.top + 6,  # 5*1.2
                                        safety_distance, self.rect.height - 12)  # 10*1.2
        elif self.facing == 'L':
            self.lookahead_rect = pygame.Rect(self.rect.centerx - safety_distance,
                                        self.rect.top + 6, safety_distance, self.rect.height - 12)
        elif self.facing == 'U':
            self.lookahead_rect = pygame.Rect(self.rect.left + 6, self.rect.centery - safety_distance,
                                        self.rect.width - 12, safety_distance)
        elif self.facing == 'D':
            self.lookahead_rect = pygame.Rect(self.rect.left + 6, self.rect.centery,
                                        self.rect.width - 12, safety_distance)
        else:
            self.lookahead_rect = self.rect.copy()

    def compute_offset_vector(self, A, B, offset=12):  # offset remains since it’s relative to path
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

    def shift_path(self, path, offset=14):  # 12 * 1.2 = 14.4, rounded to 14
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

    def start_pushback(self, max_distance=12):  # 10 * 1.2 = 12
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
        self.check_ahead(96)  # 80 * 1.2 = 96
        collision_detected = False
        all_vehicles = my_vehicle + vehicles
        
        for vehicle in all_vehicles:
            if vehicle is not self:
                if self.lookahead_rect.colliderect(vehicle.rect):
                    collision_detected = True
                    if self.rect.colliderect(vehicle.rect):
                        if self.id < vehicle.id and not self.pushback_active:
                            self.start_pushback(max_distance=12)  # 10 * 1.2
                    else:
                        if self.id < vehicle.id and not self.pushback_active:
                            self.speed = 0
                            self.collideflag = True
                            print(f"Vehicle {self.id} at {self.rect.center} stopped due to near collision with Vehicle {vehicle.id}")
        
        if not collision_detected and self.collideflag and not self.pushback_active:
            self.speed = 1.2  # 1 * 1.2
            self.collideflag = False
            print(f"Vehicle {self.id} at {self.rect.center} resumed movement")

    def update_position(self):
        self.checkcollission()
        if self.pushback_active:
            self.update_pushback()
        elif self.speed > 0:
            target_x, target_y = self.path[self.current_index + 1]
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            if abs(dx) > self.speed:
                self.rect.centerx += self.speed if dx > 0 else -self.speed
            elif abs(dy) > self.speed:
                self.rect.centery += self.speed if dy > 0 else -self.speed
            else:
                self.rect.centerx, self.rect.centery = target_x, target_y
                self.current_index += 1
                if self.current_index < len(self.original_path) - 1:
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
                    centerx = self.rect.centerx + 12  # 10*1.2
                    centery = self.rect.centery - 22  # 18*1.2
                elif self.facing == 'D':
                    centerx = self.rect.centerx - 12
                    centery = self.rect.centery + 22
                elif self.facing == 'L':
                    centerx = self.rect.centerx - 22
                    centery = self.rect.centery - 12
                elif self.facing == 'R':
                    centerx = self.rect.centerx + 22
                    centery = self.rect.centery + 12

                pygame.draw.circle(screen, self.path_color, (centerx, centery), 6, 20)  # 5*1.2=6
                pygame.draw.line(screen, self.path_color, (centerx, centery),
                                self.original_path[self.current_index + 1], 12)  # 10*1.2
                pygame.draw.line(screen, self.path_color, self.original_path[i + 1],
                                self.original_path[i + 2], 10)  # 8*1.2=9.6, rounded to 10
        screen.blit(self.surface, self.rect)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

def spawn_vehicle(source='NULL', destination='NULL'):
    global vehicles
    is_user_defined = False
    if source == 'NULL' and destination == 'NULL':
        is_user_defined = True
        source, destination = utility_func.random_spawn_edge()
    path = ts.shortest_coord(source=source, destination=destination)
    if path:
        vehicle = random.choice([red_car_surface, truck_surface, race_car_surface])
        new_vehicle = Vehicle(path, vehicle)
        if is_user_defined:
            my_vehicle.append(new_vehicle)
        else:
            new_vehicle.show_path = True
            vehicles.append(new_vehicle)

menu = UI(menu_bar_surface, menu_bar_surface, SCREEN_WIDTH * 0.91, SCREEN_HEIGHT * 0.02)

while True:
    screen.blit(city_surface, (0, 0))
    menu.render()
    
    current_time = pygame.time.get_ticks()
    if current_time - spawn_timer > SPAWN_INTERVAL:
        spawn_vehicle()
        spawn_timer = current_time

    all_vehicles = vehicles + my_vehicle
    for vehicle in all_vehicles[:]:
        vehicle.update_position()
        if vehicle.has_reached_destination():
            if vehicle in vehicles:
                vehicles.remove(vehicle)
            elif vehicle in my_vehicle:
                my_vehicle.remove(vehicle)
        else:
            vehicle.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for vehicle in vehicles[:]:
                if vehicle.check_click(event.pos):
                    vehicle.show_path = not vehicle.show_path
            for vehicle in my_vehicle[:]:
                if vehicle.check_click(event.pos):
                    vehicle.show_path = not vehicle.show_path
            if menu.is_menu_bar_open and menu.click_count < 2:
                if menu.click_count == 0:
                    menu.handle_source_destination(event.pos)
                    play_selected_sound()
                elif menu.click_count == 1:
                    menu.handle_source_destination(event.pos)
                    play_selected_sound()
            if menu.menu_icon_rect.collidepoint(event.pos):
                menu.show_text()
                play_selected_sound()
                if not menu.is_menu_bar_open:
                    menu.reset_state()
                menu.is_menu_bar_open = not menu.is_menu_bar_open
                print("Rectangle clicked!")
                
    pygame.display.update()
    clock.tick(100)