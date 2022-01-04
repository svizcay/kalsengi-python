# singleton for handling textures

# internal attributes
_nr_textures = 0
_id_to_name = {}
_name_to_id = {}
_textures = {} # key is the numeric id

from engine.texture import Texture

def init():
    _create_textures()

def get_from_name(name:str):
    global _name_to_id
    if name in _name_to_id:
        uuid = _name_to_id[name]
        return _textures[uuid]
    else:
        raise ArgumentError("texture name {} not found".format(name))

def get_from_id(uuid:int):
    global _textures
    if uuid in _textures:
        return _textures[uuid]
    else:
        raise ArgumentError("texture id {} not found".format(uuid))

# we need a method to list all available textures in a consistent order
# i.e, by calling it twice, the order is always the same.
# i'm not sure dictionaries in python preserve the order
def get_textures_ids():
    result = []
    global _id_to_name
    for uuid, name in _id_to_name.items():
        result.append((uuid, name))

    result.sort(key=lambda texture: texture[0])   # sort by uuid

    return result

# this method is most likely to get called when querying available textures
# we need ideally to return also the 'index' of the texture in the returned
# array which was sorted by uuid
def get_texture_id_by_ref(ref_texture):
    global _textures
    for uuid, texture in _textures.items():
        if texture == ref_texture:
            return uuid
    return None

def _create_textures():
    texture1 = Texture.from_image("img/ash_uvgrid01.jpg")
    texture2 = Texture.from_image("img/wall.jpg")
    texture3 = Texture.from_image("img/awesomeface.png")
    texture4 = Texture.from_image("img/ImphenziaPalette02-Albedo.png")

    _add_texture_to_database("uv_grid",         texture1)
    _add_texture_to_database("wall",            texture2)
    _add_texture_to_database("smile",           texture3)
    _add_texture_to_database("color_palette",   texture4)

def _add_texture_to_database(name, texture):
    global _name_to_id
    global _id_to_name
    global _textures
    global _nr_textures
    uuid = _get_uuid()
    _id_to_name[uuid] = name
    _name_to_id[name] = uuid
    # material = Material(shader_manager.get_from_name(shader_name))
    # material = Material(shader_manager.get_instance_from_name(shader_name))
    texture.uuid = uuid
    # material_gui = MaterialGUI(material)
    _textures[uuid] = texture
    _nr_textures = _nr_textures + 1
    return texture


# for now, returning just the id of texture instance
def _get_uuid():
    return _nr_textures
