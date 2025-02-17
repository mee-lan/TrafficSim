import pygame
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
        self.path = path
        self.facing='F'
        self.current_index = 0
        self.original_surface = image  # Store original image later used in rotation of image
        self.surface = image.copy()
        self.x,self.y=path[0]
        self.rect = self.surface.get_rect(center=(self.x,self.y))

        # Set initial rotation based on the first movement direction
        if len(self.path) > 1:
            self.set_initial_direction(self.path[0], self.path[1])

    def set_initial_direction(self, start, next_pos):
        """Set initial rotation based on first movement direction."""
        start_x, start_y = start
        next_x, next_y = next_pos

        if next_x > start_x:  # Moving right
            angle = -90
            self.facing='R'
        elif next_x < start_x:  # Moving left
            angle = 90
            self.facing='L'
        elif next_y > start_y:  # Moving down
            angle = 180
            self.facing='D'
        else:  # Moving up (default orientation)
            angle = 0
            self.facing='U'

        self.surface = pygame.transform.rotate(self.original_surface, angle)
        self.rect = self.surface.get_rect(center=self.rect.center)

    def update_position(self):
            
            target_x, target_y = self.path[self.current_index + 1]
            x,y = self.path[self.current_index + 1]
            # if self.facing=='U':
            #      target_x, target_y = (x-10,y)
            #      self.x,self.y = (x-10,y)

            # elif self.facing=='L':
            #     target_x, target_y = (x,y+10)
            #     self.x,self.y = (x,y+10)
            
            # elif self.facing=='D':
            #     target_x, target_y = (x+10,y)
            #     self.x,self.y = (x+10,y)

            # elif self.facing=='R':
            #     target_x, target_y = (x,y-10)
            #     self.x,self.y = (x,y-10)

            
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery

            if abs(dx) > 0:
                self.rect.centerx += 1 if dx > 0 else -1
            elif abs(dy) > 0:
                self.rect.centery += 1 if dy > 0 else -1

            if (self.rect.centerx, self.rect.centery) == (target_x, target_y):
                self.current_index += 1  # Move to next waypoint
                if self.current_index < len(self.path) - 1:
                    next_x, next_y = self.path[self.current_index + 1]
                    self.rotate_vehicle(target_x, target_y, next_x, next_y)

                    

    def rotate_vehicle(self, target_x, target_y, next_x, next_y):
        print(self.facing)
        if self.facing=='U' and target_x<next_x:
            self.surface = pygame.transform.rotate(self.original_surface, -90) #Rotation angles are with respect to initial image(facing forward)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.facing='R'
        
        elif self.facing=='U' and target_x>next_x:
            self.surface = pygame.transform.rotate(self.original_surface, +90)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.facing='L'

        elif self.facing=='L' and target_y>next_y:
            self.surface = pygame.transform.rotate(self.original_surface, 0)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.facing='U'
        
        elif self.facing=='L' and target_y<next_y:
            self.surface = pygame.transform.rotate(self.original_surface, 180)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.facing='D'
        
        elif self.facing=='R' and target_y>next_y:
            self.surface = pygame.transform.rotate(self.original_surface, 0)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.facing='U'
        
        elif self.facing=='R' and target_y<next_y:
            self.surface = pygame.transform.rotate(self.original_surface, -180)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.facing='D'

        elif self.facing=='D' and target_x<next_x:
            self.surface = pygame.transform.rotate(self.original_surface, -90)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.facing='L'
        
        elif self.facing=='D' and target_x>next_x:
            self.surface = pygame.transform.rotate(self.original_surface, +90)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.facing='R'


    def has_reached_destination(self):
        """Check if the vehicle has reached its final destination."""
        return self.current_index >= len(self.path) - 1

    def draw(self, screen):
        """Draw the vehicle on the screen."""
        screen.blit(self.surface, self.rect)



def spawn_vehicle():
    """Spawn a vehicle with a random source & destination (only edge nodes)."""
    global vehicles,vehicle_surface
    source, destination = utility_func.random_spawn_edge()
    path = ts.shortest_coord(source=source, destination=destination)

    if path:
        new_vehicle = Vehicle(path,vehicle_surface)
        vehicles.append(new_vehicle)


while True:
    screen.blit(city_surface, (0, 0))  # Display background

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
            print(pygame.mouse.get_pos())

    pygame.display.update()
    clock.tick(144)
