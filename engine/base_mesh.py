# the purpose of these classes is to setup opengl buffers (VBO and VAO) automatically.
# the very basic data is the vertex position but we should also able to include
# any additional data such as faces, color and uvs

# the model class should not have anything to do with the rendering
# i.e setting any glEnable stuff
# nor should care about transform and camera position.

# opengl library doesn't work with python's arrays.
# using numpy instead
import numpy as np

# for creating VBO and VAO
import OpenGL.GL as gl

from . import vertex_attrib_loc
from . import VertexAttrib

class BaseMesh:

    # explanaition of:
    # - positional argument
    # - keyword argument
    # - optional argument (has some default value)
    # - required argument (has no default value)
    # and how to mix them
    # https://stackoverflow.com/questions/9450656/positional-argument-v-s-keyword-argument
    #
    # we are missing the additional texture coordinates and the tangent (vec4)
    def __init__(self, vertices,*,
            uvs = None,
            normals = None,
            colors = None):
        # print("vertices: {}".format(vertices))
        self.vertices = vertices
        self.uvs = uvs
        self.normals = normals
        self.colors = colors

        # remember to use python's // integer division
        self._nr_vertices = len(vertices) // 3
        # print("nr vertices: {}".format(self._nr_vertices))

        # does this work when some of them are None?
        # a) it doesn't. We need to include it only if it's not None
        # this is python's array concatenation
        # vertex_data = vertices + colors + uvs + normals
        vertex_data = vertices.copy()
        vertex_data += uvs if uvs is not None else []
        vertex_data += normals if normals is not None else []
        vertex_data += colors if colors is not None else []

        # print("whole data (before numpy): {}".format(vertex_data))
        # cast to numpy array
        # let's cast only the whole vertex_data buffer and not the individual attribs
        vertex_data = np.array(vertex_data, dtype=np.float32)

        self.attribs = {
            "pos" : vertices,
            "uv" : uvs,
            "normal" : normals,
            "color" : colors,
        }

        self.attribs_size = {
            "pos" : 3,
            "uv" : 2,
            "normal" : 3,
            "color" : 3,
        }

        vertices_size = 0 if vertices is None else len(vertices) * 4
        uvs_size = 0 if uvs is None else len(uvs) * 4
        normals_size = 0 if normals is None else len(normals) * 4
        colors_size = 0 if colors is None else len(colors) * 4

        self.attribs_offset = {
            "pos" : 0,
            "uv" : vertices_size,
            "normal" : (vertices_size + uvs_size),
            "color" : (vertices_size + uvs_size + normals_size),
        }

        # self.attribs_offset = {
        #     "pos" : 0,
        #     "uv" : vertices.nbytes,
        #     "normal" : (vertices.nbytes + uvs.nbytes),
        #     "color" : (vertices.nbytes + uvs.nbytes + normals.nbytes),
        # }

        # vertices_bytes =
        # vertices_bytes = vertices.nbytes if vertices is not None else 0
        # uvs_bytes = uvs.nbytes if uvs is not None else 0
        # normals_bytes = normals.nbytes if normals is not None else 0
        # colors_bytes = colors.nbytes if colors is not None else 0

        # vertices = np.array(vertices, dtype=np.float32)
        # uvs = np.array(uvs, dtype=np.float32)
        # normals = np.array(normals, dtype=np.float32)
        # colors = np.array(colors, dtype=np.float32)


        # print("vertices: {}".format(vertices))
        # print("uvs: {}".format(uvs))
        # print("normals: {}".format(normals))
        # print("colors: {}".format(colors))
        # print("whole data: {}".format(vertex_data))

        for key in self.attribs_offset:
            print("{} offset = {}".format(key, self.attribs_offset[key]))

        # this only ask the gpu for an id
        # it doesn't allocate any memory.
        # gpu doesn't know yet how much space is needed.
        vbo = gl.glGenBuffers(1)

        # to send data to some buffer
        # we need to bind it first
        # possible options for glBindBuffer:
        # GL_ARRAY_BUFFER
        # GL_COPY_READ_BUFFER
        # GL_COPY_WRITE_BUFFER
        # GL_ELEMENT_ARRAY_BUFFER
        # GL_PIXEL_PACK_BUFFER
        # GL_PIXEL_UNPACK_BUFFER
        # GL_TEXTURE_BUFFER
        # GL_TRANSFORM_FEEDBACK_BUFFER
        # GL_UNIFORM_BUFFER
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

        print("vertex data size in bytes = {}".format(vertex_data.nbytes))

        # for whole vertex data (using a single vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            vertex_data.nbytes, # size in bytes (using numpy data structure)
            vertex_data,        # pointer to the actual data
            gl.GL_STATIC_DRAW      # usage: it depends on the usage where the chunk of memory in gpu is going to be allocated
        )

    @property
    def nr_vertices(self):
        return self._nr_vertices

class Triangle(BaseMesh):

    def __init__(self, attribs = VertexAttrib.ALL,*,
            vertices = None,
            uvs = None,
            normals = None,
            colors = None,
            ):
        """ we expect vertex data to come in the form of arrays """

        # vertex data for a triangle
        default_vertices = [-0.5, -0.5, 0,  # lower-left
                    0.5, -0.5, 0,   # lower-right
                    0, 0.5, 0]      # top-center

        default_uvs = [
            0.0, 0.0,
            1.0, 0.0,
            0.5, 1.0,
        ]

        default_normals = [0, 0, 1, # lower-left
                0, 0, 1,    # lower-right
                0, 0, 1]    # top-center

        default_colors = [1, 0, 0,
                    0, 1, 0,
                    0, 0, 1]

        # vertices can not be None. if they are not provided nor specified in the flag
        # we need to use the default
        vertices = default_vertices if (vertices is None) else vertices

        uvs = default_uvs if (uvs is None and attribs & VertexAttrib.UV) else uvs
        normals = default_normals if (normals is None and attribs & VertexAttrib.NORMAL) else normals
        colors = default_colors if (colors is None and attribs & VertexAttrib.COLOR) else colors

        # super().__init__() same as BaseModel.__init__()
        # when calling methods within the class, we don't need to pass self.
        super().__init__(vertices, uvs=uvs, normals=normals, colors=colors)
