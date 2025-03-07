import pygame
import random
from sys import exit
import math
import city_graph as ts
import utility_func as utility_func
from city_graph import coordinates

pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Traffic")

#load font
font=pygame.font.Font("traffic/src/fonts/small_pixel.ttf",22)

#color
TEXT_COL=(7, 250, 174)

# Load images
city_surface = pygame.image.load("traffic/src/images/city.jpg").convert_alpha()
truck_surface = pygame.image.load("traffic/src/images/truck.png").convert_alpha()
red_car_surface = pygame.image.load("traffic/src/images/redcar.png").convert_alpha()
location_icon_surface = pygame.image.load("traffic/src/images/location_icon.png").convert_alpha()
menu_bar_surface = pygame.image.load("traffic/src/images/menu_bar.png").convert_alpha()


#Transform images
city_surface = pygame.transform.scale(city_surface, (900, 900))
truck_surface = pygame.transform.scale(truck_surface, (22, 80))
red_car_surface = pygame.transform.scale(red_car_surface, (18, 60))
location_icon_surface=pygame.transform.scale(location_icon_surface, (50, 50))
menu_bar_surface=pygame.transform.scale(menu_bar_surface, (50, 50))
#yellow_car_surface = pygame.transform.scale(yellow_car_surface, (20, 50))

# List to store active vehicles
vehicles = []
my_vehicle=[]
collided= []
source=None,
destination=None

spawn_timer = 0  # Timer for controlling vehicle spawn interval
text_timer=0
SPAWN_INTERVAL = 3000  # 3 seconds
vehicle_id_counter=0

def draw_text(text,font,text_col):
    global text_timer
    if text_timer<50:
        text_surf = font.render(text,True,text_col)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT*0.03))
        screen.blit(text_surf,text_rect)

    text_timer+=1

    if text_timer==100:
        text_timer=0

def draw_item(coords):
    loc_rect = location_icon_surface.get_rect(center=coords)
    screen.blit(location_icon_surface,loc_rect.topleft)

