import pygame
pygame.init()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Traffic")

font = pygame.font.Font('traffic/src/fonts/small_pixel.ttf', 26)
TEXT_COL = (255, 255, 255)

spawn_timer = 0
text_timer = 0
SPAWN_INTERVAL = 4000

city_surface = pygame.image.load("traffic/src/images/city.jpg").convert()
truck_surface = pygame.image.load("traffic/src/images/truck.png").convert_alpha()
red_car_surface = pygame.image.load("traffic/src/images/redcar.png").convert_alpha()
race_car_surface = pygame.image.load("traffic/src/images/race_car.png").convert_alpha()
location_icon_surface = pygame.image.load("traffic/src/images/location_icon.png").convert_alpha()
menu_bar_surface = pygame.image.load("traffic/src/images/menu_bar.png").convert_alpha()

city_surface = pygame.transform.scale(city_surface, (1000, 1000))
truck_surface = pygame.transform.scale(truck_surface, (22, 80))
red_car_surface = pygame.transform.scale(red_car_surface, (20, 67))
race_car_surface = pygame.transform.scale(race_car_surface, (20, 50))
location_icon_surface = pygame.transform.scale(location_icon_surface, (56, 56))
menu_bar_surface = pygame.transform.scale(menu_bar_surface, (56, 56))

from collections import defaultdict
vehicle_counts = defaultdict(int)