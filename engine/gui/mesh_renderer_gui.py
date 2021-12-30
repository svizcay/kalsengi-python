import imgui

from .component_gui import ComponentGUI
import engine.material_manager

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

            # showing combobox with list of materials
            available_materials = engine.material_manager.get_materials_ids()
            material_values = [mat[1] for mat in available_materials]
            current_material_uuid = engine.material_manager.get_material_id_by_ref(self.mesh_renderer.material)

            current_material_selected_index = None
            for idx, (uuid, _) in enumerate(available_materials):
                if uuid == current_material_uuid:
                    current_material_selected_index = idx

            changed, opt_index = imgui.combo("material", current_material_selected_index, material_values)
            if changed:
                selected_uuid,_ = available_materials[opt_index]
                self.mesh_renderer.material = engine.material_manager.get_from_id(selected_uuid)

            self.mesh_renderer.material.gui.draw()


