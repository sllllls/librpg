import pygame

def init():
    pygame.init()
    
import config
import virtual_screen

def init_real_screen(real_screen_dimensions, display_mode):

    return pygame.display.set_mode(real_screen_dimensions, display_mode)

def init_virtual_screen(screen_dimensions, final_screen, scale):

    return virtual_screen.ScaledScreen(screen_dimensions, final_screen, scale, depth=32)

real_screen = init_real_screen(config.graphics_config.real_screen_dimensions, config.graphics_config.display_mode)
screen = init_virtual_screen(config.graphics_config.screen_dimensions, real_screen, config.graphics_config.scale)

import party
import map
import mapobject
import camera
import image
import log
import item
import util
from locals import *
