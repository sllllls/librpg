import pygame
from pygame.locals import *

from librpg.context import Context, get_context_stack
from librpg.virtualscreen import get_screen
from librpg.config import game_config
from librpg.util import check_direction, fill_with_surface, descale_point
from librpg.locals import *

from librpg.menu.div import Div


class Menu(Div):

    MOUSE_OFF = 0
    MOUSE_STRICT = 1
    MOUSE_LOOSE = 2

    def __init__(self, width, height, x=0, y=0, theme=None, bg=None,
                 mouse_control=MOUSE_LOOSE):
        Div.__init__(self, width, height, theme)
        self.x = x
        self.y = y
        self.cursor = None
        self.menu = self
        self.all_widgets = []
        self.init_bg(bg)
        assert mouse_control in (Menu.MOUSE_OFF,
                                 Menu.MOUSE_STRICT,
                                 Menu.MOUSE_LOOSE),\
                                'mouse_control must be 0, 1 or 2'
        self.mouse_control = mouse_control

        self.should_close = False

    def init_bg(self, bg):
        self.bg = pygame.Surface((self.width, self.height), SRCALPHA, 32)\
                  .convert_alpha()
        if bg is not None:
            if isinstance(bg, tuple) and len(bg) >= 3:
                self.bg.fill(bg)
            else:
                fill_with_surface(self.bg, bg)
        else:
            BLACK = (0, 0, 0, 255)
            self.bg.fill(BLACK)

    def draw(self):
        scr = get_screen()
        scr.blit(self.bg, (self.x, self.y))
        Div.draw(self)
        Div.render(self, scr, self.x, self.y)
        if self.cursor is not None:
            self.cursor.draw()
            self.cursor.render(scr)

    # Use cursor.bind instead
    def add_cursor(self, cursor):
        if self.cursor is not None:
            return False
        else:
            self.cursor = cursor
            return True

    def remove_cursor(self):
        result = self.cursor
        self.cursor = None
        return result

    def register_widget(self, widget):
        self.all_widgets.append(widget)

    def unregister_widget(self, widget):
        self.all_widgets.remove(widget)

    def close(self):
        self.should_close = True

    def process_event(self, event):
        return False


class MenuController(Context):

    COMMAND_COOLDOWN = 5

    def __init__(self, menu, parent=None):
        assert menu is not None, 'menu cannot be None'
        Context.__init__(self, parent)
        self.menu = menu
        menu.controller = self
        self.command_queue = []
        self.command_cooldown = 0
        self.done = False

    def draw(self):
        self.menu.draw()

    def update(self):
        if self.menu.should_close:
            self.done = True
            self.stop()
            return False

        cursor = self.menu.cursor
        if cursor is not None:
            if self.command_cooldown > 0:
                self.command_cooldown -= 1
            elif self.command_queue:
                direction = self.command_queue[0]
                if direction == ACTIVATE or direction == MOUSE_ACTIVATE:
                    self.activate()
                    self.command_cooldown = MenuController.COMMAND_COOLDOWN
                else:
                    cursor.step(direction)
                    self.command_cooldown = MenuController.COMMAND_COOLDOWN
            cursor.update()
        self.menu.update()
        return False

    def activate(self):
        cursor = self.menu.cursor
        if cursor is not None:
            w = cursor.widget
            while w is not None:
                if w.activate():
                    return
                w = w.parent

    def process_event(self, event):
        cursor = self.menu.cursor
        if cursor is not None:
            w = cursor.widget
            while w is not None:
                if w.process_event(event):
                    return True
                w = w.parent
        if self.menu.process_event(event):
            return True
        return self.menu_process_event(event)

    def menu_process_event(self, event):
        if event.type == KEYDOWN:
            direction = check_direction(event.key)
            if direction is not None and\
               not direction in self.command_queue:
                self.command_queue.append(direction)
                return True
            elif event.key in game_config.key_action:
                if not ACTIVATE in self.command_queue:
                    self.command_queue.insert(0, ACTIVATE)
                return True
            elif event.key in game_config.key_cancel:
                self.stop()
                return True
        elif event.type == KEYUP:
            direction = check_direction(event.key)
            if direction is not None and\
               direction in self.command_queue:
                self.command_queue.remove(direction)
                return True
            elif event.key in game_config.key_action \
                 and ACTIVATE in self.command_queue:
                self.command_queue.remove(ACTIVATE)
                return True
        elif event.type == MOUSEMOTION:
            self.process_mouse_motion(event)
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if not MOUSE_ACTIVATE in self.command_queue:
                    self.command_queue.insert(0, MOUSE_ACTIVATE)
                return True
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                if MOUSE_ACTIVATE in self.command_queue:
                    self.command_queue.remove(MOUSE_ACTIVATE)
                return True
        return False

    def process_mouse_motion(self, event):
        if self.menu.mouse_control == Menu.MOUSE_OFF:
            return

        cursor = self.menu.cursor
        if cursor is None:
            return

        pos = descale_point(event.pos)

        if self.menu.mouse_control == Menu.MOUSE_STRICT:
            if cursor.widget.contains_point(pos):
                return
            for w in self.menu.all_widgets:
                if w.focusable and w.contains_point(pos):
                    cursor.move_to(w)
                    return
        else:
            best = (None, 999999)
            for w in self.menu.all_widgets:
                if w.focusable:
                    dist = w.distance_to_point(pos)
                    if dist < best[1]:
                        best = (w, dist)
            if best[0] is not None:
                cursor.move_to(best[0])

    def is_done(self):
        return self.done
