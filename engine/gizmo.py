import pyrr
import OpenGL.GL as gl

from .components import MeshRenderer
from .base_mesh import GizmoMesh, CameraGizmoMesh
from . import shader_manager
from .material import Material
from .transform import Transform

from engine import material_manager

# refactor these gizmo classes

class Gizmo:

    def __init__(self):
        # instantiate a gizmo shader
        gizmo_mesh = GizmoMesh()

        # we don't create materials by ourself anymore
        # we should use the material manager
        # material = Material(shader_manager.get_from_name("mvp_vertex_color"))
        material = material_manager.get_from_name("transform_gizmo")
        self.renderer = MeshRenderer(
            None,
            gizmo_mesh,
            material
        )

    def draw(self, transform, camera):

        self.renderer.material.use()

        # gizmo should not be affected by object scaling.
        # to do so, we need to obtain the final position and pose of the object
        # and use that as model matrix
        position = transform.position
        rotation = transform.rotation
        translation_mat = pyrr.matrix44.create_from_translation(position)
        rotation_mat = Transform.matrix_from_quaternion(rotation)
        model_mat = pyrr.matrix44.multiply(rotation_mat, translation_mat)
        mvp = pyrr.matrix44.multiply(
            pyrr.matrix44.multiply(model_mat, camera.transform.view_mat),
            camera.projection)

        self.renderer.material.set_matrix("mvp", mvp)

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        # now we can ask the meshRenderer to draw the geometry
        self.renderer.render()

class CameraGizmo:

    def __init__(self):
        # instantiate a gizmo shader
        mesh = CameraGizmoMesh()
        # material = Material(shader_manager.get_from_name("mvp_flat_color_uniform"))
        material = material_manager.get_from_name("camera_gizmo")
        # print("camera gizmo material uuid={}".format(material.uuid))
        self.renderer = MeshRenderer(
            None,
            mesh,
            material
        )

    def draw(self, transform, camera):
        self.renderer.material.use()

        # gizmo should not be affected by object scaling.
        # to do so, we need to obtain the final position and pose of the object
        # and use that as model matrix
        position = transform.position
        rotation = transform.rotation
        translation_mat = pyrr.matrix44.create_from_translation(position)
        rotation_mat = Transform.matrix_from_quaternion(rotation)
        model_mat = pyrr.matrix44.multiply(rotation_mat, translation_mat)
        mvp = pyrr.matrix44.multiply(
            pyrr.matrix44.multiply(model_mat, camera.transform.view_mat),
            camera.projection)

        self.renderer.material.set_matrix("mvp", mvp)

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        self.renderer.render()
