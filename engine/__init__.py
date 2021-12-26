# this __init__.py file is located in engine subfolder

# we will define multiple modules (python files) in this subfolder
# and many of them declare classes

# to make classes available outside this folder
# we need to import in the following way:
# from <folder> import ClassName
# example:
# from engine import Window
# this is going to be possible thanks to this __init__.py file
# which exports the available classes explicitly.

# this __init__.py file needs to export classes
# as follows:
# from .<file_name> import ClassName
# example:
# .window import Window

# global constants
from enum import Flag, auto

class VertexAttrib(Flag):
    NONE = 0
    POS = auto()
    UV = auto()
    NORMAL = auto()
    COLOR = auto()
    ALL = POS | UV | NORMAL | COLOR

vertex_attrib_loc = {
    "pos" : 0,
    "uv" : 1,
    "normal" : 2,
    "color" : 3,
}

from .window import Window
from .base_mesh import Triangle
from .scene import Scene


