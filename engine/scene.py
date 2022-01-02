import inspect

import imgui
import pyrr
import OpenGL.GL as gl
import random

from .gui import GameObjectGUI
# it seeems we don't need to import a module/class name if we are not going to instantiate an object
# but in this case, when referencing the class type, we need it
from .components import MeshRenderer
from .components import Camera
from .components import Light
from .gizmo import Gizmo, CameraGizmo

from .base_mesh import GridMesh

from . import shader_manager
from . import material_manager

# for testing
from engine.gl_uniform import gl_uniform_type_to_f


# order of events:
# update gets called before rendering

class Scene:

    def __init__(self):
        self.game_objects = []
        self.cameras = []
        self.light_sources = []
        self.selected = None
        self.expanded = []
        self.guis = {}
        self.gizmo = Gizmo()
        self.camera_gizmo = CameraGizmo()

        # for debugging. it should not be a list
        # self.selected_flags = []

        # testing grid
        grid_mesh = GridMesh()
        grid_material = material_manager.get_from_name("flat_color_uniform_far_clipped")
        self.grid_renderer = MeshRenderer(
            None,
            grid_mesh,
            grid_material
        )
        self.grid_clip_distance = 75.0

        # test calling useProgram multiple times
        self.nr_calls_to_glUseProgram = 100
        self.test_multiple_calls_glUseProgram = False
        self.alternate_programs_ids = True

        # test calling glUniform multiple times
        self.nr_calls_to_glUniform = 2000
        self.test_multiple_calls_glUniform = True
        self.test_call_glUniform_directly = False

    def add_game_object(self, game_object):
        self.game_objects.append(game_object)

        # check if game object was a camera
        # NOTE: this has the issue that it doesn't take into account
        # the fact that we can add a camera componet later!!
        # the same problem is going to happen for any special game object as lights
        camera = game_object.get_component(Camera)
        light_source = game_object.get_component(Light)
        if camera is not None:
            self.cameras.append(camera)
        if light_source is not None:
            self.light_sources.append(light_source)

        gui = GameObjectGUI(game_object)
        self.guis[game_object.id] = gui

        # whenever we add a game object to the scene, we are going to create its editor gui here

        self.expanded.append(False)

        # for debugging
        # self.selected_flags.append(False)

    def update(self):
        # update components if they have an update method
        for game_obj in self.game_objects:
            for component in game_obj.components:
                # inspect(object[,predicate]) returns a list of tuples name value
                # of all members of the object
                # print("component {} members:".format(component))
                if component.enabled:
                    for name, value in inspect.getmembers(component):
                        if name == "update":
                            component.update()
                        # print(name)


    def draw_scene(self, camera, is_editor_camera = True):
        """ this method will call draw on all game objects """
        # in general: for ech game object, activate its shader and draw the object.
        # but we should sort game objects by material first


        # testing grid
        if is_editor_camera:

            # settings for drawing the grid
            imgui.begin("grid")
            changed, grid_clip_distance = imgui.slider_float("grid clip", self.grid_clip_distance, 0.0001, 100)
            if changed:
                self.grid_clip_distance = grid_clip_distance

            # tests
            changed, value = imgui.drag_int("nr calls glUseProgram", self.nr_calls_to_glUseProgram)
            if changed:
                self.nr_calls_to_glUseProgram = value
            clicked, state = imgui.checkbox("test multiple calls glUseProgram", self.test_multiple_calls_glUseProgram)
            if clicked:
                self.test_multiple_calls_glUseProgram = state

            clicked, state = imgui.checkbox("alternate programs", self.alternate_programs_ids)
            if clicked:
                self.alternate_programs_ids = state

            clicked, state = imgui.checkbox("test multiple calls glUniform", self.test_multiple_calls_glUniform)
            if clicked:
                self.test_multiple_calls_glUniform = state

            clicked, state = imgui.checkbox("call glUniform directly", self.test_call_glUniform_directly)
            if clicked:
                self.test_call_glUniform_directly = state

            changed, value = imgui.drag_int("nr calls glUniform", self.nr_calls_to_glUniform)
            if changed:
                self.nr_calls_to_glUniform = value

            imgui.end()

            gl.glLineWidth(1)
            self.grid_renderer.material.use()
            # the grid needs to move with the camera in the xy plane
            # actually not exactly like that.
            # it needs to move but at integer intervals
            camera_pos = camera.transform.position
            camera_pos.x = int(camera_pos.x)
            camera_pos.y = 0
            camera_pos.z = int(camera_pos.z)
            mvp = pyrr.matrix44.multiply(
                pyrr.matrix44.multiply(pyrr.matrix44.create_from_translation(camera_pos), camera.transform.view_mat),
                camera.projection)
            # we should not use the renderer to set uniforms!!
            self.grid_renderer.material.set_uniform("mvp", mvp)
            self.grid_renderer.material.set_uniform("clip_distance", self.grid_clip_distance)
            self.grid_renderer.render()
            gl.glLineWidth(5)


        # rather than interating directly through the list of game objects,
        # we need to find what materials they are using and render them by grouping them
        # by materials

        # testing code:
        # let's see if opengl is smart enough to realize we are binding the same
        # opengl shader program by binding it multiple times
        material_to_test = material_manager.get_from_name("flat_color_uniform")
        alternative_material_to_test = material_manager.get_from_name("mix_textures_color")
        if  self.test_multiple_calls_glUseProgram:
            for i in range(self.nr_calls_to_glUseProgram):
                if self.alternate_programs_ids:
                    if i % 2 == 0:
                        material_to_test.use()
                    else:
                        alternative_material_to_test.use()
                else:
                    material_to_test.use()

        if self.test_multiple_calls_glUniform:
            material_to_test.use()
            for i in range(self.nr_calls_to_glUniform):
                r = random.random()
                g = 0.0#random.random()
                b = 0.0#random.random()
                color = [r,g,b]
                if self.test_call_glUniform_directly:
                    # is it checking the key in the dict what makes it slow?
                    # a) no. it's still fast calling directly even looking at the dict
                    # is it when we call isinstance?
                    # a) no. it's still faster than calling our wrapper
                    # is it calling the nest dict?
                    # no..finding the parent function gl_uniform_type_to_f was not the problem
                    # is calculating the lenght of the nr of parameters?
                    # no. it was still faster
                    # maybe it's the packing unpacking of the parameters
                    # maybe we are creating new lists
                    # how many times we pack/unpack the parameters?
                    # - when they are passed to set_only_uniforms, the list is expanded at call time
                    # and they are grouped into a list when they are received
                    # it's around 5 to 6 times.
                    # and yes, this is one of the factors...it went down from 120
                    # to 90 but still not as bad as 40 when using or wrapper
                    if "color" in material_to_test.uniforms:
                        loc = material_to_test.uniforms["color"]["loc"]
                        type_ = material_to_test.uniforms["color"]["type"]
                        function_wrapper = gl_uniform_type_to_f[gl.GL_FLOAT_VEC3]
                        nr_values = len(color)
                        first_unpacking = [*color]    # when calling set_only_uniform
                        second_unpacking = [*first_unpacking]
                        third_unpacking = [*second_unpacking]
                        forth_unpacking = [*third_unpacking]
                        fith_unpacking = [*forth_unpacking]
                        if isinstance(r, float):
                            gl.glUniform3f(loc, r, 0.0, 0.0)
                else:
                    material_to_test.set_only_uniform("color", r, 0.0, 0.0)


        game_objects_per_material = {}
        for game_obj in self.game_objects:
            for component in game_obj.components:
                if isinstance(component, MeshRenderer):
                    material = component.material
                    if material not in game_objects_per_material:
                        # create the list of game objects for this material
                        game_objects_per_material[material] = []
                    game_objects_per_material[material].append(game_obj)

        for material in game_objects_per_material:
            material.use()
            for game_obj in game_objects_per_material[material]:
                for component in game_obj.components:
                    if isinstance(component, MeshRenderer):
                        mvp = pyrr.matrix44.multiply(
                            pyrr.matrix44.multiply(
                                game_obj.transform.model_mat,
                                camera.transform.view_mat),
                            camera.projection)
                        material.set_uniform("mvp", mvp)
                        material.set_uniform("model", game_obj.transform.model_mat)
                        material.set_uniform("camera_pos", *camera.transform.position)

                        # if the material uses textures,
                        # we need to make sure they are bound at the right texture units.
                        # the material knows already which texture unit to use (that was set
                        # initially using the uniform). but we need to ensure the right texture
                        # is there.
                        # self.texture1.bind()
                        # self.texture2.bind(1)
                        # therefore, material needs to know the textures is going to use

                        if len(self.light_sources) > 0:
                            # when passing uniforms, we need to treat the data as simple as possible
                            # i.e, rather than a pyrr.vector or python array, expand them
                            # to a comma separated invidual floats
                            material.set_uniform("light_pos", *self.light_sources[0].position)
                            material.set_uniform("light_color", *self.light_sources[0].color)

                        # now we can ask the meshRenderer to draw the geometry
                        component.render()

        # for game_obj in self.game_objects:
        #     for component in game_obj.components:
        #         if isinstance(component, MeshRenderer):
        #             # we should not use the MeshRenderer to activate a material program.
        #             # we should activate the material outside this loop and render
        #             # all objects that have the same material!
        #             # we are bypassing the material here and the idea, is that
        #             # we might want to change the material attached to the MeshRenderer in runtime
        #             # ALSO, we should not set material's uniforms using the mesh renderer
        #             component.shader.use()
        #             # this should be avoided and done only when there are changes
        #             # to the matrices.
        #             # the same with setting the uniform. we should set them only if they are dirty
        #             mvp = pyrr.matrix44.multiply(
        #                 pyrr.matrix44.multiply(
        #                     game_obj.transform.model_mat,
        #                     camera.transform.view_mat),
        #                 camera.projection)
        #             # it doesn't seem right that the mesh renderer has the
        #             # interface to set the uniform and forward it to the 'material'
        #             # double check what's the order here
        #             # DO NOT set uniforms using the MeshRenderer!
        #             # we should set uniforms using the material class
        #             component.set_uniform("mvp", mvp)
        #             component.set_uniform("model", game_obj.transform.model_mat)
        #             component.set_uniform("camera_pos", *camera.transform.position)
        #             # mesh_renderer.set_uniform("time", currentTime)
        #             # mesh_renderer.set_uniform("light pos", light_pos)

        #             # apart from setting the mvp
        #             # we need to send light data
        #             if len(self.light_sources) > 0:
        #                 # when passing uniforms, we need to treat the data as simple as possible
        #                 # i.e, rather than a pyrr.vector or python array, expand them
        #                 # to a comma separated invidual floats
        #                 component.set_uniform("light_pos", *self.light_sources[0].position)
        #                 component.set_uniform("light_color", *self.light_sources[0].color)

        #             # if the material uses textures,
        #             # we need to make sure they are bound at the right texture units.
        #             # the material knows already which texture unit to use (that was set
        #             # initially using the uniform). but we need to ensure the right texture
        #             # is there.
        #             # self.texture1.bind()
        #             # self.texture2.bind(1)
        #             # therefore, material needs to know the textures is going to use

        #             # mesh renderer is calling gl.DrawArrays!
        #             # we need to make it call the material instead
        #             # and the material then call the mesh.draw
        #             component.render()

    def draw_overlay(self, camera):
        """" this method will draw things that need to be on top of everything like gizmos """
        if self.selected is not None:
            self.gizmo.draw(self.selected.transform, camera)

        for game_camera in self.cameras:
            self.camera_gizmo.draw(game_camera.transform, camera)

    def draw_gui(self):
        # behaviour i want.
        # scene tree
        # double click in game object will open its inspector (which can be closed)
        # single click will just make it 'selected'
        """ this will draw the scene hierarchy as a scrollable list """
        # let's make this its "own" window (like in unity is a dockable panel)
        imgui.begin("Scene Hierarchy")
        # for the list i can try to use:
        # - imgui.collapsing_header(text, visible_header, tree_flags) -> expanded, visible_header
        # for game_obj in self.game_objects:
        #     # we should display the expandable option only of the gameObject has children
        #     expanded_visible = imgui.collapsing_header(game_obj.name, None)
        #     if imgui.is_item_active():
        #         imgui.text("{} active".format(game_obj.name))
        #     if imgui.is_item_clicked():
        #         imgui.text("{} clicked".format(game_obj.name))
        #     if imgui.is_item_focused():
        #         imgui.text("{} focused".format(game_obj.name))
        #     if imgui.is_item_hovered():
        #         imgui.text("{} hovered".format(game_obj.name))

        # display list states
        # for idx, game_obj in enumerate(self.game_objects):
        interaction_values = []

        # - imgui.list_box_header/footer with imgui.selectable
        # the returned tuple has to be interpreted as:
        # opened (or clicked) if the item was click during this frame
        # selected if the current internal state of this item is selected
        imgui.listbox_header("hierarchy tree")
        for idx, game_obj in enumerate(self.game_objects):
            # opened, selected = imgui.selectable(game_obj.name, True if self.selected == game_obj else False)
            clicked, selected = imgui.selectable(
                    "> {}".format(game_obj.name),
                    True if self.selected == game_obj else False,
                    imgui.SELECTABLE_ALLOW_DOUBLE_CLICK)

            if selected:
                self.selected = game_obj
            if clicked:
                self.expanded[idx] = not self.expanded[idx]

            # detect double click in selectable
            open_inspector = imgui.is_item_hovered() and imgui.is_mouse_double_clicked()
            if open_inspector:
                self.guis[self.selected.id].opened = True

            interaction = {
                "clicked" : clicked,
                "selected" : selected,
            }
            interaction_values.append(interaction)

            # is_mouse_double_clicked is a global event (not linked to any widget)
            # double_click = imgui.is_mouse_double_clicked()
            # if (double_click):
            #     imgui.text("double click")

            # if (self.expanded[idx]):
            #     imgui.text("{} expanded".format(game_obj.name))

        imgui.listbox_footer()

        for interaction_val in interaction_values:
            imgui.text("clicked={} selected={}".format(interaction_val["clicked"], interaction_val["selected"]))

        imgui.end()

        # we need to display maybe multiple inspectors and not only the one that are active
        for game_object_id, gui in self.guis.items():
            if gui.opened:
                gui.draw_gui()
        # there are two windows to render, the hierarchy and the inspector
        # of the currrent selected object
        # if self.selected is not None and self.guis[self.selected.id].opened:
        #     self.guis[self.selected.id].draw_gui()
        #     # self.selected.draw_gui()
        #     print("gui expanded {}; gui opened {}".format(self.guis[self.selected.id].expanded, self.guis[self.selected.id].opened))
