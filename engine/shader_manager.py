# users should not instantiate shaders by their own
# bur rather select from a list of available shaders.
# we need to have a way to refer to shaders uniquely
# and this unique id needs to be convenient and easy remember.
# we can use internally a numeric id but we can also offer aliases

# what i want:
# - compile many combinations of shaders (no need to be fully exhaustive...just a way to do it once)
# - list what are the available shaders
# this is basically a 'shader database'
# whenever we create a new shader, we need to add it here

# to have some sort of singleton, we will use the 'module' pattern
from .shader import Shader


################################################################################
# public methods
################################################################################

# we don't need to call init anymore when using the material manager.
# the material manager is going to ask us to load individual shaders
def init():
    _load_shaders()

# internal attributes
_nr_shaders = 0
_id_to_name = {}
_name_to_id = {}
_shaders = {} # key is the numeric id

def get_from_name(name:str):
    global _name_to_id
    if name in _name_to_id:
        shader_id = _name_to_id[name]
        return _shaders[shader_id]
    else:
        raise ArgumentError("shader name {} not found".format(name))

def get_from_id(shader_id:int):
    global _shaders
    if shader_id in _shaders:
        return _shaders[shader_id]
    else:
        raise ArgumentError("shader id {} not found".format(shader_id))

# i should compile only shaders that are used.
# i need to check in advance what are the list of shaders that are used
def _load_shaders():
    # define here the combination of shaders you want to use

    # list of mvp shaders i have available:
    # - vertex just sending position (simple_mvp.glsl)
    # - vertex forwarding vertex color (simple_mvp_color.glsl)
    # - vertex forwarding vertex uv (simple_mpv_uv.glsl)
    # what happens if a vertex forwards some data but fragment doesn't take it in??
    # does the compilation fail?
    # - fragment flat color defined in the shader (flat_color.glsl)
    # - fragment flat color defined by uniform (flat_color_uniform.glsl)
    # - fragment fixed red channel chaning over time - time as uniform (flat_time_color.glsl)
    # - fragment that outputs vertex color (vertex_color.glsl)
    # - fragment that takes uv and mixes two textures (mix_textures.glsl)
    # - fragment that takes uv and output texture color (txture_color.glsl)
    # - fragment that takes uv and output texture color multiplied by uniform color (texture_uniform_colog.glsl)
    # - fragment that takes uv and output texture color multiplied by vertex color (texture_vertex_color.glsl)

    # shaders where vertex shader doesn't forward any vertex attrib
    # i.e they use simple_mvp vertex shader

    # can i reuse the vertex shader??

    _load_shader(
        "mvp_flat_color",
        "engine/shaders/vertex/simple_mvp.glsl",
        "engine/shaders/fragment/flat_color.glsl"
    )

    _load_shader(
        "mvp_flat_color_uniform",
        "engine/shaders/vertex/simple_mvp.glsl",
        "engine/shaders/fragment/flat_color_uniform.glsl"
    )

    _load_shader(
        "mvp_time_color",
        "engine/shaders/vertex/simple_mvp.glsl",
        "engine/shaders/fragment/flat_time_color.glsl"
    )

    _load_shader(
        "mvp_texture_uniform_color",
        "engine/shaders/vertex/simple_mvp.glsl",
        "engine/shaders/fragment/texture_uniform_color.glsl"
    )

    _load_shader(
        "mvp_texture_vertex_color",
        "engine/shaders/vertex/simple_mvp.glsl",
        "engine/shaders/fragment/texture_uniform_color.glsl"
    )

    _load_shader(
        "mvp_flat_color_uniform_far_clipped",
        "engine/shaders/vertex/simple_mvp.glsl",
        "engine/shaders/fragment/flat_color_uniform_far_clipped.glsl"
    )

    # shaders where vertex shader forward one vertex attrib
    # i.e they use simple_mvp_[attrib] vertex shader

    _load_shader(
        "mvp_texture_color",
        "engine/shaders/vertex/simple_mvp_uv.glsl",
        "engine/shaders/fragment/texture_color.glsl"
    )

    _load_shader(
        "mvp_mix_textures_color",
        "engine/shaders/vertex/simple_mvp_uv.glsl",
        "engine/shaders/fragment/mix_textures.glsl"
    )

    _load_shader(
        "mvp_uv_color",
        "engine/shaders/vertex/simple_mvp_uv.glsl",
        "engine/shaders/fragment/uv_color.glsl"
    )

    _load_shader(
        "mvp_normal_color",
        "engine/shaders/vertex/simple_mvp_normal.glsl",
        "engine/shaders/fragment/normal_color.glsl"
    )

    _load_shader(
        "mvp_vertex_color",
        "engine/shaders/vertex/simple_mvp_color.glsl",
        "engine/shaders/fragment/vertex_color.glsl"
    )

    # shaders where vertex shader forward two vertex attribs

    # simple_mvp_vertex_uv_color.glsl -> not implemented yet
    # _load_shader(
    #     "mvp_vertex_color",
    #     "engine/shaders/vertex/simple_mvp_vertex_uv_color.glsl",
    #     "engine/shaders/fragment/texture_vertex_color.glsl"
    # )

    # testing world space color
    _load_shader(
        "world_space_color",
        "engine/shaders/vertex/world_space_color.glsl",
        "engine/shaders/fragment/vertex_color.glsl"
    )

    # testing world space normal
    _load_shader(
        "world_space_normal",
        "engine/shaders/vertex/world_space_normal.glsl",
        "engine/shaders/fragment/vertex_color.glsl"
    )

    # testing light shader
    _load_shader(
        "mvp_light_direction_color",
        "engine/shaders/vertex/mvp_light.glsl",
        "engine/shaders/fragment/light_direction.glsl"
    )

def _load_shader(alias, *files):
    # check if alias is unique
    global _name_to_id
    global _id_to_name
    global _shaders
    global _nr_shaders

    if alias not in _name_to_id:
        shader = Shader.from_file(*files)
        shader_id = _nr_shaders
        _id_to_name[shader_id] = alias
        _name_to_id[alias] = shader_id
        _shaders[shader_id] = shader
        _nr_shaders = _nr_shaders + 1
    else:
        raise ArgumentError("shader alias {} already defined".format(alias))
