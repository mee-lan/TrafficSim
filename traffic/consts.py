import pygame
pygame.init()
SCREEN_WIDTH = 1080  
SCREEN_HEIGHT = 1080  
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Traffic")

font = pygame.font.Font('traffic/src/fonts/small_pixel.ttf', 26)
TEXT_COL = (255, 255, 255) 

spawn_timer = 0
text_timer = 0
SPAWN_INTERVAL = 4000 


# Load images
city_surface = pygame.image.load("traffic/src/images/city.jpg").convert()
truck_surface = pygame.image.load("traffic/src/images/truck.png").convert_alpha()
red_car_surface = pygame.image.load("traffic/src/images/redcar.png").convert_alpha()
race_car_surface = pygame.image.load("traffic/src/images/race_car.png").convert_alpha()
location_icon_surface = pygame.image.load("traffic/src/images/location_icon.png").convert_alpha()
menu_bar_surface = pygame.image.load("traffic/src/images/menu_bar.png").convert_alpha()

# Transform images (scale by 1.2)
city_surface = pygame.transform.scale(city_surface, (1080, 1080))  
truck_surface = pygame.transform.scale(truck_surface, (24, 86))    
red_car_surface = pygame.transform.scale(red_car_surface, (22, 72))  
race_car_surface = pygame.transform.scale(race_car_surface, (22, 54))  
location_icon_surface = pygame.transform.scale(location_icon_surface, (60, 60))  
menu_bar_surface = pygame.transform.scale(menu_bar_surface, (60, 60))  

from collections import defaultdict

# Dictionary to store the number of vehicles per edge, with edges as sorted tuples (e.g., ('A', 'D'))
vehicle_counts = defaultdict(int)