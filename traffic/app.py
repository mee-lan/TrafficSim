import pygame
from consts import SCREEN_HEIGHT,SCREEN_WIDTH,screen,clock,menu_bar_surface,city_surface,spawn_timer,SPAWN_INTERVAL
from sys import exit
from city_graph import shortest_coord
from utility_func import spawn_vehicle
from sound import play_selected_sound
from vehicle_class import vehicles,my_vehicle
from ui_class import home_screen,UI

pygame.init()
collided = []
source = None
destination = None

#Start From home screen
home_screen()

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