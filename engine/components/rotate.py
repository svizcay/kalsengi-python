import pyrr

# i don't want to reference things as engine.<thing>
# i want to reference them by the actual name of the engine as
# kalsengi.time
import engine.time
from .component import Component


class Rotate(Component):

    def __init__(self, game_object, angular_speed = 15.0, axis = pyrr.Vector3([0, 1, 0])):
        super().__init__(game_object)

        self.angular_speed = angular_speed
        self.axis = axis

    def update(self):
        # we need to access our Time singleton here
        delta_rot = (self.angular_speed * engine.time.delta_time) * (self.axis)
        # delta_rot = self.angular_speed * (self.axis)
        self.game_object.transform.rotate(delta_rot)
