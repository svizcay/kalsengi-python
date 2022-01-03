import pyrr

# i think it's a better practise to use absolute import path
# from .component import Component
from engine.components.component import Component
from engine.gui.camera_gui import CameraGUI

# as a Component, this Camera needs to be added to some game object.

class Camera(Component):

    # we would like to have the right values for aspect ratio
    # and we dont want to pass them explicitly

    # we are going to protect the projection matrix
    # so when this is read and it's dirty, we recalculate it

    # similarly with every camera parameter,
    # we are going to make them properties so they run a method
    # that dirty the matrices appropiately

    # the camera will have an internal transform.
    # the view matrix is going to be linked to that

    # we should treat the aspect ratio differently
    # and make sure it's always right with the size of the rendering viewport
    def __init__(self, game_object, aspect_ratio = 16/9):
        super().__init__(game_object)

        self._vfov = 60
        self._aspect_ratio = aspect_ratio
        self._near = 0.01
        self._far = 1000

        self.clear_color = (0.705, 0.980, 0.992) # light blue

        # whenever we have a class that inherits from Component
        # and we DO have a valid component gui implemented, then set it
        self.gui = CameraGUI(self)
        self.name = "camera"

        # shortcut for now
        self.transform = self.game_object.transform

        self._set_projection_matrix()

    # internal getters
    @property
    def vfov(self):
        return self._vfov

    @property
    def aspect_ratio(self):
        return self._aspect_ratio

    @property
    def near(self):
        return self._near

    @property
    def far(self):
        return self._far

    # internal setters
    @vfov.setter
    def vfov(self, value):
        self._vfov = value
        self._projection_dirty = True
        self._view_projection_dirty = True

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        self._aspect_ratio = value
        self._projection_dirty = True
        self._view_projection_dirty = True

    @near.setter
    def near(self, value):
        self._near = value
        self._projection_dirty = True
        self._view_projection_dirty = True

    @far.setter
    def far(self, value):
        self._far = value
        self._projection_dirty = True
        self._view_projection_dirty = True

    # public api (getters)
    @property
    def projection(self):
        if (self._projection_dirty):
            self._set_projection_matrix()
        return self._projection

    @property
    def view_projection(self):
        if self.view_projection_dirty:
            # using the property getters to get up to date values
            # and to update dirty flags on the way
            self._view_projection = pyrr.matrix44.multiply(
                self.transform.view_mat, self.projection
            )
        return self._view_projection

    @property
    def view_projection_dirty(self):
        return self._projection_dirty or self.transform.view_dirty

    def look_at(self, eye, center, up):
        pass

    def _set_projection_matrix(self):
        self._projection = pyrr.matrix44.create_perspective_projection_matrix(
                self._vfov,
                self._aspect_ratio,
                self._near,
                self._far
        )
        self._projection_dirty = False




