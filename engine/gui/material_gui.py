import imgui
import OpenGL.GL as gl

from .component_gui import ComponentGUI
from engine import texture_manager

class MaterialGUI:

    def __init__(self, material):
        self.material = material
        self.material.gui = self
        self._set_labels()

    def draw(self):
        # draw uniform slots
        # how to know when to use a color widget and when to use a float?
        # let's follow the convention uniform name needs to have "color"
        # on it
        for uniform_name in self.material.uniforms:
            uniform = self.material.uniforms[uniform_name]
            self._draw_uniform_entry(uniform)

        for attrib_name in self.material.vertex_attribs:
            attrib = self.material.vertex_attribs[attrib_name]
            self._draw_vertex_attrib_entry(attrib)

        expanded, visible = imgui.collapsing_header(self.discarded_uniforms_label)
        if expanded:
            for uniform_name in self.material.discarded_uniforms:
                uniform = self.material.discarded_uniforms[uniform_name]
                self._draw_uniform_entry(uniform)

        expanded, visible = imgui.collapsing_header(self.discarded_vertex_attribs_label)
        if expanded:
            for attrib_name in self.material.discarded_vertex_attribs:
                attrib = self.material.discarded_vertex_attribs[attrib_name]
                self._draw_vertex_attrib_entry(attrib)

    def _set_labels(self):
        self.discarded_uniforms_label = ComponentGUI.get_unique_imgui_label(
            "discarded uniforms",
            # a material doesn not belong to a game object!
            # we can not use game object id
            # self.material.game_object.id,
            self.material.uuid,
            self.__class__.__name__)
        self.vertex_attribs_label = ComponentGUI.get_unique_imgui_label(
            "vertex attribs",
            self.material.uuid,
            self.__class__.__name__)
        self.discarded_vertex_attribs_label = ComponentGUI.get_unique_imgui_label(
            "discarded vertex attribs",
            self.material.uuid,
            self.__class__.__name__)

    def _draw_uniform_entry(self, uniform:dict):
        if not uniform["name"].startswith("_"):
            type_ = uniform["type"]

            # draw the right widget based on the type of uniform
            if type_ == gl.GL_FLOAT_VEC3:
                if "color" in uniform["name"]:
                    value = uniform["value"] # value is stored as a list
                    # i think i need to make the label unique
                    label = ComponentGUI.get_unique_imgui_label(
                        uniform["name"],
                        self.material.uuid,
                        self.__class__.__name__
                    )
                    changed, color = imgui.color_edit3(label, *value)
                    if changed:
                        # set uniform back using the material
                        # self.camera.clear_color = clear_color
                        # we can not just call material.set_uniform()
                        # here because there might be another glProgram bound at this time
                        # and now set_uniform is not binding the program
                        # we need to "submit" this change
                        # self.material.set_uniform(uniform["name"], color)
                        self.material.set_value(uniform["name"], color)
            elif type_ == gl.GL_FLOAT:
                # if starts with slider -> draw slider
                if uniform["name"].startswith("slider"):
                    tokens = uniform["name"].split('_')
                    min_val = float(tokens[1])
                    max_val = float(tokens[2])
                    label = "_".join(tokens[3:])
                    current_val = uniform["value"][0] if "value" in uniform else min_val
                    # there is no easy way to know in advance what's the default value
                    changed, value = imgui.slider_float(label, current_val, min_val, max_val)
                    if changed:
                        self.material.set_value(uniform["name"], [value])
                else:
                    # there is no easy way to know in advance what's the default value
                    # we can not set it fixed to the var name
                    current_val = uniform["value"][0] if "value" in uniform else 0.0
                    changed, value = imgui.drag_float(uniform["name"], current_val, change_speed=0.01)
                    if changed:
                        self.material.set_value(uniform["name"], [value])
                # otherwise just draw a float input
            elif type_ == gl.GL_SAMPLER_2D:
                # list all available textures
                # showing combobox with list of materials
                available_textures = texture_manager.get_textures_ids()
                texture_values = [tex[1] for tex in available_textures]

                # get the current texture used in the material for that texture sampler
                # current_texture_uuid = texture_manager.get_texture_id_by_ref(self.mesh_renderer.material)
                current_texture = None
                if self.material.textures is not None:
                    for texture_entry in self.material.textures:
                        if texture_entry["name"] == uniform["name"]:
                            current_texture = texture_entry["texture"]
                            break
                current_texture_uuid = 0 if current_texture is None else current_texture.uuid

                current_texture_selected_index = None
                for idx, (uuid, _) in enumerate(available_textures):
                    if uuid == current_texture_uuid:
                        current_texture_selected_index = idx

                changed, opt_index = imgui.combo(uniform["name"], current_texture_selected_index, texture_values)
                if changed:
                    selected_uuid,_ = available_textures[opt_index]
                    selected_texture = texture_manager.get_from_id(selected_uuid)
                    self.material.replace_texture(uniform["name"], selected_texture)
                    # self.mesh_renderer.material = engine.material_manager.get_from_id(selected_uuid)
            else:
                # we don't have a widget for that type.
                # just display the info
                imgui.text("{} type={}".format(uniform["name"], uniform["type"]))

    def _draw_vertex_attrib_entry(self, vertex_attrib:dict):
        imgui.text("{} type={} size={}".format(vertex_attrib["name"], vertex_attrib["type"], vertex_attrib["size"]))
