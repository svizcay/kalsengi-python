# the purpose of these classes is to setup opengl buffers (VBO and VAO) automatically.
# the very basic data is the vertex position but we should also able to include
# any additional data such as faces, color and uvs

# the model class should not have anything to do with the rendering
# i.e setting any glEnable stuff
# nor should care about transform and camera position.

# opengl library doesn't work with python's arrays.
# using numpy instead
import numpy as np
import pyassimp as assimp
import pickle

# for paths (python 3.5)
from pathlib import PurePath

# for creating VBO and VAO
import OpenGL.GL as gl

# import ctypes

from . import vertex_attrib_loc
from . import VertexAttrib

class BaseMesh():

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
            colors = None,
            indices = None,
            drawing_mode = gl.GL_TRIANGLES,
            verbose = False):


        self.vertices = vertices
        self.uvs = uvs
        self.normals = normals
        self.colors = colors

        self.drawing_mode = drawing_mode

        # remember to use python's // integer division
        self._nr_vertices = len(vertices) // 3

        if (self._nr_vertices < 30 and verbose):
            print("BaseMesh constructor")
            print("********************")
            print("vertices: {}".format(vertices))
            print("uvs: {}".format(uvs))
            print("normals: {}".format(normals))
            print("colors: {}".format(colors))
            print("indices: {}".format(indices))
            print("nr vertices: {}".format(self._nr_vertices))

        # does this work when some of them are None?
        # a) it doesn't. We need to include it only if it's not None
        # this is python's array concatenation
        # vertex_data = vertices + colors + uvs + normals
        vertex_data = vertices.copy()
        if (uvs is not None):
            vertex_data += uvs if uvs is not None else []
        if (normals is not None):
            vertex_data += normals if normals is not None else []
        if (colors is not None):
            vertex_data += colors if colors is not None else []

        if verbose:
            print("whole data (before numpy cast): {}".format(vertex_data))
        # cast to numpy array
        # let's cast only the whole vertex_data buffer and not the individual attribs
        # self.vertex_data is the numpy version of the data ready to be
        # transfered to the GPU
        self.vertex_data = np.array(vertex_data, dtype=np.float32)
        if verbose:
            print("whole data (after numpy cast): {}".format(vertex_data))

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

        # for key in self.attribs_offset:
        #     print("{} offset = {}".format(key, self.attribs_offset[key]))

        self.indexed_drawing = False if indices is None else True
        self.nr_indices = 0 if indices is None else len(indices)
        # data ready to be transfer to GPU
        self.indices = None if indices is None else np.array(indices, dtype=np.uint32)

        self.configure_opengl_buffers()

    def configure_opengl_buffers(self):
        # this only ask the gpu for an id
        # it doesn't allocate any memory.
        # gpu doesn't know yet how much space is needed.
        self.vbo = gl.glGenBuffers(1)

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
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

        # for whole vertex data (using a single vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            self.vertex_data.nbytes, # size in bytes (using numpy data structure)
            self.vertex_data,        # pointer to the actual data
            gl.GL_STATIC_DRAW      # usage: it depends on the usage where the chunk of memory in gpu is going to be allocated
        )

        if self.indexed_drawing:
            self.ebo = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            gl.glBufferData(
                gl.GL_ELEMENT_ARRAY_BUFFER,
                self.indices.nbytes,
                self.indices,
                gl.GL_STATIC_DRAW
            )


    @property
    def nr_vertices(self):
        return self._nr_vertices

    def draw(self):
        if (self.indexed_drawing):
            # print("using indexed drawing nr indices = {}".format(self.nr_indices))
            gl.glDrawElements(
                # gl.GL_TRIANGLES,    # mode
                self.drawing_mode,    # mode
                self.nr_indices,    # nr of indices
                gl.GL_UNSIGNED_INT, # type
                None                # offset
                # 0
                # ctypes.c_void_p(0)  # offset but in pointer format (it's supposed to be an adddres)
            )
        else:
            gl.glDrawArrays(
                # gl.GL_TRIANGLES,   # mode
                self.drawing_mode,    # mode
                0,              # starting index
                self.nr_vertices # nr vertices or triangles? i think it's nr vertices
            )
    def bind_buffers(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        if self.indexed_drawing:
            # print("binding ebo")
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

    def save(self, filename):
        # use pickle to dump mesh data into a binary file we understand
        with open(filename, "wb") as output_file:
            pickle.dump(self, output_file, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def from_imported_file(cls, filename):
        with open(filename, "rb") as input_file:
            mesh_instance = pickle.load(input_file)
            mesh_instance.configure_opengl_buffers()
            # configure opengl vbos

            return mesh_instance

    @classmethod
    def from_file(cls, filename, verbose=False):
        asset = assimp.load(
            filename,
            processing=assimp.postprocess.aiProcessPreset_TargetRealtime_MaxQuality
            # processing=assimp.postprocess.aiProcess_Triangulate | assimp.postprocess.aiProcess_OptimizeMeshes
        )

        # in assimp data structure
        # a model is mode out of multiple meshes
        # for example, a simple obj model
        # can consist of an entire 'scene' (light, camera, multiple meshes)
        # and all of this be packed in a simple 'model'
        if verbose:
            print("model {}".format(filename))
            print("nr meshes: {}".format(len(asset.meshes)))
            print("nr materials: {}".format(len(asset.materials)))
            print("nr textures: {}".format(len(asset.textures)))
            print("hierarchy:")
            BaseMesh.traverse_hierarchy(asset.rootnode)

        vertices = None
        normals = None
        uvs = None
        colors = None
        indices = None

        for index, mesh in enumerate(asset.meshes):
            if verbose:
                print("mesh id={}".format(index))
                print("material id={}".format(mesh.materialindex))
                print("nr vertices={}".format(len(mesh.vertices)))
                print("vertices={}".format(mesh.vertices))
            vertices = mesh.vertices
            if mesh.normals.any():
                # print("    first 3 normals:\n" + str(mesh.normals[:3]))
                if verbose:
                    print("normals={}".format(mesh.normals))
                normals = mesh.normals
            else:
                if verbose:
                    print("no normal data")
            if verbose:
                print("colors={}".format(mesh.colors))
            if len(mesh.colors) > 0:
                colors = mesh.colors

            tcs = mesh.texturecoords
            if tcs.any():
                uvs = mesh.texturecoords[0]
                for tc_index, tc in enumerate(tcs):
                    if verbose:
                        print("texture-coords "+ str(tc_index) + ":" + str(len(tcs[tc_index])) + "first3:" + str(tcs[tc_index][:3]))
            else:
                if verbose:
                    print("no uv data")
                # print("    no texture coordinates")

            if verbose:
                print("uv-component-count:" + str(len(mesh.numuvcomponents)))
            for uvcomponent in mesh.numuvcomponents:
                if verbose:
                    print(uvcomponent)
            if verbose:
                print("faces:" + str(len(mesh.faces)) + " -> first:\n" + str(mesh.faces[:3]))
                print("bones:" + str(len(mesh.bones)) + " -> first:" + str([str(b) for b in mesh.bones[:3]]))
                print("***********************")
                print("")
            indices = mesh.faces

        # note: assimp returns mesh data as array of vertex data.
        # i.e to return the 3 vertices of a triangles,
        # rather than returning:
        # [x1, y1, z1, x2, y2, z2, x3, y3, z3]
        # it's going to return
        # [[x1, y1, z1], [x2, y2, z2], [x3, y3, z3]]
        vertices = [coord for vertex in vertices for coord in vertex]
        if uvs is not None:
            uvs = [coord for uv in uvs for coord in uv]
        if normals is not None:
            normals = [coord for normal in normals for coord in normal]
        if colors is not None:
            colors = [channel for color in colors for channel in color]
        indices = [index for triangle in indices for index in triangle]
        mesh_instance = cls(vertices, uvs=uvs ,normals=normals ,colors=colors, indices=indices, verbose=verbose)

        assimp.release(asset)

        # if we succesfully loaded the mesh with assimp, we should try
        # to save the imported asset as binary so we can re-use it later using pickle
        asset_file = PurePath(filename)
        # extract only the file name if dragon.fbx -> dragon
        # extract the parent directory
        parent_dir = asset_file.parent
        asset_name = asset_file.stem + ".pkl" # the name dragon.fbx with no extension
        pkl_file = parent_dir.joinpath(asset_name)
        # print("dir={}\t asset={}\t file={}".format(parent_dir, asset_name, pkl_file))
        mesh_instance.save(pkl_file)

        # return cls(parameters)
        return mesh_instance

    # assimp hierarchy
    @staticmethod
    def traverse_hierarchy(node,level = 0):
        print("  " + "\t" * level + "- " + str(node))
        for child in node.children:
            BaseMesh.traverse_hierarchy(child, level + 1)


class Triangle(BaseMesh):

    def __init__(self, attribs = VertexAttrib.ALL,*,
            vertices = None,
            uvs = None,
            normals = None,
            colors = None,
            ):
        """ we expect vertex data to come in the form of arrays """

        # vertex data for a triangle
        # we need to check if it's ccw or cw
        default_vertices = [
            -0.5, -0.5, 0,  # lower-left
            0.5, -0.5, 0,   # lower-right
            0, 0.5, 0,      # top-center
        ]

        default_uvs = [
            0.0, 0.0,
            1.0, 0.0,
            0.5, 1.0,
        ]

        default_normals = [
            0, 0, 1,
            0, 0, 1,
            0, 0, 1,
        ]

        default_colors = [
            1, 0, 0,
            0, 1, 0,
            0, 0, 1,
        ]

        indices = [
            0,1,2
        ]

        # vertices can not be None. if they are not provided nor specified in the flag
        # we need to use the default
        vertices = default_vertices if (vertices is None) else vertices

        uvs = default_uvs if (uvs is None and attribs & VertexAttrib.UV) else uvs
        normals = default_normals if (normals is None and attribs & VertexAttrib.NORMAL) else normals
        colors = default_colors if (colors is None and attribs & VertexAttrib.COLOR) else colors

        # super().__init__() same as BaseModel.__init__()
        # when calling methods within the class, we don't need to pass self.
        super().__init__(vertices, uvs=uvs, normals=normals, colors=colors, indices=indices)

class GridMesh(BaseMesh):

    def __init__(self, size:int = 200):

        if size % 2 == 0:
            size = size + 1

        half_size = size // 2
        pos_z = -half_size
        pos_x = -half_size

        default_vertices = []

        # forward lines
        for i in range(size):
            # back vertex of forward line
            default_vertices.append(pos_x)
            default_vertices.append(0)
            default_vertices.append(-half_size)

            # front vertex of forward line
            default_vertices.append(pos_x)
            default_vertices.append(0)
            default_vertices.append(half_size)

            pos_x = pos_x + 1

        # horizontal lines
        for i in range(size):
            # left vertex of horizontal line
            default_vertices.append(-half_size)
            default_vertices.append(0)
            default_vertices.append(pos_z)

            # right vertex of horizontal line
            default_vertices.append(half_size)
            default_vertices.append(0)
            default_vertices.append(pos_z)

            pos_z = pos_z + 1

        super().__init__(default_vertices, drawing_mode=gl.GL_LINES)


class Line(BaseMesh):

    def __init__(self, attribs = VertexAttrib.ALL,*,
            vertices = None,
            uvs = None,
            normals = None,
            colors = None,
            ):
        """ we expect vertex data to come in the form of arrays """

        default_vertices = [
            -0.5, 0, 0,  # left
            0.5, 0, 0,   # right
        ]

        default_uvs = [
            0.0, 0.0,   # bottom left
            1.0, 0.0,   # bottom right
        ]

        default_normals = [
            0, 0, 1,
            0, 0, 1,
        ]

        default_colors = [
            1, 0, 0,
            0, 1, 0,
        ]

        # indices = [
        #     0,1,2,
        #     1,3,2,
        # ]

        # vertices can not be None. if they are not provided nor specified in the flag
        # we need to use the default
        vertices = default_vertices if (vertices is None) else vertices

        uvs = default_uvs if (uvs is None and attribs & VertexAttrib.UV) else uvs
        normals = default_normals if (normals is None and attribs & VertexAttrib.NORMAL) else normals
        colors = default_colors if (colors is None and attribs & VertexAttrib.COLOR) else colors

        # super().__init__() same as BaseModel.__init__()
        # when calling methods within the class, we don't need to pass self.
        super().__init__(vertices, uvs=uvs, normals=normals, colors=colors, drawing_mode=gl.GL_LINES)

class CameraGizmoMesh(BaseMesh):

    def __init__(self):
        # it's going to be a tetrahedron
        # the origin (tip of the tetrahedron) it's going to be at zero

        # 8 lines
        # O - LT
        # O - RT
        # O - LB
        # O - RB
        # LT - RT
        # RT - RB
        # RB - LB
        # LB - LT
        z = 0.5
        width = 0.25
        height = 0.25
        x = width / 2.0
        y = height / 2.0

        default_vertices = [

            # O - LT
            0, 0, 0,        # 0
            -x, y, -z,      # LT

            # O - RT
            0, 0, 0,        # 0
            x, y, -z,      # RT

            # O - LB
            0, 0, 0,        # 0
            -x, -y, -z,      # LB

            # O - RB
            0, 0, 0,        # 0
            x, -y, -z,      # RB

            # LT - RT
            -x, y, -z,      # LT
            x, y, -z,      # RT

            # RT - RB
            x, y, -z,      # RT
            x, -y, -z,      # RB

            # RB - LB
            x, -y, -z,      # RB
            -x, -y, -z,      # LB

            # LB - LT
            -x, -y, -z,      # LB
            -x, y, -z,      # LT
        ]

        super().__init__(default_vertices, drawing_mode=gl.GL_LINES)

class GizmoMesh(BaseMesh):

    def __init__(self):

        default_vertices = [
            0, 0, 0,    # x center
            1, 0, 0,    # x right
            0, 0, 0,    # y center
            0, 1, 0,    # y up
            0, 0, 0,    # z center
            0, 0, 1,    # z forward
        ]

        default_colors = [
            1, 0, 0,
            1, 0, 0,
            0, 1, 0,
            0, 1, 0,
            0, 0, 1,
            0, 0, 1,
        ]

        # super().__init__() same as BaseModel.__init__()
        # when calling methods within the class, we don't need to pass self.
        super().__init__(default_vertices, colors=default_colors, drawing_mode=gl.GL_LINES)

class Quad(BaseMesh):

    def __init__(self, attribs = VertexAttrib.ALL,*,
            vertices = None,
            uvs = None,
            normals = None,
            colors = None,
            ):
        """ we expect vertex data to come in the form of arrays """

        default_vertices = [
            -0.5, -0.5, 0,  # bottom left
            0.5, -0.5, 0,   # bottom right
            -0.5, 0.5, 0,   # top left
            0.5, 0.5, 0,    # top right
        ]

        default_uvs = [
            0.0, 0.0,   # bottom left
            1.0, 0.0,   # bottom right
            0.0, 1.0,   # top left
            1.0, 1.0,   # top right
        ]

        default_normals = [
            0, 0, 1,
            0, 0, 1,
            0, 0, 1,
            0, 0, 1,
        ]

        default_colors = [
            1, 0, 0,
            0, 1, 0,
            0, 0, 1,
            1, 1, 0,
        ]

        indices = [
            0,1,2,
            1,3,2,
        ]

        # vertices can not be None. if they are not provided nor specified in the flag
        # we need to use the default
        vertices = default_vertices if (vertices is None) else vertices

        uvs = default_uvs if (uvs is None and attribs & VertexAttrib.UV) else uvs
        normals = default_normals if (normals is None and attribs & VertexAttrib.NORMAL) else normals
        colors = default_colors if (colors is None and attribs & VertexAttrib.COLOR) else colors

        # super().__init__() same as BaseModel.__init__()
        # when calling methods within the class, we don't need to pass self.
        super().__init__(vertices, uvs=uvs, normals=normals, colors=colors, indices=indices)

class Cube(BaseMesh):

    def __init__(self, attribs = VertexAttrib.ALL,*,
            vertices = None,
            uvs = None,
            normals = None,
            colors = None,
            ):
        """ we expect vertex data to come in the form of arrays """

        default_vertices = [
            # front
            -0.5, -0.5, 0.5,  # bottom left
            0.5, -0.5, 0.5,   # bottom right
            -0.5, 0.5, 0.5,   # top left
            0.5, 0.5, 0.5,    # top right
            # back
            -0.5, -0.5, -0.5,  # bottom left
            0.5, -0.5, -0.5,   # bottom right
            -0.5, 0.5, -0.5,   # top left
            0.5, 0.5, -0.5,    # top right
        ]

        default_uvs = [
            # front
            0.0, 0.0,   # bottom left
            1.0, 0.0,   # bottom right
            0.0, 1.0,   # top left
            1.0, 1.0,   # top right
            # back
            0.0, 0.0,   # bottom left
            1.0, 0.0,   # bottom right
            0.0, 1.0,   # top left
            1.0, 1.0,   # top right
        ]

        default_normals = [
            # front
            0, 0, 1,
            0, 0, 1,
            0, 0, 1,
            0, 0, 1,
            # back
            0, 0, 1,
            0, 0, 1,
            0, 0, 1,
            0, 0, 1,
        ]

        default_colors = [
            # front
            1, 0, 0,
            0, 1, 0,
            0, 0, 1,
            1, 1, 0,
            # front
            1, 0, 0,
            0, 1, 0,
            0, 0, 1,
            1, 1, 0,
        ]

        indices = [
            # frontal face
            0,1,2,
            1,3,2,
            # right face
            1,5,3,
            5,7,3,
            # back face
            5,4,7,
            4,6,7,
            # left face
            4,0,6,
            0,2,6,
            # top face
            2,3,6,
            3,7,6,
            # bottom face
            0,4,1,
            1,4,5,
        ]

        # vertices can not be None. if they are not provided nor specified in the flag
        # we need to use the default
        vertices = default_vertices if (vertices is None) else vertices

        uvs = default_uvs if (uvs is None and attribs & VertexAttrib.UV) else uvs
        normals = default_normals if (normals is None and attribs & VertexAttrib.NORMAL) else normals
        colors = default_colors if (colors is None and attribs & VertexAttrib.COLOR) else colors

        # super().__init__() same as BaseModel.__init__()
        # when calling methods within the class, we don't need to pass self.
        super().__init__(vertices, uvs=uvs, normals=normals, colors=colors, indices=indices)
