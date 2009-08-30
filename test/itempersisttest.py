# Imports

import librpg
from librpg.map import MapModel
from librpg.mapobject import ScenarioMapObject
from librpg.util import Position
from librpg.party import Character, CharacterReserve, Party
from librpg.world import MicroWorld
from librpg.item import OrdinaryInventory, OrdinaryItem
from librpg.dialog import MessageDialog
from librpg.context import Context, get_context_stack

from pygame.locals import *
import os

SAVE_FILE = "itempersisttest.sav"

# Items

ITEM_LOG = 'log'
ITEM_LEAF = 'leaf'

class LogItem(OrdinaryItem):
    def __init__(self):
        OrdinaryItem.__init__(self, ITEM_LOG, 'Log')

class LeafItem(OrdinaryItem):
    def __init__(self):
        OrdinaryItem.__init__(self, ITEM_LEAF, 'Leaf')

def item_factory(id):
    return {ITEM_LOG: LogItem, ITEM_LEAF: LeafItem}[id]()


# Map objects

class LogPile(ScenarioMapObject):

    def __init__(self, map):
        ScenarioMapObject.__init__(self, map, 0, 9)
        
    def activate(self, party_avatar, direction):
        added = party_avatar.party.inventory.add_item_by_id(ITEM_LOG)
        if added:
            self.map.schedule_message(MessageDialog("Got a Log."))
        else:
            self.map.schedule_message(MessageDialog("Inventory full of Logs."))


class Tree(ScenarioMapObject):

    def __init__(self, map):
        ScenarioMapObject.__init__(self, map, 0, 5)
        
    def activate(self, party_avatar, direction):
        added = party_avatar.party.inventory.add_item_by_id(ITEM_LEAF)
        if added:
            self.map.schedule_message(MessageDialog("Got a Leaf."))
        else:
            self.map.schedule_message(MessageDialog("Inventory full of Leaves."))

class SavePoint(ScenarioMapObject):

    def __init__(self, map):
        ScenarioMapObject.__init__(self, map, 0, 7)

    def activate(self, party_avatar, direction):
        self.map.schedule_message(MessageDialog('You game will be saved to %s.'
                                  % SAVE_FILE, block_movement=True))
        self.map.save_world(SAVE_FILE)
        self.map.schedule_message(MessageDialog('Game saved.',
                                                block_movement=True))
# Map

class PersistTestMap(MapModel):
    
    def __init__(self):
        MapModel.__init__(self, 'itempersisttest.map',
                          ('lower_tileset32.png', 'lower_tileset32.bnd'),
                          [('upper_tileset32.png', 'upper_tileset32.bnd')])

    def initialize(self, local_state, global_state):
        self.add_object(LogPile(self), Position(4, 5))
        self.add_object(Tree(self), Position(6, 5))
        self.add_object(SavePoint(self), Position(5, 2))
        
        self.inventory_context = InventoryContext(self)
        self.add_context(self.inventory_context)


# Party

class TestParty(Party):
    
    def __init__(self, reserve, capacity=None, chars=None, leader=None,
                 party_state=None):
        Party.__init__(self, reserve, capacity, chars, leader,
                       party_state)
        if party_state is None:
            self.inventory = OrdinaryInventory(item_factory)

    def custom_save(self):
        return self.inventory

    def custom_initialize(self, party_state=None):
        print party_state.get_items_with_amounts()
        self.inventory = party_state


# Char and party factories

def char_factory(name, char_state):
    return Character('Andy', 'char_alex32.png')

def party_factory(reserve, capacity=None, chars=None, leader=None,
                  party_state=None):
    return TestParty(reserve, capacity, chars, leader, party_state)


# Inventory context

class InventoryContext(Context):

    def __init__(self, map):
        Context.__init__(self, map)
        self.map = map
        self.inv = map.party.inventory

    def process_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_i \
               and not self.map.controller.message_queue.is_active():
                msg = str(self.inv.get_items_with_amounts())
                self.map.schedule_message(MessageDialog(msg))
                return True
        return False


# Main

if __name__ == '__main__':
    librpg.init('Item Persist Test')
    librpg.config.graphics_config.config(tile_size=32,
                                         object_height=32,
                                         object_width=32,
                                         scale=2)

    world = MicroWorld(PersistTestMap(), char_factory, party_factory)
    if SAVE_FILE in os.listdir('.'):
        world.load_config(SAVE_FILE)
    else:
        world.initial_config(Position(4, 3), ['Andy'])
    world.gameloop()
    exit()
