import OpenGL.GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader

class Shader:

    # we want vertex and fragment shader to be mandatory
    # and they can be provided using positional arguments.
    # but those shader can be supplied either by src or by path to file.
    # let's make by default the path to srcs because it's most commonly used.
    # but if they decided to be passed explicitly using keywords, it's also fine
    # how can we have an overloaded method that takes a path rather than the context of the text file?
    def __init__(self,
            vertex_file = None, fragment_file = None, # they should be optional by also used as positional arguments
            *,
            vertex_src = None, fragment_src = None,
            geometry_src = None):

        if (vertex_file is None and vertex_src is None or fragment_file is None and fragment_src is None):
            raise ArgumentError("Missing vertex or fragment file or src")

        if (vertex_file is not None):
            with open(vertex_file, 'r') as file:
                vertex_src = file.read()

        if (fragment_file is not None):
            with open(fragment_file, 'r') as file:
                fragment_src = file.read()

        vertex_shader = compileShader(vertex_src, gl.GL_VERTEX_SHADER)
        frag_shader = compileShader(fragment_src, gl.GL_FRAGMENT_SHADER)
        self.program = compileProgram(vertex_shader, frag_shader)

