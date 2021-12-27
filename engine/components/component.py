# since python list can have elements of different types,
# do we actually need a base class for components?
class Component:

    def __init__(self, game_object):
        self.game_object = game_object
        self.name = ""
        self.gui = None

        # in Unity, the class hierarchy is
        # Component > Behaviour > MonoBehaviour with the enabled property at Behaviour level
        self.enabled = True
