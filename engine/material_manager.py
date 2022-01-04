# similar to shader manager, this is going to be a 'singleton'

# the idea is that we don't instatiate materials by ourselves anymore
# but we use the one available here
# a material just has a shader as dependency (input data)

# this mananger can also be used to tell the shader manager
# what shaders needs to be loaded
# so we avoid loading all shaders by default

# similarly to shader manager, we can refer to materials
# either by name or by id
# for now material name needs to be unique.
# later on we are going to use uuid for assets
# we can assume that uuid is going to be implemented
# but for now is just going to be the name string

# the engine needs to declare at the beginning what are
# the materials that are going to be used
# and based on that, this material manager is going to
# to ask the shader manager to load those shaders
from engine.material import Material
from engine import shader_manager
from engine.gui.material_gui import MaterialGUI
from engine.texture import Texture

# internal attributes
_nr_materials = 0
_id_to_name = {}
_name_to_id = {}
_materials = {} # key is the numeric id

################################################################################
# public methods
################################################################################

# the list of names correspond to the list of shader names.
# i don't want to keep calling 'shaders' by a long name.
# i want to use some simple name like 'red material', 'shinny material', etc
# and that internally we know what to shader name to use

# therefore, rather than 'asking' materials to be loaded
# we need to 'create' this materials and give them some aliases
# and specify what is the shader to use (without specifying the shader sources)
# but a reference to them (without having them loaded)

# we might even want to have two instances of materials
# referring to the same shader but controlling them apart
# like having to 'material properties' for the same shader

# materials name don't need to be unique.
# they need some internal unique identifier but the name
# should be something indicative just for the final user

# unity has a Shader.Find method that returns a shader
# and then that shader is pass to the material constructor

def init():
    _create_materials()

def get_from_name(name:str):
    global _name_to_id
    if name in _name_to_id:
        uuid = _name_to_id[name]
        return _materials[uuid]
    else:
        raise ArgumentError("material name {} not found".format(name))

def get_from_id(uuid:int):
    global _materials
    if uuid in _materials:
        return _materials[uuid]
    else:
        raise ArgumentError("material id {} not found".format(uuid))

# we need a method to list all available materials in a consistent order
# i.e, by calling it twice, the order is always the same.
# i'm not sure dictionaries in python preserve the order
def get_materials_ids():
    result = []
    global _id_to_name
    for uuid, name in _id_to_name.items():
        result.append((uuid, name))

    result.sort(key=lambda material: material[0])   # sort by uuid

    return result

# this method is most likely to get called when querying available materials
# we need ideally to return also the 'index' of the material in the returned
# array which was sorted by uuid
def get_material_id_by_ref(ref_material):
    global _materials
    for uuid, material in _materials.items():
        if material == ref_material:
            return uuid
    return None


################################################################################
# internal methods
################################################################################

def _create_materials():

    # internal materials
    _create_material("transform_gizmo", "mvp_vertex_color") # render using mvp matrix and vertex color
    _create_material("camera_gizmo", "mvp_flat_color_uniform") # render using mvp matrix and vertex color

    # list of materials I want to have availabe
    # - textured + tint color (uniform) + light diffuse
    # - full phong (ambient + diffuse + specular) * texture color
    # - pull phong with specularity comming from texture

    # other materials
    _create_material("flat_color", "mvp_flat_color")
    _create_material("flat_color_uniform", "mvp_flat_color_uniform")
    _create_material("time_color", "mvp_time_color")

    textured_material = _create_material("texture_uniform_color", "mvp_texture_uniform_color")
    unlit_low_poly_material = _create_material("unlit low_poly", "mvp_texture_uniform_color")
    low_poly_material = _create_material("low_poly", "texture_color_diffuse")

    phong_color_material = _create_material("phong_color", "phong_uniform_color")
    phong_texture_material = _create_material("phong_texture", "phong_texture_uniform_color")

    _create_material("texture_vertex_color", "mvp_texture_vertex_color")
    grid_material = _create_material("flat_color_uniform_far_clipped", "mvp_flat_color_uniform_far_clipped")
    _create_material("texture_color", "mvp_texture_color")
    mixed_textures_material = _create_material("mix_textures_color", "mvp_mix_textures_color")
    _create_material("uv_color", "mvp_uv_color")
    _create_material("normal_color", "mvp_normal_color")
    _create_material("vertex_color", "mvp_vertex_color")
    _create_material("world_space_color", "world_space_color")
    _create_material("world_space_normal", "world_space_normal")
    _create_material("light_direction_color", "mvp_light_direction_color")
    _create_material("light_specular", "mvp_light_specular")

    # we want to be able to have 'instances' of 'materials'
    # i.e to have specific uniforms for them

    # let's start having a diffuse red and a diffuse green
    # should they use intenally the same opengl program?
    # we need our shader manager to create different shader programs id using the same source
    red_diffuse_material = _create_material("red_diffuse", "flat_color_diffuse")
    green_diffuse_material = _create_material("green_diffuse", "flat_color_diffuse")
    # _create_material("red_diffuse", "flat_color_diffuse")

    # configure materials
    red_diffuse_material.use()
    red_diffuse_material.set_uniform("color", [1.0, 0, 0])

    green_diffuse_material.use()
    green_diffuse_material.set_uniform("color", [0.0, 1.0, 0])

    # i should have a texture manager
    texture1 = Texture.from_image("img/ash_uvgrid01.jpg")
    texture2 = Texture.from_image("img/wall.jpg")
    texture3 = Texture.from_image("img/awesomeface.png")

    low_poly_texture = Texture.from_image("img/ImphenziaPalette02-Albedo.png")

    textured_material.use()
    textured_material.set_texture("texture0", texture1, 0)

    mixed_textures_material.use()
    mixed_textures_material.set_texture("texture0", texture1, 0)
    mixed_textures_material.set_texture("texture1", texture2, 1)

    low_poly_material.use()
    low_poly_material.set_texture("texture0", low_poly_texture, 0)

    # ideally, we should grab these default values from the shader
    # source code
    phong_color_material.use()
    phong_color_material.set_uniform("slider_0_1_reflectivity", [1.0])
    phong_color_material.set_uniform("slider_1_32_shine_damper", [32.0])

    phong_texture_material.use()
    phong_texture_material.set_uniform("slider_0_1_reflectivity", [1.0])
    phong_texture_material.set_uniform("slider_1_32_shine_damper", [32.0])
    phong_texture_material.set_texture("texture0", low_poly_texture, 0)


    grid_material.use()
    grid_material.set_uniform("color", [0.678, 0.678, 0.678])


def _create_material(name, shader_name):
    global _name_to_id
    global _id_to_name
    global _materials
    global _nr_materials
    uuid = _get_uuid()
    _id_to_name[uuid] = name
    _name_to_id[name] = uuid
    # material = Material(shader_manager.get_from_name(shader_name))
    material = Material(shader_manager.get_instance_from_name(shader_name))
    material.uuid = uuid
    material_gui = MaterialGUI(material)
    _materials[uuid] = material
    _nr_materials = _nr_materials + 1
    return material

# for now, returning just the id of material instance
def _get_uuid():
    return _nr_materials
