import imgui
import pyrr

class TransformGUI:

    def __init__(self, transform):
        self.transform = transform

    # imgui has the problem/feature that the internal id of a widget is set equal to its label.
    # labels are scoped to its window but if we want to re-use a label within a window, we will
    # have to add '##<something>' at the end of the label.
    # example for reusing the label 'pos' -> 'pos##<unique_id>'
    def draw(self):

        imgui.text("object={}".format(self.transform.game_object.name))

        # transform position
        pos = self.transform.position.x, self.transform.position.y, self.transform.position.z
        # changed, pos = imgui.slider_float3("position", *pos, -100, 100)
        label = "position##{}".format(self.transform.game_object.id)
        changed, pos = imgui.drag_float3(label, *pos, change_speed=0.01)
        if changed:
            self.transform.position = pyrr.Vector3([pos[0], pos[1], pos[2]])

        # transform rotation
        label = "rotation##{}".format(self.transform.game_object.id)
        rotation = self.transform.rotation.x, self.transform.rotation.y, self.transform.rotation.z
        changed, rotation = imgui.drag_float3(label, *rotation)
        if changed:
            # print(pos)
            self.transform.rotation = pyrr.Vector3([rotation[0], rotation[1], rotation[2]])

        # transform scale
        label = "scale##{}".format(self.transform.game_object.id)
        scale = self.transform.scale.x, self.transform.scale.y, self.transform.scale.z
        changed, scale = imgui.drag_float3(label, *scale, change_speed=0.01)
        if changed:
            # print(pos)
            self.transform.scale = pyrr.Vector3([scale[0], scale[1], scale[2]])

        # for debugging
        imgui.text("right={}".format(self.transform.right))
        imgui.text("up={}".format(self.transform.up))
        imgui.text("forward={}".format(self.transform.forward))
