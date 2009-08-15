import pygame

from librpg.locals import *
from librpg.movement import MovementQueue, MovementCycle
from librpg.image import ObjectImage

class MapObject(object):

    """
    image: ObjectImage (read-only)
    Image of the MapObject. If this field is None, the object will be
    invisible.

    map: MapModel (read-only)
    The MapModel in which the MapObject was placed. None is if it not
    placed in any map.

    position: Position (read-only)
    Where on the map the MapObject is. None if it is not in any map.

    obstacle: int (read-only)
    0 if a party or an object can move over this object, 3 if they can
    move under it, 1 if it is considered an obstacle. If it is a
    counter - that is, if push key events may affect objects on the
    other side of it -, this attribute is set to 2.

    facing: Direction (public)
    Direction that the object is facing.

    speed: int (public)
    Object speed, in the number of frames to move that object by 1 tile.
    Use VERY_FAST_SPEED, FAST_SPEED, NORMAL_SPEED, SLOW_SPEED and
    VERY_SLOW_SPEED.

    movement_phase: int (private)
    0 if still, 1 to speed if in the middle of a movement.
    """

    BELOW, OBSTACLE, COUNTER, ABOVE = 0, 1, 2, 3

    def __init__(self, obstacle, image=None, facing=DOWN, speed=NORMAL_SPEED,
                 image_file=None, image_index=0):

        assert obstacle in range(0, 4), ('MapObject cannot be created with an'
                                         ' `obstacle` as %s' % str(obstacle))
        assert (image is None or image_file is None),\
                'Only one of (image, image_file) can be specified.'

        self.map = None
        self.position = None
        self.prev_positon = None
        self.obstacle = obstacle

        self.movement_phase = 0
        self.facing = facing
        self.speed = speed
        self.scheduled_movement = MovementQueue()
        self.movement_behavior = MovementCycle()
        self.sliding = False
        self.just_completed_movement = False

        self.areas = []
        self.prev_areas = []
        
        if image is not None:
            self.image = image
        elif image_file is not None:
            self.image = ObjectImage(image_file, image_index)

    # Virtual
    def activate(self, party_avatar, direction):
        pass

    # Virtual
    def collide_with_party(self, party_avatar, direction):
        pass

    def is_counter(self):
        return self.obstacle == MapObject.COUNTER

    def is_obstacle(self):
        return (self.obstacle == MapObject.OBSTACLE or
                self.obstacle == MapObject.COUNTER)

    def is_below(self):
        return self.obstacle == MapObject.BELOW

    def is_above(self):
        return self.obstacle == MapObject.ABOVE

    def get_surface(self):
        return self.image.get_surface(self)

    def flow(self):
        just_completed_movement = False

        if self.movement_phase == 1:
            self.just_completed_movement = True

        if self.movement_phase > 0:
            self.movement_phase -= 1
        else:
            no_scheduled_movement = self.scheduled_movement.flow(self)
            if no_scheduled_movement:
                self.movement_behavior.flow(self)

    def schedule_movement(self, movement):
        self.scheduled_movement.append(movement)


class PartyAvatar(MapObject):

    def __init__(self, party, facing=DOWN, speed=NORMAL_SPEED):
        MapObject.__init__(self, MapObject.OBSTACLE, party.get_image(self),
                           facing, speed)
        self.party = party


class ScenarioMapObject(MapObject):

    def __init__(self, map, scenario_number, scenario_index, obstacle=None,
                 facing=DOWN, speed=NORMAL_SPEED):
        tile = map.scenario_tileset[scenario_number].tiles[scenario_index]
        if obstacle is None:
            MapObject.__init__(self, tile.obstacle, tile.image, facing, speed)
        else:
            MapObject.__init__(self, obstacle, tile.image, facing, speed)

