import glfw
import pyrr

# we don't work on a camera, we work on its transform
# but that is actually internal to the camera class
# from .transform import Transform
# from .camera import Camera

# update:
# free fly camera, as in our unity script, it's going to work
# for any gameObject with a FreeFlyCamera component (it works on the transform and not an actual camera).
from .transform import Transform

class FreeFlyCamera:

    def __init__(self, transform):
        self.transform = transform

        self.speed = 5          # 5 meters per seconds
        self.angular_speed = 30 # 30 degrees per seconds

        # there are different "approaches/models" for moving a camera.
        # - 1st attemp learnopengl:
        #   * in a single frame check for all keys that are pressed
        #   * if they are mapped to some direction, add/substract to the current position accordingly
        #   * multiply that by some speed and delta time

    def process_input(self, glfw_context, delta_time):
        # if we render to screen buffer, we shoud not check for window focus
        # window = glfw.get_window_user_pointer(context)
        delta_pos = pyrr.Vector3([0, 0, 0])

        # wasd qe for movement
        # if control is being pressed, use global positon rather than local
        right = self.transform.right
        up = self.transform.up
        forward = self.transform.forward

        translation_changed = False

        if (glfw.get_key(glfw_context, glfw.KEY_LEFT_CONTROL) == glfw.PRESS):
            right = pyrr.Vector3([1, 0, 0])
            up = pyrr.Vector3([0, 1, 0])
            forward = pyrr.Vector3([0, 0, 1])

        if (glfw.get_key(glfw_context, glfw.KEY_W) == glfw.PRESS):
            delta_pos = delta_pos + (self.speed * delta_time) * (-forward)
            translation_changed = True
        if (glfw.get_key(glfw_context, glfw.KEY_S) == glfw.PRESS):
            delta_pos = delta_pos + (self.speed * delta_time) * (forward)
            translation_changed = True
        if (glfw.get_key(glfw_context, glfw.KEY_A) == glfw.PRESS):
            delta_pos = delta_pos + (self.speed * delta_time) * (-right)
            translation_changed = True
        if (glfw.get_key(glfw_context, glfw.KEY_D) == glfw.PRESS):
            delta_pos = delta_pos + (self.speed * delta_time) * (right)
            translation_changed = True
        if (glfw.get_key(glfw_context, glfw.KEY_Q) == glfw.PRESS):
            delta_pos = delta_pos + (self.speed * delta_time) * (-up)
            translation_changed = True
        if (glfw.get_key(glfw_context, glfw.KEY_E) == glfw.PRESS):
            delta_pos = delta_pos + (self.speed * delta_time) * (up)
            translation_changed = True

        # DO NOT set the position if delta_pos is zero!
        # otherwise it will trigger generating the matrices all over again
        if translation_changed:
            self.transform.position = self.transform.position + delta_pos

        # what about rotations?
        # should they be local or global?
        # rotations in global space are weird if they are not done
        # in the same exact order, i.e once we have rotation along y for example
        # rotation along x looks very wrong because our engine is using RxRyRz
        delta_rot = pyrr.Vector3([0, 0, 0])

        # what these values should be to do local rotations?
        pitch = pyrr.Vector3([1, 0, 0])     # x rotation
        yaw = pyrr.Vector3([0, 1, 0])       # y rotation
        roll = pyrr.Vector3([0, 0, 1])
        # what do we get if instead of using global right, up, forward, we use the locals?
        # pitch = self.transform.right     # x rotation
        # yaw = self.transform.up       # y rotation
        # roll = self.transform.forward
        # it didn't work. seems a similar error to the one using globals.
        # what we want:
        # once we have a rotation in y or z, we want to rotate in x along world space
        # without having to care for the order of the rotations

        rotation_changed = False

        # using ikjl for rotation and uo for roll
        if (glfw.get_key(glfw_context, glfw.KEY_I) == glfw.PRESS):
            delta_rot = delta_rot + (self.angular_speed * delta_time) * (pitch)
            rotation_changed = True
        if (glfw.get_key(glfw_context, glfw.KEY_K) == glfw.PRESS):
            delta_rot = delta_rot + (self.angular_speed * delta_time) * (-pitch)
            rotation_changed = True

        if (glfw.get_key(glfw_context, glfw.KEY_J) == glfw.PRESS):
            delta_rot = delta_rot + (self.angular_speed * delta_time) * (yaw)
            rotation_changed = True
        if (glfw.get_key(glfw_context, glfw.KEY_L) == glfw.PRESS):
            delta_rot = delta_rot + (self.angular_speed * delta_time) * (-yaw)
            rotation_changed = True

        if (glfw.get_key(glfw_context, glfw.KEY_U) == glfw.PRESS):
            delta_rot = delta_rot + (self.angular_speed * delta_time) * (roll)
            rotation_changed = True
        if (glfw.get_key(glfw_context, glfw.KEY_O) == glfw.PRESS):
            delta_rot = delta_rot + (self.angular_speed * delta_time) * (-roll)
            rotation_changed = True

        if rotation_changed:
            self.transform.rotation = self.transform.rotation + delta_rot

