import pygame
from sound import intro_sound,play_selected_sound,load_and_play_city_sound
from city_graph import coordinates
from utility_func import spawn_vehicle
import math
from consts import screen,SCREEN_HEIGHT,SCREEN_WIDTH,font,TEXT_COL,clock,location_icon_surface,text_timer

class UI:
    def __init__(self, surface, image, x, y):
        self.image = image
        self.surface = surface
        self.x = x
        self.y = y
        self.click_count = 0
        self.draw_location_icon = False
        self.source_coords = (-120, -120)  
        self.source_node = None
        self.destination_node = None
        self.destination_coords = (-120, -120)  
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
        
        if not self.menu_icon_rect.collidepoint(pos):
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
        self.source_coords = (-120, 1200) 
        self.destination_coords = (-120, -120) 
        self.click_count = 0



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
            screen.blit(title_text, (SCREEN_WIDTH//2 - 120, 360))  

        elif text_timer == 100:
            text_timer = 0
        
        text_timer += 1
        
        start_rect = pygame.Rect(SCREEN_WIDTH//2 - 78, 480, 180, 60) 
        quit_rect = pygame.Rect(SCREEN_WIDTH//2 - 48, 552, 120, 48)  
        
        pygame.draw.rect(screen, (50, 200, 50), start_rect)
        pygame.draw.rect(screen, (200, 50, 50), quit_rect)
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2 + 12, 492)) 
        screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2 + 12, 564)) 

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


def draw_text(text, font, text_col):
    global text_timer
    if text_timer < 50:
        text_surf = font.render(text, True, text_col)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT * 0.03))  
        screen.blit(text_surf, text_rect)

    text_timer += 1
    if text_timer == 100:
        text_timer = 0


def draw_item(coords):
    loc_rect = location_icon_surface.get_rect(center=coords)
    screen.blit(location_icon_surface, loc_rect.topleft)


