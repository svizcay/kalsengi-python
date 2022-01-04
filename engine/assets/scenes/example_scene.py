import pyrr

from engine.scene import Scene
from engine.game_object import GameObject
from engine import material_manager
from engine.components import Camera, Light, LightType, MeshRenderer, Rotate
from engine.base_mesh import BaseMesh, Cube, Quad

class ExampleScene(Scene):

    # this is run once
    # here you are supposed to declare and configure the game objects
    def setup(self):
        print("runnning example scene setup")

        ########################################################################
        # CREATE GAME OBJECTS
        ########################################################################
        monkey_go = GameObject("red monkey")
        monkey_go2 = GameObject("green monkey")
        monkey_go3 = GameObject("textured monkey")
        # dragon_go = GameObject("dragon")
        # plane_go = GameObject("floor")
        # cube_go = GameObject("cube")
        dragon = GameObject("dragon")
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
        # monkey_mesh = BaseMesh.from_imported_file("models/suzanne/suzanne.pkl")
        # monkey_mesh = BaseMesh.from_file("models/suzanne/textured/suzanne_uv.obj", True)
        # monkey_mesh = BaseMesh.from_file("models/suzanne/textured/suzanne_uv.fbx", True)
        # monkey_mesh = BaseMesh.from_file("models/suzanne/textured/suzanne_uv_smooth.fbx", True)
        # monkey_mesh = BaseMesh.from_imported_file("models/suzanne/textured/suzanne_uv.pkl")
        monkey_mesh = BaseMesh.from_imported_file("models/suzanne/textured/suzanne_uv_smooth.pkl")
        dragon_mesh = BaseMesh.from_imported_file("models/xyzrgb_dragon/xyzrgb_dragon.pkl")

        # textured_material = material_manager.get_from_name("texture_uniform_color")
        low_poly_material = material_manager.get_from_name("low_poly")
        textured_material = material_manager.get_from_name("mix_textures_color")
        red_diffuse_material = material_manager.get_from_name("red_diffuse")
        green_diffuse_material = material_manager.get_from_name("green_diffuse")
        diffuse_material = material_manager.get_from_name("light_direction_color")
        default_material = material_manager.get_from_name("light_specular")
        phong_color_material = material_manager.get_from_name("phong_color")

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
        light.add_component(Light, LightType.DIRECTIONAL)
        monkey_go.add_component(MeshRenderer, monkey_mesh, red_diffuse_material)
        monkey_go2.add_component(MeshRenderer, monkey_mesh, green_diffuse_material)
        monkey_go3.add_component(MeshRenderer, monkey_mesh, low_poly_material)

        # i can not pass key parameters to game_object.add_component()
        # monkey_go.add_component(Rotate, axis=pyrr.Vector3([0, 0, 1]))
        monkey_go.add_component(Rotate, 90.0, pyrr.Vector3([0, 0, 1]))
        monkey_go2.add_component(Rotate, 90.0, pyrr.Vector3([0, 0, 1]))
        monkey_go3.add_component(Rotate, 90.0, pyrr.Vector3([0, 0, 1]))
        dragon.add_component(MeshRenderer, dragon_mesh, phong_color_material)

        ########################################################################
        # CONFIGURE COMPONENTS
        ########################################################################
        light.transform.local_position = pyrr.Vector3([0, 5, 5])
        light.transform.local_euler_angles = pyrr.Vector3([-60, 5, 0])
        game_camera.transform.local_position = pyrr.Vector3([0, 1, 2.5])
        game_camera.transform.local_euler_angles = pyrr.Vector3([-20, 0, 0])
        # set initial transforms
        monkey_go.transform.local_position = pyrr.Vector3([-2, 5, 0])
        monkey_go.transform.local_euler_angles = pyrr.Vector3([270, 0, 0])
        monkey_go2.transform.local_position = pyrr.Vector3([2, 5, 0])
        monkey_go2.transform.local_euler_angles = pyrr.Vector3([270, 0, 0])
        monkey_go3.transform.local_position = pyrr.Vector3([0, 3, 0])
        monkey_go3.transform.local_euler_angles = pyrr.Vector3([270, 0, 0])
        # plane_go.transform.local_euler_angles = pyrr.Vector3([270, 0, 0])
        # plane_go.transform.local_scale = pyrr.Vector3([10,10,10])
        # cube_go.transform.local_position = pyrr.Vector3([0, 0.5, 0])
        dragon.transform.local_scale = pyrr.Vector3([0.1, 0.1, 0.1])

        ########################################################################
        # ADD GAME OBJECTS TO THE SCENE
        ########################################################################
        # self.scene.add_game_object(dragon_go)
        self.add_game_object(monkey_go)
        self.add_game_object(monkey_go2)
        self.add_game_object(monkey_go3)
        # self.scene.add_game_object(plane_go)
        # self.scene.add_game_object(cube_go)
        self.add_game_object(dragon)
        self.add_game_object(game_camera)
        self.add_game_object(light)
