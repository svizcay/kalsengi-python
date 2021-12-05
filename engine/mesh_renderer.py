# for creating VAO and querying shader
import OpenGL.GL as gl
from . import vertex_attrib_loc
from .gl_uniform import set_uniform, gl_uniform_type_to_f

import ctypes

class MeshRenderer:
    """ This class is in charge of rendering a model using some material."""

    def __init__(self, mesh, shader):

        self.mesh = mesh
        self.shader = shader

        self.uniforms = {}

        # we could check what are the available uniforms and attribs
        print("list of available uniforms in shader {}".format(shader.program))
        nr_uniforms = gl.glGetProgramiv(shader.program, gl.GL_ACTIVE_UNIFORMS)
        for i in range(nr_uniforms):
            # name comes in a bytestring -> needs ascii decoding
            name, size, type = gl.glGetActiveUniform(shader.program, i)
            name = name.decode("ascii")
            # don't we need to bind the program fist before
            # querying for locations?
            # a)no, we don't need the program to be bind.
            # that's why we pass the program to glGetUniformLocation.
            # for glUniform is different. They don't take the program as parameter
            # and the program needs to be bound
            loc = gl.glGetUniformLocation(shader.program, name);
            uniform = {}
            uniform["name"] = name
            uniform["loc"] = loc
            uniform["type"] = type
            uniform["size"] = size
            self.uniforms[name] = uniform
            if (loc < 0):
                print("uniform {} was optimized out".format(name))

            print("uniform {} size={} type={} loc={}".format(name, size, type, loc))

            if (not type in gl_uniform_type_to_f):
                print("type {} has not been added yet to gl_uniform_type_to_f".format(type))

            # print("type for sampler2D GL_SAMPLER_2D = {}".format(gl.GL_SAMPLER_2D))
            # print("type for vec3 GL_FLOAT_VEC3 = {}".format(gl.GL_FLOAT_VEC3))
            # print("type for mat4 GL_FLOAT_MAT4 = {}".format(gl.GL_FLOAT_MAT4))
            # print("type for float GL_FLOAT = {}".format(gl.GL_FLOAT))

        self.vao = gl.glGenVertexArrays(1)
        # print("binding vao")
        gl.glBindVertexArray(self.vao)

        # do we need to ensure we have the right vbo
        # bound to GL_ARRAY_BUFFER?
        # right now we have it bound just because we created the mesh recently
        # a) yes, we need a vbo bound to GL_ARRAY_BUFFER
        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, mesh.vbo)
        # for the GL_ELEMENT_BUFFER, we need to bind it once again
        # after binding the vao, otherwise the vao is not going to be aware
        # of it
        mesh.bind_buffers()

        # let's check what's available in the shader
        # do we need the glUseProgram() when calling glGetAttribLocation?
        for attrib in vertex_attrib_loc:
            loc = gl.glGetAttribLocation(shader.program, attrib)
            if (loc >= 0):
                # things to test:
                # - do not enable the attrib at all if vertex doesn't have data
                # - enable attrib but don't specify any layout (attribPointer)
                print("{} attrib available in shader {}".format(attrib, shader.program))
                if mesh.attribs[attrib] is not None:
                    print("{} attrib available in mesh data".format(attrib))
                    gl.glEnableVertexAttribArray(loc)
                    gl.glVertexAttribPointer(
                        loc,            # index of the generic vertex attribute
                        mesh.attribs_size[attrib],  # size: nr of components in the vertex attribute
                        gl.GL_FLOAT,    # data type of each element
                        gl.GL_FALSE,    # should data go through normalization?
                        0,              # stride
                        ctypes.c_void_p(mesh.attribs_offset[attrib]) # offset but in pointer format (it's supposed to be an adddres)
                    )
                else:
                    # enabling the attrib without specifying the data source
                    # with glVertexAttribPointer failed at rendering time
                    # gl.glEnableVertexAttribArray(loc)

                    # it seems that we need to use glDisableVertexAttribArray
                    # if we are not going to enable it
                    gl.glDisableVertexAttribArray(loc)
                    print("{} attrib not available in mesh data".format(attrib))
            else:
                print("{} attrib not available in shader {}".format(attrib, shader.program))

        gl.glBindVertexArray(0)

    def render(self):
        gl.glBindVertexArray(self.vao)
        self.mesh.draw()
        gl.glBindVertexArray(0)

    # def glUniform(uniform_type, loc, value):
    #     switcher =
    #     {
    #         gl.GL_SAMPLER : gl
    #     }

    # we need to support a variable number of "uniform_value".
    def set_uniform(self, uniform_name, *uniform_values):
        # common function for setting uniforms
        # sampler2D GL_SAMPLER_2D -> glUniform1i(loc, texture_unit)
        # mat4 GL_FLOAT_MAT4 -> glUniformMatrix4fv(loc, count=1, transpose=GL_FALSE, matrix)
        # glUniform1i(self.sampler0Loc, 0)
        # glUniformMatrix4fv(self.rotation_loc, 1, GL_FALSE, rotation)
        # pass

        if (uniform_name in self.uniforms):
            loc = self.uniforms[uniform_name]["loc"]
            uniform_type = self.uniforms[uniform_name]["type"]
            # gl_uniform(loc, *uniform_values)
            # this is the call to set_uniform in gl_uniform module
            # print("mesh_renderer: about to set uniform {}".format(uniform_name))
            set_uniform(uniform_type, loc, *uniform_values)
        else:
            print("uniform {} not found in shader".format(uniform_name))
        #     match uniform_type:
        #         case gl.GL_SAMPLER_2D:
        #             print("setting sampler2D uniform")
        #             gl.glUniform1i(loc, uniform_value)
        #         case gl.GL_FLOAT_MAT4:
        #             print("setting mat4 uniform")
        #             glUniformMatrix4fv(loc, 1, GL_FALSE, value)
        #     # switch(self.uniforms[uniform_name]["
        #     # pass


