import OpenGL.GL as gl
from .gl_uniform import set_uniform, gl_uniform_type_to_f

# are we going to deal with VAOs at this level?
# i.e, are we going to set uniform values?
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

            # based on type and 'name', we should provide a default value
            if type_ == gl.GL_FLOAT_VEC3:
                if "color" in name:
                    uniform["value"] = [1, 1, 1]

            if (loc < 0):
                self.discarded_uniforms[name] = uniform
            else:
                self.uniforms[name] = uniform

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

    def set_uniform(self, uniform_name, *uniform_values):
        if (uniform_name in self.uniforms):
            loc = self.uniforms[uniform_name]["loc"]
            uniform_type = self.uniforms[uniform_name]["type"]
            self.uniforms[uniform_name]["value"] = uniform_values
            # make sure program is in use before setting uniform value
            self.shader.use()
            set_uniform(uniform_type, loc, *uniform_values)
        else:
            print("uniform {} not found in shader".format(uniform_name))
