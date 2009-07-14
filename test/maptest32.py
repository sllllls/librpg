from librpg.map import *
from librpg.util import *
from librpg.party import *
from librpg.config import *

import pygame

pygame.init()

graphics_config.screen_width = 300
graphics_config.screen_height = 400
graphics_config.tile_size = 32
graphics_config.object_height = 32
graphics_config.object_width = 32

m = Map(MapModel('maptest32.map', ('lower_tileset32.png', 'lower_tileset32.bnd'), ('upper_tileset32.png', 'upper_tileset32.bnd')))

r = CharacterReserve()
a = Character('Andy', 'char_alex32.png')
r.add_char(a)
p = r.create_party(3)
p.add_char(a)

print 'Adding', str(p)
m.map_model.add_party(p, Position(0, 0))
print 'Added'
print

print 'Starting gameloop()'
m.gameloop()
print 'Finished gameloop()'

exit()