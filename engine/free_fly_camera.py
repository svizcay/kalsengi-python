import glfw
import pyrr

# we don't work on a camera, we work on its transform
# but that is actually internal to the camera class
# from .transform import Transform
from .camera import Camera

class FreeFlyCamera:

    def __init__(self, camera):
        self.camera = camera

        self.speed = 5

        # there are different "approaches/models" for moving a camera.
        # - 1st attemp learnopengl:
        #   * in a single frame check for all keys that are pressed
        #   * if they are mapped to some direction, add/substract to the current position accordingly
        #   * multiply that by some speed and delta time

    def process_input(self, glfw_context, delta_time):
        delta_pos = pyrr.Vector3([0, 0, 0])
        if (glfw.get_key(glfw_context, glfw.KEY_W) == glfw.PRESS):
            delta_pos = delta_pos + (self.speed * delta_time) * pyrr.Vector3([0, 0, -1])
            # print("W pressed -> delta_pos = {}".format(delta_pos))
        if (glfw.get_key(glfw_context, glfw.KEY_S) == glfw.PRESS):
            delta_pos = delta_pos + (self.speed * delta_time) * pyrr.Vector3([0, 0, 1])
            # print("S pressed -> delta_pos = {}".format(delta_pos))
        if (glfw.get_key(glfw_context, glfw.KEY_A) == glfw.PRESS):
            delta_pos = delta_pos + (self.speed * delta_time) * pyrr.Vector3([-1, 0, 0])
            # print("A pressed -> delta_pos = {}".format(delta_pos))
        if (glfw.get_key(glfw_context, glfw.KEY_D) == glfw.PRESS):
            delta_pos = delta_pos + (self.speed * delta_time) * pyrr.Vector3([1, 0, 0])
            # print("D pressed -> delta_pos = {}".format(delta_pos))

        self.camera.transform.position = self.camera.transform.position + delta_pos

