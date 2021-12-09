# since python list can have elements of different types,
# do we actually need a base class for components?
class Component:

    def __init__(self, game_object):
        self.game_object = game_object
