import OpenGL.GL as gl
from .gl_uniform import set_uniform, gl_uniform_type_to_f
from .gl_uniform import set_uniform2

from engine.gl_uniform import gl_uniform_type_to_function

# are we going to deal with VAOs at this level?
# i.e, are we going to set uniform values? -> uniform values have nothing to do with VAOs!
# if that's so, what's the difference with the mesh renderer?
# the mesh renderer should be the object that groups mesh and material together
# a material can not be used to draw a mesh (the actual call to glDraw)
# that's the job of the mesh renderer.

# materials should offer an API to update them
# and most likely, it's the mesh renderer in its 'update' method
# the one updating the material but we could also do it directly by
# grabbing the reference

# to set uniform values:
# - we need the loc -> do it only once at setup time (we DONT need to load the program for that).
# - we need to set the uniform -> we need the program to be bound
#   -> therefore, we want an interface that set a value and internally activates the shader
#   -> but we also want a faster version that sets a value (like some time or matrix)
#       without 'using' the program every time (done only once)
# - does opengl performs an expensive operation glUseProgram if the program id passed is the same?
# for now, let's use the rule that we 'use' the program for every uniform change
class Material:
    """
    this class exposes what is available in a shader.
    both, vertex attributes and uniforms.
    """

    def __init__(self, shader):
        self.shader = shader

        self.uniforms = {}
        self.discarded_uniforms = {}

        self.vertex_attribs = {}
        self.discarded_vertex_attribs = {}

        self.uuid = None

        self.gui = None

        # no need to bind program yet
        nr_uniforms = gl.glGetProgramiv(shader.program, gl.GL_ACTIVE_UNIFORMS)
        for i in range(nr_uniforms):
            name, size, type_ = gl.glGetActiveUniform(shader.program, i)
            # name comes in a bytestring -> needs ascii decoding
            name = name.decode("ascii")

            # no need to bind program for querying uniform locations
            loc = gl.glGetUniformLocation(shader.program, name);

            uniform = {}
            uniform["name"] = name
            uniform["loc"] = loc
            uniform["type"] = type_
            uniform["size"] = size
            uniform["dirty"] = True # it tells use whether we have actually call glUniform with the value while having the shader active
            # we need to give uniforms a default value
            # uniform["value"] = default_based_on_type

            if (not type_ in gl_uniform_type_to_function):
                print("type {} has not been added yet to gl_uniform_type_to_function".format(type_))

            uniform["fun"] = gl_uniform_type_to_function[type_]

            # based on type and 'name', we should provide a default value
            if type_ == gl.GL_FLOAT_VEC3:
                if "color" in name:
                    uniform["value"] = [1, 1, 1]

            if (loc < 0):
                self.discarded_uniforms[name] = uniform
            else:
                self.uniforms[name] = uniform

            # report the cases where we have an incomplete implementation
            # of the right function to use to load uniform values
            if (not type_ in gl_uniform_type_to_f):
                print("type {} has not been added yet to gl_uniform_type_to_f".format(type_))


        # the following code is supposed to return the active vertex attributes of the shader.
        # were these active by default or because it happened that we activate them before
        # when linking vertex data within a vao??
        nr_attribs = gl.glGetProgramiv(shader.program, gl.GL_ACTIVE_ATTRIBUTES)
        for i in range(nr_attribs):
            bufSize = gl.glGetProgramiv(shader.program, gl.GL_ACTIVE_ATTRIBUTE_MAX_LENGTH)
            length = gl.GLsizei()
            size = gl.GLint()
            type_ = gl.GLenum()
            name = (gl.GLchar * bufSize)()
            gl.glGetActiveAttrib(
                    shader.program,
                    i,
                    bufSize,    # size of the buffer to write the name
                    length,     # how many chars were written
                    size,       # size of the attrib
                    type_,      # type of the attrib
                    name        # name of the attrib
            )
            name = name.raw.decode("ascii").rstrip('\x00')
            size = size.value
            type_ = type_.value
            attrib = {}
            attrib["name"] = name
            attrib["type"] = type_
            attrib["size"] = size
            self.vertex_attribs[name] = attrib
            # print("attrib {} size={} type={}".format(name, size, type_))

    def use(self):
        self.shader.use()
        # apply uniform changes that were requested
        # while the material was not being used
        for uniform_name in self.uniforms:
            if self.uniforms[uniform_name]["dirty"] and "value" in self.uniforms[uniform_name]:
                self.set_uniform(uniform_name, self.uniforms[uniform_name]["value"])

    # we need a method for callbacks to use with gui widgets
    # that "set uniform values" but those are not apply (call to glUniform)
    # until the next time we use the material
    def set_value(self, uniform_name, list_of_values):
        if (uniform_name in self.uniforms):
            self.uniforms[uniform_name]["value"] = list_of_values
            self.uniforms[uniform_name]["dirty"] = True

    # general method for setting uniforms.
    # shader program needs to be bound.
    # for setting matrices, use set_matrix
    # we expect the values as a python list
    def set_uniform(self, uniform_name, list_of_values, verbose=False):
        if (uniform_name in self.uniforms):
            loc = self.uniforms[uniform_name]["loc"]
            # type is not needed anymore
            uniform_type = self.uniforms[uniform_name]["type"]
            self.uniforms[uniform_name]["value"] = list_of_values
            self.uniforms[uniform_name]["fun"](loc, *list_of_values)
            self.uniforms[uniform_name]["dirty"] = False
        else:
            if verbose:
                print("uniform {} not found in shader".format(uniform_name))

    def set_matrix(self, uniform_name, matrix, verbose=False):
        if (uniform_name in self.uniforms):
            loc = self.uniforms[uniform_name]["loc"]
            # NOTE: when passing matrix to glUniformMatrix4fv (vector form)
            # we don't need to unpack it
            self.uniforms[uniform_name]["fun"](loc, 1, gl.GL_FALSE, matrix)
            # gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, matrix)
        else:
            if verbose:
                print("uniform {} not found in shader".format(uniform_name))
