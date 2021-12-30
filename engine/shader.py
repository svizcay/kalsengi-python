import OpenGL.GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader

# for paths (python 3.5)
from pathlib import PurePath

class Shader:

    # we want vertex and fragment shader to be mandatory
    # and they can be provided using positional arguments.
    # but those shader can be supplied either by src or by path to file.
    # let's make by default the path to srcs because it's most commonly used.
    # but if they decided to be passed explicitly using keywords, it's also fine
    # how can we have an overloaded method that takes a path rather than the context of the text file?

    # update:
    # rather than accepting many different parameters all default to None in __init__
    # we are going to use classmethod to create from_file or from_source_text
    # now the constructor is going to take the sources as mandatory and the files as optional
    def __init__(self, vertex_src, fragment_src, vertex_file = None, fragment_file = None, *additional_shaders):
        # we will save it for reloading
        self.vertex_file = vertex_file
        self.fragment_file = fragment_file

        self._compile(vertex_src, fragment_src, *additional_shaders)

    @classmethod
    # mandatory parameters: vertex and fragment shaders
    def from_file(cls, vertex_file, fragment_file, *additional_shaders):
        if (vertex_file is None or fragment_file is None):
            raise ArgumentError("Missing vertex or fragment source files")

        # we should check if file exist
        vertex_src = None
        fragment_src = None

        with open(vertex_file, 'r') as file:
            vertex_src = file.read()

        with open(fragment_file, 'r') as file:
            fragment_src = file.read()

        return cls(vertex_src, fragment_src, vertex_file, fragment_file, *additional_shaders)

    @classmethod
    # mandatory parameters: vertex and fragment shaders
    def from_string(cls, vertex_src, fragment_src, *additional_shaders):
        if (vertex_src is None or fragment_src is None):
            raise ArgumentError("Missing vertex or fragment source text")

        return cls(vertex_src, fragment_src, None, None, *additional_shaders)

    def use(self):
        gl.glUseProgram(self.program)

    def _compile(self, vertex_src, fragment_src, *additional_srcs):
        # if we dont succeed compiling the shader,
        # we should use an error shader
        # add try-catch!!
        # otherwise reloading shaders it's going to be useless
        vertex_shader = compileShader(vertex_src, gl.GL_VERTEX_SHADER)
        frag_shader = compileShader(fragment_src, gl.GL_FRAGMENT_SHADER)
        self.program = compileProgram(vertex_shader, frag_shader)
        self.dirty = False

    def reload(self):
        # if we have stored the file, read it again, and recreate the shader program
        if (self.vertex_file is not None and self.fragment_file is not None):
            with open(self.vertex_file, 'r') as file:
                vertex_src = file.read()

            with open(self.fragment_file, 'r') as file:
                fragment_src = file.read()

            self._compile(vertex_src, fragment_src)

    def depends_on_file(self, path):
        # if shader was loaded from string, then False
        # if shader was loaded from files, check files
        if (self.vertex_file is not None and self.fragment_file is not None):
            vertex = PurePath(self.vertex_file)
            fragment = PurePath(self.fragment_file)
            # print("checking for {} and {}".format(vertex.name, fragment.name))
            if (path.endswith(vertex.name) or path.endswith(fragment.name)):
                return True

        return False



