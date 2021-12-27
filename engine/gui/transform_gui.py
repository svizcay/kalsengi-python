import imgui
import pyrr
import math

# it's interesting to see that even though this script works
# on a Transform, we don't need to import the module
# becuse of python dynamic typing.
# As long as we don't create an instance of a transform, we don't need to import anything

# some of the possible imgui wdigets to use:
#
# has the issue that we need to specify min and max values
# changed, pos = imgui.slider_float3("position", *pos, -100, 100)
#
# the one that we are using now.
# works well to set values by dragging it + setting them manually
# changed, pos = imgui.drag_float3(position_label, *pos, change_speed=0.01)
#
# i think this only work by writing the value
# changed, pos = imgui.input_float3(label, *self.transform.local_euler_angles, flags=imgui.INPUT_TEXT_READ_ONLY)

from .component_gui import ComponentGUI

class TransformGUI:

    def __init__(self, transform):
        self.transform = transform
        self._set_labels()

    # imgui has the problem/feature that the internal id of a widget is set equal to its label.
    # labels are scoped to its window but if we want to re-use a label within a window, we will
    # have to add '##<something>' at the end of the label.
    # example for reusing the label 'pos' -> 'pos##<unique_id>'
    # on top of object id, we can add the classname

    # imgui shows the labels at the right of the widgets.
    # i don't like it much. let's try to display them at the left.
    # the strategy is as follows:
    # rather than imgui.input_<type>(label, val)
    # use: imgui.text(label); imgui.same_line(); imgui.input_type(no_label, val)
    # a) i dind't like the result. things are not aligned well.
    def draw(self):

        changed, name = imgui.input_text(self.name_label, self.transform.game_object.name, 255)
        if changed:
            self.transform.game_object.name = name

        expanded, visible = imgui.collapsing_header(self.transform_label, flags=imgui.TREE_NODE_DEFAULT_OPEN)
        if expanded:
            pos = self.transform.local_position.x, self.transform.local_position.y, self.transform.local_position.z
            changed, pos = imgui.drag_float3(self.position_label, *pos, change_speed=0.01)
            if changed:
                self.transform.local_position = pyrr.Vector3([pos[0], pos[1], pos[2]])

            changed, rotation = imgui.drag_float3(self.rotation_label, *self.transform.local_euler_angles)
            if changed:
                self.transform.local_euler_angles = pyrr.Vector3([rotation[0], rotation[1], rotation[2]])

            scale = self.transform.local_scale.x, self.transform.local_scale.y, self.transform.local_scale.z
            changed, scale = imgui.drag_float3(self.scale_label, *scale, change_speed=0.01)
            if changed:
                self.transform.local_scale = pyrr.Vector3([scale[0], scale[1], scale[2]])

        expanded, visible = imgui.collapsing_header(self.matrices_label)
        if expanded:
            # we are considering matrix are stored by cols internally, i.e mat[0] returns the first col
            # but we want to display them per rows (as in math)
            # so we transpose them
            translation_mat = self.transform.translation_mat.T
            TransformGUI.matrix_text("translation", translation_mat, self.transform.game_object.id)

            imgui.separator()
            rotation_mat = self.transform.rotation_mat.T
            TransformGUI.matrix_text("rotation", rotation_mat, self.transform.game_object.id)

    @staticmethod
    def matrix_text(label, mat, unique_id):
        # matrix needs to be transposed already so each element represents a row
        """ to display matrix as read only """
        imgui.text("{} matrix".format(label))
        row_1_label = "{} row 0##{}".format(label, unique_id)
        _, _ = imgui.input_float4(row_1_label, *mat[0], flags=imgui.INPUT_TEXT_READ_ONLY)
        row_2_label = "{} row 1##{}".format(label, unique_id)
        _, _ = imgui.input_float4(row_2_label, *mat[1], flags=imgui.INPUT_TEXT_READ_ONLY)
        row_3_label = "{} row 2##{}".format(label, unique_id)
        _, _ = imgui.input_float4(row_3_label, *mat[2], flags=imgui.INPUT_TEXT_READ_ONLY)
        row_4_label = "{} row 3##{}".format(label, unique_id)
        _, _ = imgui.input_float4(row_4_label, *mat[3], flags=imgui.INPUT_TEXT_READ_ONLY)

    def _set_labels(self):
        self.name_label = ComponentGUI.get_unique_imgui_label(
            "name",
            self.transform.game_object.id,
            self.__class__.__name__)
        self.transform_label = ComponentGUI.get_unique_imgui_label(
            "transform",
            self.transform.game_object.id,
            self.__class__.__name__)
        self.position_label = ComponentGUI.get_unique_imgui_label(
            "position",
            self.transform.game_object.id,
            self.__class__.__name__)
        self.rotation_label = ComponentGUI.get_unique_imgui_label(
            "rotation",
            self.transform.game_object.id,
            self.__class__.__name__)
        self.scale_label = ComponentGUI.get_unique_imgui_label(
            "scale",
            self.transform.game_object.id,
            self.__class__.__name__)
        self.matrices_label = ComponentGUI.get_unique_imgui_label(
            "matrices",
            self.transform.game_object.id,
            self.__class__.__name__)

