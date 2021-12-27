import imgui
import OpenGL.GL as gl

class MaterialGUI:

    def __init__(self, material):
        self.material = material
        self.material.gui = self

    def draw(self):
        # draw uniform slots
        # how to know when to use a color widget and when to use a float?
        # let's follow the convention uniform name needs to have "color"
        # on it
        for uniform_name in self.material.uniforms:
            uniform = self.material.uniforms[uniform_name]
            imgui.text("{} type={}".format(uniform["name"], uniform["type"]))
            type_ = uniform["type"]
            if type_ == gl.GL_FLOAT_VEC3:
                if "color" in uniform["name"]:
                    value = uniform["value"]
                    changed, color = imgui.color_edit3(uniform["name"], *value)
                    if changed:
                        # set uniform back using the material
                        # self.camera.clear_color = clear_color
                        self.material.set_uniform(uniform["name"], *color)

