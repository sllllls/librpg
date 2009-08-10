import pygame

from image import ObjectImage

class Party(object):

    # Public Attributes:
    # leader - character who is the current party leader

    # Read-Only Attributes:
    # capacity - maximum number of characters
    # reserve - CharacterReserve that contains the party's characters
    # chars - list of characters in the party currently

    # Called only by CharacterReserve, use
    # CharacterReserve.create_party()
    def __init__(self, capacity, reserve):
        self.capacity = capacity
        self.reserve = reserve
        self.chars = []
        self.leader = None

    def add_char(self, char):
        if char not in self.reserve.get_chars() or\
           len(self.chars) >= self.capacity:
            return False
        else:
            self.reserve.allocate_char(char, self)
            self.chars.append(char)
            if self.leader is None:
                self.leader = char
            return True

    def remove_char(self, char):
        if char in self.chars:
            self.reserve.allocate_char(char, None)
            self.chars.remove(char)
            if self.leader == char:
                if len(self.chars) == 0:
                    self.leader = None
                else:
                    self.leader = self.chars[0]
            return True
        else:
            return False

    def __repr__(self):
        if len(self.chars) == 0:
            return '(Empty party)'
        else:
            chars = ', '.join([str(c) for c in self.chars if c != self.leader])
            return '(Leader: %s, %s)' % (self.leader, chars)

    def get_image(self, avatar):
        assert self.leader, 'A Party with no characters may not be displayed'
        return self.leader.image


class CharacterReserve(object):

    # Read-Only Attributes:
    # chars - maps the characters in the reserve currently to the party they are in
    # parties - list of parties that contain the characters in this reserve

    def __init__(self, chars=[]):
        self.chars = {}
        self.parties = []

        for char in chars:
            self.add_char(char)

    def add_char(self, char):
        self.chars[char] = None

    def remove_char(self, char):
        if self.chars.has_key(char):
            if self.chars[char] is not None:
                self.chars[char].remove_char(char)
            del self.chars[char]
            return char
        else:
            return None

    def create_party(self, capacity, chars=[]):
        party = Party(capacity, self)
        self.parties.append(party)

        for char in chars:
            party.add_char(char)

        return party

    def destroy_party(self, party):
        if party not in self.parties:
            return False
        for char in party.chars:
            self.chars[char] = None
        self.parties.remove(party)
        return True

    def get_chars(self):
        return self.chars.keys()

    # Used only by Party
    def allocate_char(self, char, party):
        self.chars[char] = party

    def __repr__(self):
        return self.chars.__repr__()


class Character(object):

    """
    name: string (public)
    The character's name as it should be displayed.

    image_file: string (read-only)
    The file with the character's sprites.

    image: ObjectImage (read-only)
    The character's sprites.
    """

    def __init__(self, name, image_file=None, index=0):
        self.name, self.image_file = name, image_file
        if image_file:
            self.image = ObjectImage(self.image_file, index)
        else:
            self.image = None

    def __repr__(self):
        return self.name

