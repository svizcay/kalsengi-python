import imgui
import pyrr
import math

class TransformGUI:

    def __init__(self, transform):
        self.transform = transform

    # imgui has the problem/feature that the internal id of a widget is set equal to its label.
    # labels are scoped to its window but if we want to re-use a label within a window, we will
    # have to add '##<something>' at the end of the label.
    # example for reusing the label 'pos' -> 'pos##<unique_id>'

    # imgui shows the labels at the right of the widgets.
    # i don't like it much. let's try to display them at the left.
    # the strategy is as follows:
    # rather than imgui.input_<type>(label, val)
    # use: imgui.text(label); imgui.same_line(); imgui.input_type(no_label, val)
    # a) i dind't like the result. things are not aligned well.
    def draw(self):

        # imgui.text("object={}".format(self.transform.game_object.name))

        label = "name##{}".format(self.transform.game_object.id)
        changed, name = imgui.input_text(label, self.transform.game_object.name, 255)
        if changed:
            self.transform.game_object.name = name

        expanded, visible = imgui.collapsing_header("transform", flags=imgui.TREE_NODE_DEFAULT_OPEN)
        if expanded:

            # transform position
            # pos = self.transform.position.x, self.transform.position.y, self.transform.position.z
            pos = self.transform.local_position.x, self.transform.local_position.y, self.transform.local_position.z
            # changed, pos = imgui.slider_float3("position", *pos, -100, 100)
            label = "position##{}".format(self.transform.game_object.id)
            changed, pos = imgui.drag_float3(label, *pos, change_speed=0.01)
            if changed:
                self.transform.local_position = pyrr.Vector3([pos[0], pos[1], pos[2]])

            # disabling rotation gui until we manage to read euler angles from quaternion/rotation mat
            # for now, we can maybe just display the quaternion
            label = "rotation##{}".format(self.transform.game_object.id)
            # imgui.text("rotation={}".format(self.transform.local_rotation))
            # changed, pos = imgui.input_float4(label, *self.transform.local_rotation, flags=imgui.INPUT_TEXT_READ_ONLY)
            # changed, pos = imgui.input_float3(label, *self.transform.local_euler_angles, flags=imgui.INPUT_TEXT_READ_ONLY)
            changed, rotation = imgui.drag_float3(label, *self.transform.local_euler_angles)
            if changed:
                self.transform.local_euler_angles = pyrr.Vector3([rotation[0], rotation[1], rotation[2]])

            # # transform rotation
            # label = "rotation##{}".format(self.transform.game_object.id)
            # rotation = self.transform.rotation.x, self.transform.rotation.y, self.transform.rotation.z
            # changed, rotation = imgui.drag_float3(label, *rotation)
            # if changed:
            #     # print(pos)
            #     self.transform.rotation = pyrr.Vector3([rotation[0], rotation[1], rotation[2]])

            # transform scale
            label = "scale##{}".format(self.transform.game_object.id)
            scale = self.transform.local_scale.x, self.transform.local_scale.y, self.transform.local_scale.z
            changed, scale = imgui.drag_float3(label, *scale, change_speed=0.01)
            if changed:
                # print(pos)
                self.transform.local_scale = pyrr.Vector3([scale[0], scale[1], scale[2]])

        expanded, visible = imgui.collapsing_header("matrices")
        if expanded:
            # we are considering matrix are stored by cols internally, i.e mat[0] returns the first col
            # but we want to display them per rows (as in math)
            # so we transpose them
            imgui.text("translation matrix")
            translation_mat = self.transform.translation_mat.T
            label = "translation row 0##{}".format(self.transform.game_object.id)
            _, _ = imgui.input_float4(label, *translation_mat[0], flags=imgui.INPUT_TEXT_READ_ONLY)
            label = "translation row 1##{}".format(self.transform.game_object.id)
            _, _ = imgui.input_float4(label, *translation_mat[1], flags=imgui.INPUT_TEXT_READ_ONLY)
            label = "translation row 2##{}".format(self.transform.game_object.id)
            _, _ = imgui.input_float4(label, *translation_mat[2], flags=imgui.INPUT_TEXT_READ_ONLY)
            label = "translation row 3##{}".format(self.transform.game_object.id)
            _, _ = imgui.input_float4(label, *translation_mat[3], flags=imgui.INPUT_TEXT_READ_ONLY)

            imgui.separator()
            # we are considering matrix are stored by cols internally, i.e mat[0] returns the first col
            # but we want to display them per rows (as in math)
            # so we transpose them
            imgui.text("rotation matrix")
            rotation_mat = self.transform.rotation_mat.T
            label = "rotation row 0##{}".format(self.transform.game_object.id)
            _, _ = imgui.input_float4(label, *rotation_mat[0], flags=imgui.INPUT_TEXT_READ_ONLY)
            label = "rotation row 1##{}".format(self.transform.game_object.id)
            _, _ = imgui.input_float4(label, *rotation_mat[1], flags=imgui.INPUT_TEXT_READ_ONLY)
            label = "rotation row 2##{}".format(self.transform.game_object.id)
            _, _ = imgui.input_float4(label, *rotation_mat[2], flags=imgui.INPUT_TEXT_READ_ONLY)
            label = "rotation row 3##{}".format(self.transform.game_object.id)
            _, _ = imgui.input_float4(label, *rotation_mat[3], flags=imgui.INPUT_TEXT_READ_ONLY)

        # rad = math.asin(rotation_mat[0,2])
        # grad = math.degrees(rad)
        # imgui.text("asin={} rad and in degrees={}".format(rad, grad))


        # for debugging
        # imgui.text("right={}".format(self.transform.right))
        # imgui.text("up={}".format(self.transform.up))
        # imgui.text("forward={}".format(self.transform.forward))

        # using label to the left of the widgets
        # imgui.text("name")
        # imgui.same_line()
        # label = "##{}".format(self.transform.game_object.id)
        # changed, name = imgui.input_text(label, self.transform.game_object.name, 255)
        # if changed:
        #     self.transform.game_object.name = name

        # pos = self.transform.local_position.x, self.transform.local_position.y, self.transform.local_position.z
        # imgui.text("position")
        # imgui.same_line()
        # label = "##{}".format(self.transform.game_object.id)
        # # changed, pos = imgui.slider_float3("position", *pos, -100, 100)
        # changed, pos = imgui.drag_float3(label, *pos, change_speed=0.01)
        # if changed:
        #     self.transform.local_position = pyrr.Vector3([pos[0], pos[1], pos[2]])

        # imgui.text("rotation={}".format(self.transform.local_rotation))

        # imgui.text("scale")
        # imgui.same_line()
        # label = "##{}".format(self.transform.game_object.id)
        # scale = self.transform.local_scale.x, self.transform.local_scale.y, self.transform.local_scale.z
        # changed, scale = imgui.drag_float3(label, *scale, change_speed=0.01)
        # if changed:
        #     # print(pos)
        #     self.transform.local_scale = pyrr.Vector3([scale[0], scale[1], scale[2]])
