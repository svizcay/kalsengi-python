import pyrr

from engine.scene import Scene
from engine.game_object import GameObject
from engine import material_manager
from engine.components import Camera, Light, LightType, MeshRenderer
from engine.base_mesh import BaseMesh, Cube

class ExampleScene(Scene):

    # this is run once
    # here you are supposed to declare and configure the game objects
    def setup(self):
        print("runnning example scene setup")

        ########################################################################
        # CREATE GAME OBJECTS
        ########################################################################
        monkey_go = GameObject("monkey")
        # dragon_go = GameObject("dragon")
        # plane_go = GameObject("floor")
        # cube_go = GameObject("cube")
        blender_quad = GameObject("blender quad")
        game_camera = GameObject("game camera")
        light = GameObject("light")

        ########################################################################
        # LOAD ASSETS
        ########################################################################
        print("about to load something with assimp")
        # plane_mesh = Quad()
        # cube_mesh = Cube()
        # monkey_mesh = BaseMesh.from_file("models/suzanne/suzanne.fbx", True)
        # dragon_mesh = BaseMesh.from_file("models/xyzrgb_dragon/xyzrgb_dragon.obj", True)
        # blender_quad_mesh = BaseMesh.from_file("models/primitives/plane_vertices.obj", True)
        # blender_quad_mesh = BaseMesh.from_file("models/xyzrgb_dragon/xyzrgb_dragon.obj", False)
        # blender_quad_mesh = BaseMesh.from_file("models/primitives/plane_vertices.obj", False)
        # blender_quad_mesh = BaseMesh.from_file("models/suzanne/suzanne.fbx", False)
        # blender_quad_mesh = Cube()
        # blender_quad_mesh = BaseMesh.from_imported_file("test.pkl")
        # monkey_mesh = BaseMesh.from_file("models/suzanne/suzanne.fbx", True)
        monkey_mesh = BaseMesh.from_imported_file("models/suzanne/suzanne.pkl")
        blender_quad_mesh = BaseMesh.from_imported_file("models/xyzrgb_dragon/xyzrgb_dragon.pkl")

        diffuse_material = material_manager.get_from_name("light_direction_color")
        default_material = material_manager.get_from_name("light_specular")

        ########################################################################
        # ADD COMPONENTS
        ########################################################################
        # components such as cameras and lights need to be added BEFORE adding
        # the game objects into the scene
        # add components to game objects
        # # add renderers
        # redenderers now should not take shaders direclty BUT MATERIALS
        # plane_go.add_component(MeshRenderer, plane_mesh, flat_color_shader)
        # cube_go.add_component(MeshRenderer, cube_mesh, texture_shader)
        # # dragon_go.add_component(MeshRenderer, dragon_mesh, texture_shader)
        # self.gizmo_renderer = MeshRenderer(
        #     None,
        #     gizmo,
        #     gizmo_shader
        # )
        # NOTE: we need to know somehow what's going to be the size of the game view panel
        # game_camera.add_component(Camera, self.editor_scene_size[0]/self.editor_scene_size[1])
        game_camera.add_component(Camera, 16.0 / 9.0)
        # blender_quad.add_component(Rotate)
        light.add_component(Light, LightType.DIRECTIONAL)
        monkey_go.add_component(MeshRenderer, monkey_mesh, diffuse_material)
        blender_quad.add_component(MeshRenderer, blender_quad_mesh, default_material)

        ########################################################################
        # CONFIGURE COMPONENTS
        ########################################################################
        light.transform.local_position = pyrr.Vector3([0, 5, 5])
        light.transform.local_euler_angles = pyrr.Vector3([-60, 5, 0])
        game_camera.transform.local_position = pyrr.Vector3([0, 1, 2.5])
        game_camera.transform.local_euler_angles = pyrr.Vector3([-20, 0, 0])
        # set initial transforms
        monkey_go.transform.local_position = pyrr.Vector3([0, 5, 0])
        monkey_go.transform.local_euler_angles = pyrr.Vector3([270, 0, 0])
        # plane_go.transform.local_euler_angles = pyrr.Vector3([270, 0, 0])
        # plane_go.transform.local_scale = pyrr.Vector3([10,10,10])
        # cube_go.transform.local_position = pyrr.Vector3([0, 0.5, 0])
        blender_quad.transform.local_scale = pyrr.Vector3([0.1, 0.1, 0.1])

        ########################################################################
        # ADD GAME OBJECTS TO THE SCENE
        ########################################################################
        # self.scene.add_game_object(dragon_go)
        self.add_game_object(monkey_go)
        # self.scene.add_game_object(plane_go)
        # self.scene.add_game_object(cube_go)
        self.add_game_object(blender_quad)
        self.add_game_object(game_camera)
        self.add_game_object(light)
