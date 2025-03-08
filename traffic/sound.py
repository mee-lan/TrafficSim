# sound.py
import pygame

# Initialize the mixer
pygame.mixer.init()
intro_sound=None

def load_and_play_city_sound():
    """
    Loads and plays the city ambient sound in a loop.
    """
    # Load the city/ambient sound (replace with your own sound file)
    city_sound = pygame.mixer.Sound("traffic/src/sound/city_sound.mp3")
    
    # Play the city sound in a loop
    city_sound.play(loops=-1, maxtime=0)  # Loop indefinitely
    
    return city_sound

def stop_sound(city_sound):
    """
    Stops the sound that is currently playing.
    """
    city_sound.stop()
    intro_sound.stop()

def play_selected_sound():
    selected_sound = pygame.mixer.Sound("traffic/src/sound/select_sound.mp3")
    selected_sound.play()

def intro_sound():
    global intro_sound
    intro_sound = pygame.mixer.Sound("traffic/src/sound/intro_sound.mp3")
    intro_sound.play()  

