import imgui
from .component_gui import ComponentGUI

# from ..engine.components import LightType
import engine.components.light as light_module

class LightGUI(ComponentGUI):

    def __init__(self, light):
        self.light = light

    def draw(self):
        expanded, visible = imgui.collapsing_header(self.light.name, flags=imgui.TREE_NODE_DEFAULT_OPEN)
        if expanded:

            changed, color = imgui.color_edit3("light color", *self.light.color)
            if changed:
                self.light.color = color

            # light_type_values = [str(e.value) for e in light_module.LightType]
            # enum has e.value assigned starting at 1
            light_type_values = [e.name for e in light_module.LightType]

            # clicked, light_type = imgui.combo("type", self.light.light_type, light_type_values)
            # print("light type: {}".format(self.light.light_type))
            light_type_current_index = self.light.light_type - 1    # light.light_type is a 1-based index enum
            changed, opt_index = imgui.combo("type", light_type_current_index, light_type_values)
            if changed:
                # print("light type: changed to value {}".format(light_type))
                self.light.light_type = (opt_index + 1)


