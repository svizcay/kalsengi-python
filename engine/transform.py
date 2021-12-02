import pyrr

class Transform:

    def __init__(pos = None, rotation = None, scale = None):
        # 'raw' values which are expected to be set by clients
        # we are going to use properties so we can update the internal matrices accordingly
        # most pyrr functions work on pyrr.VectorX objects.
        # and pyrr.Vector3 is constructed from a python array.
        self._pos = pos if pos is not None else pyrr.Vector3([0, 0, 0])
        self._scale = scale if scale is not None else pyrr.Vector3([1, 1, 1])

        # internal matrices which are only read for rendering
        # we need:
        # - individual translation, rotation and scale matrices
        # - model matrix = translation * rotation * scale
        # - 'view' matrix which is the inverse of the model
        # we could also have utilities to set them as lookat
        # maybe we might not want to calculate inverse matrices all the time
        # and we should do it only when they are requested and they are dirty
        self._t = pyrr.matrix44.create_from_translation(self._pos)

        # to multiply transformations we can use the regular '*' but that doesn't work in pygmae.
        # for pygame, use '@' as operator for matrix multiplication.
        # another alternative is to use pyrr multiplecation method that takes two matrices: pyrr.matrix44.multiply(a,b)
        rotation = pyrr.Matrix44.from_y_rotation(currentTime)
        # glUniformMatrix4fv(self.rotation_loc, 1, GL_FALSE, rotation)

        # projection matrix
        # parameters (fov_deg, aspect_ratio, near, far)
        # projection = pyrr.matrix44.create_perspective_projection_matrix()

        # view matrix
        # takes 3 pyrr.Vector3 (which were constructed from python arrays):
        # camera position, target, up
        #view = pyrr.matrix44.create_look_at()

    def T(self):
        return pyrr.matrix44.create_from_translation(self.pos)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._t = pyrr.matrix44.create_from_translation(self._pos)

