import imgui

from .component_gui import ComponentGUI

class MeshRendererGUI(ComponentGUI):

    def __init__(self, mesh_renderer):
        self.mesh_renderer = mesh_renderer

    def draw(self):

        expanded, visible = imgui.collapsing_header(self.mesh_renderer.name, flags=imgui.TREE_NODE_DEFAULT_OPEN)
        if expanded:
            # the gui for the mesh renderer needs to show a combobox for
            # the material selection
            # and the material gui itself
            # plus also some mesh info like data available
            self.mesh_renderer.material.gui.draw()


