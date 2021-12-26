import imgui
import pyrr

from .component_gui import ComponentGUI

class CameraGUI(ComponentGUI):

    def __init__(self, camera):
        self.camera = camera

    def draw(self):

        # gl.glClearColor(0.705, 0.980, 0.992, 1)# light blue
        changed, clear_color = imgui.color_edit3("clear color", *self.camera.clear_color)
        if changed:
            self.camera.clear_color = clear_color

        changed, vfov = imgui.slider_float("fov", self.camera.vfov, 0.01, 180)
        if (changed):
            self.camera.vfov = vfov

        changed, near = imgui.drag_float("near", self.camera.near, change_speed=0.01, min_value=0.001, max_value=100)#; imgui.same_line()
        if (changed):
            self.camera.near = near

        changed, far = imgui.drag_float("far", self.camera.far, change_speed=0.1, min_value=near+1, max_value=1000)
        if (changed):
            self.camera.far = far
