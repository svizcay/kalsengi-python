# given that we need a mesh and its VBO,EBO to configure a VAO
# and based on the mesh data we need to enable attributes in the shader program,
# we are going to create a MeshRenderer class that will work as the link between them.

import OpenGL.GL as gl
# from . import vertex_attrib_loc
from engine import vertex_attrib_loc
# from .gl_uniform import set_uniform, gl_uniform_type_to_f
from engine.gl_uniform import set_uniform, gl_uniform_type_to_f

from .component import Component

from engine.gui import MeshRendererGUI

import ctypes

class MeshRenderer(Component):
    # we could say this class is in charge of rendering a model using some material
    # but in reality, this class is more like the link between the mesh data
    # and the shader vertex attributes available.

    # the code for "rendering a model using a material" is done in the rendering loop
    # of a scene graph and usually is sorted per material

    def __init__(self, game_object, mesh, material):
        super().__init__(game_object)

        self.mesh = mesh

        # whenever we have a class that inherits from Component
        # and we DO have a valid component gui, then set it
        self.gui = MeshRendererGUI(self)
        self.name = "mesh renderer"

        self.vao = gl.glGenVertexArrays(1)

        # set up material-mesh link by calling the setter property
        self.material = material

    # material getter
    @property
    def material(self):
        return self._material

    # material setter
    @material.setter
    def material(self, value):
        self._material = value

        # we need to configure the vao
        # for that, we need to have the mesh data
        # and the current material/shader vertex attribs
        gl.glBindVertexArray(self.vao)

        # to configure the vao, we need the vbo and ebo bound
        # do we need to ensure we have the right vbo
        # this need to be done after biding the vao
        self.mesh.bind_buffers()

        # let's check how well matches the mesh data
        # with the material/shader that we are going to use
        # opengl offers two functions to inspect shaders' input:
        # - glGetProgramiv(program, GL_ACTIVE_ATTRIBUTES)
        #   that returns a list of attributes available and their type.
        #   actually, the previous function just return the NUMBER of ative attribs.
        #   the actual function to get the data attrib data is:
        # - glGetActiveAttrib(program, index, returned_data)
        # - glGetAttribLocation(program, attribName)
        #   that returns specifically the location parameter of the attribute.
        # NONE of this need the program to be bound (in use). That's why we need to specify the program

        # let's check what's available in the shader
        # do we need the glUseProgram() when calling glGetAttribLocation?

        # we are not just 'checking' how well they match
        # but we are also connecting mesh data to vertex attributes in vertex shader.
        # we actually need to perform this every time we replace the material
        # i think this part of the code should be using some interace provided by the material
        for attrib in vertex_attrib_loc:
            loc = gl.glGetAttribLocation(self._material.shader.program, attrib)
            if (loc >= 0):
                # things to test:
                # - do not enable the attrib at all if vertex doesn't have data
                # - enable attrib but don't specify any layout (attribPointer)
                print("{} attrib available in shader {}".format(attrib, self._material.shader.program))
                if self.mesh.attribs[attrib] is not None:
                    print("{} attrib available in mesh data".format(attrib))
                    gl.glEnableVertexAttribArray(loc)
                    gl.glVertexAttribPointer(
                        loc,            # index of the generic vertex attribute
                        self.mesh.attribs_size[attrib],  # size: nr of components in the vertex attribute
                        gl.GL_FLOAT,    # data type of each element
                        gl.GL_FALSE,    # should data go through normalization?
                        0,              # stride
                        ctypes.c_void_p(self.mesh.attribs_offset[attrib]) # offset but in pointer format (it's supposed to be an adddres)
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
                print("{} attrib not available in shader {}".format(attrib, self._material.shader.program))

        gl.glBindVertexArray(0)

    def render(self):
        # there is some sort of double 'dependency' here.
        # we are supposed to render ALL game objects that share the same material
        # and this MeshRenderer.render should only activate the VAO
        # and ask the model to call gl.DrawElements
        # but we need also to make sure the shader program is enabled
        gl.glBindVertexArray(self.vao)
        self.mesh.draw()
        gl.glBindVertexArray(0)

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


