import imgui
import pyrr

class TransformGUI:

    def __init__(self, transform):
        self.transform = transform

    def draw(self):

        # transform position
        pos = self.transform.position.x, self.transform.position.y, self.transform.position.z
        # changed, pos = imgui.slider_float3("position", *pos, -100, 100)
        changed, pos = imgui.drag_float3("position", *pos, change_speed=0.01)
        if changed:
            self.transform.position = pyrr.Vector3([pos[0], pos[1], pos[2]])

        # transform rotation
        rotation = self.transform.rotation.x, self.transform.rotation.y, self.transform.rotation.z
        changed, rotation = imgui.drag_float3("rotation", *rotation)
        if changed:
            # print(pos)
            self.transform.rotation = pyrr.Vector3([rotation[0], rotation[1], rotation[2]])

        # transform scale
        scale = self.transform.scale.x, self.transform.scale.y, self.transform.scale.z
        changed, scale = imgui.drag_float3("scale", *scale, change_speed=0.01)
        if changed:
            # print(pos)
            self.transform.scale = pyrr.Vector3([scale[0], scale[1], scale[2]])

