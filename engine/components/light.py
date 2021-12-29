from enum import IntEnum, auto

from .component import Component
# we are getting circular refernces
# from engine.gui import LightGUI
import engine.gui.light_gui as light_gui

# as a component, it needs to receive a game_object and therefore a transform.
class LightType(IntEnum):
    DIRECTIONAL = auto()
    POINT = auto()

# should i use a sub class for each type of light or just an enum?
# let's use an enum for now
class Light(Component):

    def __init__(self, game_object, light_type = LightType.DIRECTIONAL):
        super().__init__(game_object)
        self.light_type = light_type
        # we need to make sure all channels (specially the first one) are treated as float
        self.color = (1.0, 0.992, 0.658) # yellowish

        self.gui = light_gui.LightGUI(self)
        self.name = "light"

    # internal getters
    @property
    def position(self):
        # should we return a pyrr.vector or a flat array?
        # let's try the 2nd
        if (self.light_type == LightType.DIRECTIONAL):
            # similarly to our camera,
            # the negative of the forward direction is the
            # direction of they ray from the light source
            # therefore, in the shader, to get the ray
            # from surface to light, we have to invert this value again
            direction = -self.game_object.transform.forward
            return [*direction, 0]
        else:
            position = self.game_object.transform.position
            return [*position, 1]


