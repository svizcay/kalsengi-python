# this __init__.py file is located in engine/components subfolder

# we will define multiple modules (python files) in this subfolder
# and many of them declare classes

# to make classes available outside this folder
# we need to import in the following way:
# from <this_folder> import ClassName
# example:
# from engine/components import Camera
# this is going to be possible thanks to this __init__.py file
# which exports the available classes explicitly.

# this __init__.py file needs to export classes
# as follows:
# from .<file_name> import ClassName
# example:
# .camera import Camera

from .component import Component
from .camera import Camera
from .mesh_renderer import MeshRenderer


