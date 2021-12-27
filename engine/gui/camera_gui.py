import imgui
import pyrr

from .component_gui import ComponentGUI

class CameraGUI(ComponentGUI):

    def __init__(self, camera):
        self.camera = camera

    def draw(self):

        expanded, visible = imgui.collapsing_header(self.camera.name, flags=imgui.TREE_NODE_DEFAULT_OPEN)
        if expanded:

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

            expanded, visible = imgui.collapsing_header("matrices")
            if expanded:
                imgui.text("view matrix")
                # we need to transpose it because
                # we consider its internal representation to be col major
                # and we want to display it per rows
                view_mat = self.camera.transform.view_mat.T
                label = "view row 0##{}".format(self.camera.game_object.id)
                _, _ = imgui.input_float4(label, *view_mat[0], flags=imgui.INPUT_TEXT_READ_ONLY)
                label = "view row 1##{}".format(self.camera.game_object.id)
                _, _ = imgui.input_float4(label, *view_mat[1], flags=imgui.INPUT_TEXT_READ_ONLY)
                label = "view row 2##{}".format(self.camera.game_object.id)
                _, _ = imgui.input_float4(label, *view_mat[2], flags=imgui.INPUT_TEXT_READ_ONLY)
                label = "view row 3##{}".format(self.camera.game_object.id)
                _, _ = imgui.input_float4(label, *view_mat[3], flags=imgui.INPUT_TEXT_READ_ONLY)

                imgui.separator()

                imgui.text("projection matrix")
                proj_mat = self.camera.projection.T
                label = "projection row 0##{}".format(self.camera.game_object.id)
                _, _ = imgui.input_float4(label, *proj_mat[0], flags=imgui.INPUT_TEXT_READ_ONLY)
                label = "projection row 1##{}".format(self.camera.game_object.id)
                _, _ = imgui.input_float4(label, *proj_mat[1], flags=imgui.INPUT_TEXT_READ_ONLY)
                label = "projection row 2##{}".format(self.camera.game_object.id)
                _, _ = imgui.input_float4(label, *proj_mat[2], flags=imgui.INPUT_TEXT_READ_ONLY)
                label = "projection row 3##{}".format(self.camera.game_object.id)
                _, _ = imgui.input_float4(label, *proj_mat[3], flags=imgui.INPUT_TEXT_READ_ONLY)
