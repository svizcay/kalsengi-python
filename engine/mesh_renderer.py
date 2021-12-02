# for creating VAO and querying shader
import OpenGL.GL as gl
from . import vertex_attrib_loc

import ctypes

class MeshRenderer:
    """ This class is in charge of rendering a model using some material."""

    def __init__(self, mesh, shader):
        self.mesh = mesh
        self.shader = shader

        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        # do we need to ensure we have the right vbo
        # bound to GL_ARRAY_BUFFER?
        # right now we have it bound just because we created the mesh recently

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
        gl.glDrawArrays(
            gl.GL_TRIANGLES,   # mode
            0,              # starting index
            self.mesh.nr_vertices # nr vertices or triangles? i think it's nr vertices
        )
        gl.glBindVertexArray(0)
