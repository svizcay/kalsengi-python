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

from engine.texture import Texture

# for testing
from engine.gl_uniform import gl_uniform_type_to_f

# import timeit
from timeit import default_timer as timer


# order of events:
# update gets called before rendering

class Scene:

    def __init__(self):
        self.game_objects = []
        self.cameras = []
        self.light_sources = []
        self.selected = None
        self.expanded = []   # the list of flags saying whether the gameObject is expanded in the hierarchy window
        self.guis = {}
        self.gizmo = Gizmo()
        self.camera_gizmo = CameraGizmo()

        # testing grid
        grid_mesh = GridMesh()
        grid_material = material_manager.get_from_name("flat_color_uniform_far_clipped")
        # using a grid with vertex color didn't work as expected
        # because we are moving the grid with the camera
        # grid_material = material_manager.get_from_name("vertex_color")
        self.grid_renderer = MeshRenderer(
            None,
            grid_mesh,
            grid_material
        )
        self.grid_clip_distance = 75.0

        # testing textures
        # self.texture1 = Texture.from_image("img/ash_uvgrid01.jpg")
        # self.texture2 = Texture.from_image("img/wall.jpg")
        # self.texture3 = Texture.from_image("img/awesomeface.png")
        # self.textured_material = material_manager.get_from_name("mix_textures_color")
        # self.textured_material.use()
        # self.texture1.bind(0)
        # self.texture2.bind(1)
        # # even if we are not drawing anything with textures
        # # we can not tell about other libraries like imgui
        # # so it's not just a matter of telling the shader program what texture unit to use with glUnifor
        # # but also about saying what's the texture id in that texture slot (bind texture)
        # # but maybe what we can "skip" is saying over and over again what's the texture unit to use in the shader program
        # # that data is per glProgram and we should be able to set it just one
        # self.textured_material.set_uniform("texture0", [0])
        # self.textured_material.set_uniform("texture1", [1])

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
            imgui.end()

            # how am i supposed to execute some
            # opengl code (setting the state machine)
            # before rendering?
            # is the renderer in charge of that?
            # or is it the material?
            # how should i render multiple passes?
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
            self.grid_renderer.material.set_matrix("mvp", mvp)
            self.grid_renderer.material.set_uniform("clip_distance", [self.grid_clip_distance])
            self.grid_renderer.render()
            gl.glLineWidth(5)


        # rather than interating directly through the list of game objects,
        # we need to find what materials they are using and render them by grouping them
        # by materials
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

            # # testing textures
            # self.texture1.bind(0)
            # self.texture2.bind(1)
            # # material.set_uniform("texture0", [0])
            # # material.set_uniform("texture1", [1])
            # # end testing texture

            for game_obj in game_objects_per_material[material]:
                for component in game_obj.components:
                    if isinstance(component, MeshRenderer):

                        # mvp = pyrr.matrix44.multiply(
                        #     pyrr.matrix44.multiply(
                        #         game_obj.transform.model_mat,
                        #         camera.transform.view_mat),
                        #     camera.projection)

                        mvp = pyrr.matrix44.multiply(
                            game_obj.transform.model_mat,
                            camera.view_projection
                        )

                        material.set_matrix("mvp", mvp)
                        material.set_matrix("model", game_obj.transform.model_mat)
                        material.set_uniform("_camera_pos", camera.transform.position)

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
                            material.set_uniform("_light_pos", self.light_sources[0].position)
                            material.set_uniform("_light_color", self.light_sources[0].color)

                        # now we can ask the meshRenderer to draw the geometry
                        component.render()

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