class UI:
    def __init__(self,surface,image,x,y):
        self.image=image
        self.surface=surface
        self.x=x
        self.click_count=0
        self.y=y
        self.draw_location_icon=False
        self.source_coords = (-100,-100)
        self.source_node=None
        self.destination_node=None

        self.destination_coords=(-100,-100)
        self.is_menu_bar_open = False
        self.menu_icon_rect = self.surface.get_rect(topleft=(self.x,self.y))

    def render(self):

        screen.blit(self.surface,(self.x,self.y))

        if (self.is_menu_bar_open):
            self.show_text()
            
        if (self.draw_location_icon):
            draw_item(self.source_coords)
            draw_item(self.destination_coords)


    def handle_source_destination(self,pos):
        global source,destination,show_location_icon

        if (self.is_menu_bar_open):
            self.show_text()
        
        if not self.menu_icon_rect.collidepoint(event.pos):
            #only read it as input to source or destination coordinate if user has not clicked on menu icon
    
            if (self.click_count==0):
                node=self.find_source_or_destination_node(pos)
                self.source_coords=coordinates[node]
                self.source_node=node
                self.click_count+=1
                self.draw_location_icon=True
            
            elif (self.click_count==1):
                node=self.find_source_or_destination_node(pos)
                self.destination_coords=coordinates[node]
                self.destination_node=node
                #Both source and destination are fixed now spawn vehicle
                self.click_count=0

                self.is_menu_bar_open=False
                self.is_first_vehicle=False
                source=self.source_coords
                destination=self.destination_coords
                spawn_vehicle(self.source_node,self.destination_node)
            
            else:
                print("some error occured , clickcount",self.click_count)


            print("user clicked at x,y",pos)



    def find_source_or_destination_node(self,pos):
    
            #Find the nearest node to the clicked position
            min_dist = float('inf')
            nearest = None
            x, y = pos
            for node, (nx, ny) in coordinates.items():
                dist = math.sqrt((x - nx) ** 2 + (y - ny) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    nearest = node
            return (nearest) # returns tuple with 3 datas i.e x ,y coordinates and the name of node
    

    def show_text(self):
            draw_text(
            text="Select Source And Destination",
            font=font,
            text_col=TEXT_COL,
            )


    def reset_state(self):
            self.draw_location_icon=False
            self.source_coords=(-100,1000)
            self.destination_coords=(-100,-100)
            self.click_count=0


class Vehicle:
    def __init__(self, path, image):
        global vehicle_id_counter
        self.id = vehicle_id_counter
        vehicle_id_counter += 1  # Increment the counter
        
        self.original_path = path[:]
        self.path = self.shift_path(path)
        self.show_path = False
        self.facing = 'F'
        self.speed = 1
        self.collideflag = False
        self.pushback_active = False  # New: Tracks if vehicle is being pushed back
        self.pushback_distance = 0    # New: Total distance to push back
        self.pushback_speed = 1       # New: Speed of pushback (pixels per frame)
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
        
        print("Before path", self.original_path)
        print("After shifted path", self.path)

    def check_ahead(self,safety_distance):
        #self.old_rect = self.lookahead_rect
        #self.lookahead_rect = pygame.Rect(self.rect.centerx,self.rect.centery,40,40)
        if self.facing == 'R':
                self.lookahead_rect = pygame.Rect(self.rect.centerx, self.rect.top+5,
                                            safety_distance, self.rect.height-10)
        elif self.facing == 'L':
                self.lookahead_rect = pygame.Rect(self.rect.centerx - safety_distance,
                                            self.rect.top+5, safety_distance, self.rect.height-10)
        elif self.facing == 'U':
                self.lookahead_rect = pygame.Rect(self.rect.left+5, self.rect.centery - safety_distance,
                                            self.rect.width-10, safety_distance)
        elif self.facing == 'D':
                self.lookahead_rect = pygame.Rect(self.rect.left+5, self.rect.centery,
                                            self.rect.width-10, safety_distance)
        else:
            self.lookahead_rect = self.rect.copy()  # fallback
        

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

    def shift_path(self,path, offset=12):
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

        
    def start_pushback(self, max_distance=10):
        """Initiate a smooth pushback over multiple frames."""
        self.pushback_active = True
        self.pushback_distance = max_distance  # Total distance to push back
        self.speed = 0  # Stop forward movement during pushback
        self.collideflag = True
        print(f"Vehicle {self.id} at {self.rect.center} started pushback")


    def update_pushback(self):
        """Incrementally push the vehicle back each frame."""
        if self.pushback_active and self.pushback_distance > 0:
            push_step = min(self.pushback_speed, self.pushback_distance)  # Move by pushback_speed or remaining distance
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
        self.check_ahead(80)
        collision_detected = False
        all_vehicles = my_vehicle + vehicles
        
        for vehicle in all_vehicles:
            if vehicle is not self:
                if self.lookahead_rect.colliderect(vehicle.rect):
                    collision_detected = True
                    if self.rect.colliderect(vehicle.rect):
                        if self.id < vehicle.id and not self.pushback_active:
                            self.start_pushback(max_distance=10)  # Start smooth pushback
                        # Higher ID vehicle continues moving
                    else:
                        if self.id < vehicle.id and not self.pushback_active:
                            self.speed = 0
                            self.collideflag = True
                            print(f"Vehicle {self.id} at {self.rect.center} stopped due to near collision with Vehicle {vehicle.id}")
                    #break
        
        if not collision_detected and self.collideflag and not self.pushback_active:
            self.speed = 1
            self.collideflag = False
            print(f"Vehicle {self.id} at {self.rect.center} resumed movement")


    def update_position(self,):
        self.checkcollission()
        
        # Handle pushback if active
        if self.pushback_active:
            self.update_pushback()
        # Move forward only if not pushing back and speed > 0
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
            for i in range(self.current_index, len(self.path) - 2):

                pygame.draw.rect(screen, (255, 255, 0), self.lookahead_rect, 50)  # Draw lookahead_rect in red
                screen.blit(self.surface, self.rect)

                if self.facing=='U':
                    centerx=self.rect.centerx+10
                    centery=self.rect.centery-18 #
                elif self.facing=='D':
                    centerx=self.rect.centerx-10
                    centery=self.rect.centery+18 #

                elif self.facing=='L':
                    centerx=self.rect.centerx-18 #
                    centery=self.rect.centery-10

                elif self.facing=='R':
                    centerx=self.rect.centerx+18 #
                    centery=self.rect.centery+10

                pygame.draw.circle(
                    screen,
                    color=self.path_color,
                    center=(centerx,centery),
                    radius=5,
                    width=20

                )
                pygame.draw.line(
                    surface=screen,
                    color=self.path_color,
                    start_pos=(centerx, centery),
                    end_pos=self.original_path[self.current_index + 1],
                    width=10)
                
                pygame.draw.line(
                    surface=screen,
                    color=self.path_color,
                    start_pos=self.original_path[i+1],
                    end_pos=self.original_path[i +2],
                    width=8)
                
        screen.blit(self.surface, self.rect)


    def check_click(self, pos):
        return self.rect.collidepoint(pos)




def spawn_vehicle(source='NULL',destination='NULL'):
    """Spawn a vehicle with a random source & destination (only edge nodes)."""
    global vehicles,vehicle_surface
    is_user_defined=False

    if source=='NULL' and destination=='NULL':
        is_user_defined=True
        source, destination = utility_func.random_spawn_edge()

    path = ts.shortest_coord(source=source, destination=destination)
    
    if path:
        vehicle = random.choice([red_car_surface,truck_surface])
        new_vehicle = Vehicle(path,vehicle)

        # if source =='NULL' then it is random vehicle generated by app itself
        #  but if source and destionation given then it is by user so put them in my_vehicle list
        if is_user_defined:
            my_vehicle.append(new_vehicle)
        else:
            new_vehicle.show_path=True
            vehicles.append(new_vehicle)


menu = UI(menu_bar_surface,menu_bar_surface,SCREEN_WIDTH*0.91,SCREEN_HEIGHT*0.02) #menu icon

while True:
    screen.blit(city_surface, (0, 0))
    menu.render()
    
    # Handle vehicle spawning at intervals
    current_time = pygame.time.get_ticks()
    if current_time - spawn_timer > SPAWN_INTERVAL:
        spawn_vehicle()
        spawn_timer = current_time  # Reset spawn timer

    all_vehicles = vehicles + my_vehicle  # Combine lists for rendering and collision
    for vehicle in all_vehicles[:]:
        vehicle.update_position()
        if vehicle.has_reached_destination():
            if vehicle in vehicles:
                vehicles.remove(vehicle)
            elif vehicle in my_vehicle:
                my_vehicle.remove(vehicle)
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
            

            for vehicle in my_vehicle[:]:
                if vehicle.check_click(event.pos):
                    print("Clicked")
                    vehicle.show_path= not vehicle.show_path

            if (menu.is_menu_bar_open): # only handle source destination logic if menu is opened
                if (menu.click_count < 2): # user can click only twice i.e source and destination
                    menu.handle_source_destination(event.pos)
    
            if menu.menu_icon_rect.collidepoint(event.pos):
                menu.show_text()
                if not menu.is_menu_bar_open: menu.reset_state() #if it is just click reset state like click count=0 source,dest=-100
                menu.is_menu_bar_open = not menu.is_menu_bar_open
                print("Rectangle clicked!")

                
    pygame.display.update()
    clock.tick(100)
