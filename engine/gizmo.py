import pyrr
import OpenGL.GL as gl

from .components import MeshRenderer
from .base_mesh import GizmoMesh, CameraGizmoMesh
from . import shader_manager
from .material import Material
from .transform import Transform

# refactor these gizmo classes

class Gizmo:

    def __init__(self):
        # instantiate a gizmo shader
        gizmo_mesh = GizmoMesh()
        material = Material(shader_manager.get_from_name("mvp_vertex_color"))
        self.gizmo_renderer = MeshRenderer(
            None,
            gizmo_mesh,
            material
        )

    def draw(self, transform, camera):
        self.gizmo_renderer.shader.use()
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
        self.gizmo_renderer.set_uniform("mvp", mvp)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        self.gizmo_renderer.render()

class CameraGizmo:

    def __init__(self):
        # instantiate a gizmo shader
        mesh = CameraGizmoMesh()
        material = Material(shader_manager.get_from_name("mvp_flat_color_uniform"))
        self.renderer = MeshRenderer(
            None,
            mesh,
            material
        )

    def draw(self, transform, camera):
        self.renderer.shader.use()
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
        self.renderer.set_uniform("mvp", mvp)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        self.renderer.render()
