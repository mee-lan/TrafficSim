#This one is reference project which i did earlier while learning pygame  (dino game jasto banauda)


import pygame
from sys import exit
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT)) #Main display surface over which we draw other (regular)surfaces
pygame.display.set_caption("Traffic") # gives name to the window
clock = pygame.time.Clock() #needed to manage FPS
test_font = pygame.font.Font('py_game/fonts/small_pixel.ttf',50) #font type and font size params


#STATE:
game_active = True
start_time=0


#SURFACES:
sky_surface = pygame.image.load('py_game/graphics/sky.png').convert()
bot_surface = pygame.image.load('py_game/graphics/bot.png').convert_alpha()
ground_surface = pygame.image.load('py_game/graphics/groundimg.jpg').convert()
player_surface = pygame.image.load('py_game/graphics/player1.png').convert_alpha()



#Transform images
sky_surface= pygame.transform.scale(sky_surface,(SCREEN_WIDTH,SCREEN_HEIGHT*0.8))
ground_surface= pygame.transform.scale(ground_surface,(SCREEN_WIDTH,SCREEN_HEIGHT*0.2))
bot_surface = pygame.transform.scale(bot_surface,(100,100))
player_surface = pygame.transform.scale(player_surface,(300,250))

#RECTANGLE:
# converting surface to rect allows to take difference anchor points of image to place
player_rect = player_surface.get_rect(midbottom = (100,SCREEN_HEIGHT*0.85))
bot_rect = bot_surface.get_rect(midbottom = (SCREEN_WIDTH,SCREEN_HEIGHT*0.8))
# use midbottom, midleft, topleft,center etc
def update_score():
    time_in_sec=pygame.time.get_ticks()//10-start_time
    score_surf = test_font.render(f'SCORE: {time_in_sec}',False,(64,64,64))
    score_rect = score_surf.get_rect(center = (SCREEN_WIDTH//2,50))
    screen.blit(score_surf,score_rect)
    print(time_in_sec)

player_gravity =0
c=0

while True:

    if game_active: #state representing user is playing the game

        screen.blit(ground_surface,(0,SCREEN_HEIGHT*0.8))
        screen.blit(sky_surface,(0,0)) #blit = block image transfer (used to diplay surfaces )
        screen.blit(bot_surface,bot_rect)
        screen.blit(player_surface,player_rect)
        update_score()

        player_rect.bottom+=player_gravity
        player_gravity+=0.1
        #print(player_rect.bottom)
        if player_rect.bottom>=SCREEN_HEIGHT*0.85: player_rect.bottom = SCREEN_HEIGHT*0.85

        #if doesnot collide move bot to the left else
        if(not player_rect.colliderect(bot_rect)):
            if (bot_rect.right>-100): bot_rect.right-=5
            else: bot_rect.right=SCREEN_WIDTH
        else:
             print("collission")
             game_active=False
             bot_rect.left = SCREEN_WIDTH
             player_rect.left = 0

    else:
        screen.fill('Yellow')
        start_time=pygame.time.get_ticks()//10

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
                player_gravity=-5
        
        if event.type == pygame.KEYDOWN:
            #print("key up")
            if event.key ==  pygame.K_SPACE:
                if not game_active:
                     game_active=True
                else:
                    if(player_rect.bottom>=SCREEN_HEIGHT*0.85):
                        print(player_rect.bottom)
                        print(player_gravity)
                        player_gravity=-8

    

    pygame.display.update()
    clock.tick(144) # sets the FPS to 60fps

 