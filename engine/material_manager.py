# similar to shader manager, this is going to be a 'singleton'

# the idea is that we don't instatiate materials by ourselves anymore
# but we use the one available here
# a material just has a shader as dependency (input data)

# this mananger can also be used to tell the shader manager
# what shaders needs to be loaded
# so we avoid loading all shaders by default

# similarly to shader manager, we can refer to materials
# either by name or by id

# the engine needs to declare at the beginning what are
# the materials that are going to be used
# and based on that, this material manager is going to
# to ask the shader manager to load those shaders
from .material import Material

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

def init(list_of_names):
    pass
    # _load_shaders()






################################################################################
# internal methods
################################################################################

