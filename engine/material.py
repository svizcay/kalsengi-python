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

    # general method for setting uniforms.
    # shader program needs to be bound.
    # for setting matrices, use set_matrix
    def set_uniform(self, uniform_name, *uniform_values):
        if (uniform_name in self.uniforms):
            loc = self.uniforms[uniform_name]["loc"]
            # type is not needed anymore
            uniform_type = self.uniforms[uniform_name]["type"]
            self.uniforms[uniform_name]["value"] = uniform_values
            # make sure program is in use before setting uniform value
            # self.shader.use()
            set_uniform(uniform_type, loc, *uniform_values)
            # self.uniforms[uniform_name]["fun"](loc, *uniform_values)
        else:
            print("uniform {} not found in shader".format(uniform_name))

    # no need to pack/unpack to call it
    # we should compare the speed with the previous way
    # to see if it's better to not pack/unpack multiple times
    # and also to see if we save some times
    # having the function pointer more directly
    # this didn't turned out to be so much faster but still a bit better.
    # actually it is considerable much faster.
    # the problem with the measurement was that i was creating an indentity matrix each time.
    # now the question is, how much faster would it be if i call the right glUniform function right away?
    def set_matrix(self, uniform_name, matrix):
        if (uniform_name in self.uniforms):
            loc = self.uniforms[uniform_name]["loc"]
            self.uniforms[uniform_name]["fun"](loc, 1, gl.GL_FALSE, *matrix)

    # performance is practically the same with set_matrix
    def set_matrix_direct(self, uniform_name, matrix):
        if (uniform_name in self.uniforms):
            loc = self.uniforms[uniform_name]["loc"]
            gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, *matrix)

    # right now set_uniform is grouping uniform values
    # into a single array (they get packed)
    # and therefore, to call this method, whenever we have a list of parameters,
    # we need to unpack them.
    # this is very inefficient
    # let's always receive an array and if the value is only one,
    # the caller should have to wrap it into an array
    def set_only_uniform(self, uniform_name, *uniform_values):
        if (uniform_name in self.uniforms):
            loc = self.uniforms[uniform_name]["loc"]
            uniform_type = self.uniforms[uniform_name]["type"]
            self.uniforms[uniform_name]["value"] = uniform_values
            # make sure program is in use before setting uniform value
            # self.shader.use()
            set_uniform(uniform_type, loc, *uniform_values)

    # we are going to use this method for the mvp matrices
    def set_only_uniform2(self, uniform_name, uniform_values):
        if (uniform_name in self.uniforms):
            loc = self.uniforms[uniform_name]["loc"]
            uniform_type = self.uniforms[uniform_name]["type"]
            self.uniforms[uniform_name]["value"] = uniform_values
            # make sure program is in use before setting uniform value
            # self.shader.use()
            # set_uniform2(uniform_type, loc, uniform_values)

            # this turned to be a faster method of
            # calling the apporpiate glUniform function
            # for setting matrices, we can not just expand the list of values
            # we also need to say if it's transpose and the nr of matrices
            self.uniforms[uniform_name]["fun"](loc, *uniform_values)



            # debugging, we are calling this just for the vec3
            # until here, we are okay
            # gl.glUniform3f(loc, *values)
            # calling a method is find...but calling a function
            # from gl_uniform module is very expensive somehow
            # self.test(loc, uniform_values)

    def test(self, loc, values):
        gl.glUniform3f(loc, *values)
