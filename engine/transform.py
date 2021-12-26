import pyrr
import math
import numpy as np
import sys, traceback

class Transform:

    # clients don't set matrices
    # they only set values such as position, orientation and scales
    # whenever those values are set, we dirty the matrices.
    # the renderers read those matrices and if the values are dirtied,
    # they are recalculated
    def __init__(self, game_object = None, pos = None, euler_angles = None, scale = None):
        # following unity's design
        # a tranform can not exists without a gameObject
        self.game_object = game_object

        # internal local data
        # we don't want users to set values directly so we make them private.
        # public method, apart of updating local values will also dirty some flags
        self._local_position = pos if pos is not None else pyrr.Vector3([0, 0, 0])
        # if we are not going to keep track of euler angles, maybe we should not store them
        # self._local_euler_angles = euler_angles if euler_angles is not None else pyrr.Vector3([0, 0, 0])
        # identity quaternion = (1,0,0,0)
        # note that that is the resulting quaternion after applying cos/sin etc.
        # to get it, we multiply the rotations obtained from 0 degrees along x direction; 0 along y and 0 along z
        self._local_rotation = Transform.quaternion_from_euler(euler_angles)  if euler_angles is not None else [1, 0, 0, 0]
        self._local_scale = scale if scale is not None else pyrr.Vector3([1, 1, 1])

        # internal matrices for individual affine transformations
        # these are LOCAL matrices.
        # there should not be any reason that someone want's to get them individually.
        # these are kept here so we can reconstruct the correct local model and view matrix every time.
        # most clients of the class will work only with final model and view matrices (which involve processing all the tree structure)
        # if we use dirty flags, it's because we are caching the representation (the matrices in this case)
        # UPDATE: even though they are not needed from a user point,
        # we might want to access them to debug them in the inspector
        self._translation_dirty = True
        self._rotation_dirty = True
        self._scale_dirty = True

        # these are still internal
        # but they are actually read by clients of this class
        # we are going to disable them by now.
        # they are going to be use only when we cache final model and view matrices
        # let's do this later. it's taking to long.
        # we need to do it at some point though!!
        # self._model_dirty = True    # they get dirty when either local model matrix changed or when parent's model changed
        # self._view_dirty = True
        # local versions. do we actually need to local view??
        self._local_model_dirty = True
        self._local_view_dirty = True

        # directions
        # in unity they read/write but let's make them read-only for the moment.
        # or to be set all together with some sort of lookAt method or any method where the 3 axis are given simultaneously
        # they should be extracted from the rotation matrix.
        # once we get the rotation matrix based obtained from the local quaternion,
        # we should update this directions
        # since they might be dirty, we need to create a property for its getter
        # as everything else that can be dirtied
        # in our engine, we are going to use right hand rule.
        # positive x (right): thumb
        # positive y (up): index
        # positive z (forward): middle finger
        # should we mark them as dirty they dependent only on the model matrix?
        # let's work only with the model_dirty flag by now
        # self._right_dirty = True
        # self._up_dirty = True
        # self._forward_dirty = True
        # self.right = pyrr.Vector3([1, 0, 0])
        # self.up = pyrr.Vector3([0, 1, 0])
        # self.forward = pyrr.Vector3([0, 0, 1])

        # adding support to traverse the tree hierarchy:
        self.parent = None
        self.children = []

    # internal getters
    @property
    def position(self):
        # we need to think whether we are going to cache the global position
        # or if we are going to calculate it every time based "updated" values
        # for now, let's go for the second.
        # how expensive is to 'get' the parent model_mat? should we also cache it?
        model_matrix = self.parent.model_mat if self.parent is not None else pyrr.matrix44.create_identity()
        # it's more convenient to return a pyrr.Vector3 object so we can access x,y,z
        # the problem here is we are creating a new object every time we read this value
        # we should totally work in caching the result
        return pyrr.Vector3(pyrr.matrix44.apply_to_vector(model_matrix, self._local_position))

    # in which cases we would like to get the rotation (in quaternion) of a gameObject?
    # a) when we want to get poses and then interpolate between them
    # how do we get the final pose (global rotation)?
    # does it matter the local position and scale?
    # do parents' position and scale matters?
    # a) i don't think so. we should get only the final parent rotation and then multiply it by the local
    @property
    def rotation(self):
        # same as for position we will return local one for now
        # return self.local_rotation
        parent_rotation = self.parent.rotation if self.parent is not None else [1, 0, 0, 0] # identity quaternion
        return Transform.quaternion_multiply(parent_rotation, self._local_rotation)

    # when are we actually supposed to get final 'scale'??
    # unity doesn't return this value because it's not always right to reprenset final
    # scale with a vec3, but with a matrix
    # lossyScale tries to return a vec3 representing the final scale but it's not exactly the same
    # maybe we don't need to at all set/read a final scale and we can work well just with model matrices and local scales.
    # @property
    # def scale(self):
    #     # same as for position we will return local one for now
    #     return self.local_scale

    @property
    def local_position(self):
        return self._local_position

    @property
    def local_rotation(self):
        return self._local_rotation

    @property
    def local_scale(self):
        return self._local_scale

    # we need to add the property decorator once we manage to implement reading euler angles from quaternion
    @property
    # to convert from rotation matric to euler angles
    # http://eecs.qmul.ac.uk/~gslabaugh/publications/euler.pdf
    def local_euler_angles(self):
        if (self._rotation_dirty):
            self._update_rotation_matrix()
        # this is the M[1,3] of the mathematical matrix (1st row, 3 col)
        sin_beta = self._rotation_mat[2,0]
        sin_beta = max(min(sin_beta,1),-1)
        y_rot_rad = math.asin(sin_beta)
        y_rot = math.degrees(y_rot_rad)

        cos_beta = math.cos(y_rot_rad)

        # i need to change the order of rotations so it's z in the middle

        # if not math.isclose(cos_beta, 0):
        if not math.isclose(cos_beta, 0):
            # gamma (z rot) is related to the matrix as
            # M[1,2]/M[1,1] = -tan(gamma)
            z_rot_rad = -math.atan2(self._rotation_mat[1,0]/cos_beta, self._rotation_mat[0,0]/cos_beta)
            z_rot = math.degrees(z_rot_rad)

            # alpha (x rot) is related to the matrix as
            # M[2,3]/M[3,3] = -tan(alpha)
            x_rot_rad = -math.atan2(self._rotation_mat[2,1]/cos_beta, self._rotation_mat[2,2]/cos_beta)
            x_rot = math.degrees(x_rot_rad)
            self.last_euler_angle_z = z_rot
        else:
            # fix one of the angles to any value
            z_rot = self.last_euler_angle_z
            # x = atan(R21, R22) - z
            x_rot_rad = math.atan2(self._rotation_mat[0,1], self._rotation_mat[1,1]) - z_rot
            x_rot = math.degrees(x_rot_rad)
        # i just need to take into account the special case
        # when beta is 90 and cos(beta) is zero (which was simplified-divided
        # for the calculation of alpha and gamma)
        return pyrr.Vector3([x_rot, y_rot, z_rot])

    #     print("reading local euler angles. not implemented yet!")
    #     traceback.print_stack()
    #     exit()
    #     return

    # debuggin property getters for local matrices
    @property
    def translation_mat(self):
        # print("querying translation mat")
        # traceback.print_stack()
        # exit()
        if self._translation_dirty:
            self._update_translation_matrix()
        return self._translation_mat

    @property
    def rotation_mat(self):
        if (self._rotation_dirty):
            self._update_rotation_matrix()
        return self._rotation_mat


    # public api setters
    # for now global setters are acting like local
    @position.setter
    def position(self, value):
        # by setting position (as world space pos), we should
        # set local_position accordingly
        # for now, let's set local_position directly

        # what we actually need to do:
        # new_local_pos = parent_global_view_mat * target_ws_value
        # i.e the local position is based on how the parent transform
        # see the given world space position
        view_matrix = self.parent.view_mat if self.parent is not None else pyrr.matrix44.create_identity()
        # be careful. we need to make sure data is treated as pyrr.Vector3 and not just numpy ndarray
        local_pos = pyrr.Vector3(pyrr.matrix44.apply_to_vector(view_matrix, value))
        # should we try to cache this world space value in case is asked?
        # yes. we need somehow to return the local position when we are asked for it.
        # and we are not going to recalculate it every time.
        # should it have a dirty flag then?

        # we are going to use the property to dirty the values appropiately
        self.local_position = local_pos

    @local_position.setter
    def local_position(self, value):
        self._local_position = value
        self._translation_dirty = True
        self._local_model_dirty = True
        self._local_view_dirty = True

    # we were calling 'rotation' the euler angles
    # should we allow this setter?
    # yes, the 'inspector' can work based on these values
    @rotation.setter
    def rotation(self, value):
        # same as for position, we need to update local values
        # self.local_rotation(value)

        # this parent rotation is a quaternion
        parent_rotation = self.parent.rotation if self.parent is not None else [1, 0, 0, 0] # identity quaternion
        # we need to get the inverse rotation of the parent
        parent_rotation_inverse = [
            -parent_rotation[0],
            -parent_rotation[1],
            -parent_rotation[2],
            parent_rotation[3]
        ]
        local_rotation = Transform.quaternion_multiply(parent_rotation_inverse, value)
        # we are going to use the property to dirty the values appropiately
        self.local_rotation = local_rotation

    #

    @local_rotation.setter
    def local_rotation(self, value):
        self._local_rotation = value
        self._rotation_dirty = True
        self._local_model_dirty = True
        self._local_view_dirty = True

    # add back the property decorator once we manage to read euler from quaternion
    @local_euler_angles.setter
    def local_euler_angles(self, value):
        # print("trying to set euler angles to {}".format(value))
        self._local_rotation = Transform.quaternion_from_euler(value)
        self._rotation_dirty = True
        self._local_model_dirty = True
        self._local_view_dirty = True

    # local_euler_angles = property(None, local_euler_angles)

    # removed from now.
    # i don't think we are going to need trying to set a final scale
    # @scale.setter
    # def scale(self, value):
    #     # same as for position, we need to update local values
    #     self.local_scale(value)

    @local_scale.setter
    def local_scale(self, value):
        self._local_scale = value
        self._scale_dirty = True
        self._local_model_dirty = True
        self._local_view_dirty = True

    # public api (getters)
    # @property
    # def translation_mat(self):
    #     if (self._translation_dirty):
    #         self._set_translation_matrix()
    #     return self._translation_mat

    # @property
    # def rotation_mat(self):
    #     if (self._rotation_dirty):
    #         self._set_rotation_matrix()
    #     return self._rotation_mat

    # @property
    # def scale_mat(self):
    #     if (self._scale_dirty):
    #         self._set_scale_matrix()
    #     return self._scale_mat

    # public api getters
    @property
    # model matrix takes all hierarchy transformations into account.
    # model matrix = parent_model * local_model
    # how should we cache this matrix?
    # in order to cache it, we need to have a method to check if
    # parent's model matrix is up to date
    # plus a similar method to know if our local matrix is also up to date
    # to know if the parent model matrix is up to date, it's a recursive method
    # we are trying to cache the resulting model matrix to not do matrix multiplications
    # every time we 'get' this value.
    def model_mat(self):
        # if (self._model_dirty): # <- this means that whenever we change the local transform, we need to dirty our children's model matrices
        #     self._update_model_matrix()
        # return
        model_matrix = self.parent.model_mat if self.parent is not None else pyrr.matrix44.create_identity()
        # we use the property to access the local model matrix in case is dirty
        return pyrr.matrix44.multiply(self.local_model_mat, model_matrix)

    # this is the final view matrix
    # final view matrix = parent_view * local_view
    @property
    def view_mat(self):
        view_matrix = self.parent.view_mat if self.parent is not None else pyrr.matrix44.create_identity()
        # we use the property to access the local view matrix in case is dirty
        return pyrr.matrix44.multiply(self.local_view_mat, view_matrix)

    @property
    def local_model_mat(self):
        if (self._local_model_dirty):
            self._update_local_model_matrix()
        return self._local_model_mat

    @property
    def local_view_mat(self):
        if (self._local_view_dirty):
            self._update_local_view_matrix()
        return self._local_view_mat


    @property
    # world space of the right vector of this node
    # i should debug this directions by drawing a gizmo for each selected gameObject
    # direction vectors depends on the global model matrix
    def right(self):
        # if (self._right_dirty):
            # we should obtain the right vector from rotation matrix
            # we can do it a bit more directly checking directly if the rotation matrix is dirty.
            # actually no. the right vector is not just some vector in the local rotation matrix.
            # we also need to take into account the parent transforms
            # self._set_model_matrix()
        # right is the first col of the model matrix
        # and it's stored in numpy matrix as the first row (mat[0])
        # return self.model_mat[0,:3]
        # note. this was wrong. we were not even considering scale into account
        # now we do it taking the whole hierarchy into account and then normalize the vector
        # if (self._model_dirty):
        #     self._set_model_matrix()
        #     # we need to avoid doing this calculation every time
        #     # actually no. this calculation is only done when the model matrix is dirty
        #     # if we use the property to get the model matrix, we woulnd't need to check
        #     # here if the matrix is dirty.
        #     # but at the same time, we dont know if the matrix was dirty, we can
        #     # not tell if we need to recalculate the direction vector.
        #     # another apporach is to use the property getter for the model matrix
        #     # but having its own right_dirty flag
        #     # that means, whenever we set the model matrix, we need to set the direction
        #     # flag as dirty.
        #     # we might end up with a circular dependency if we follow that approach:
        #     # - direction is dirty,
        #     # we recalculate it by multiplying model * vector3.right
        #     # during that multiplication, we use the model matrix property getter
        #     # which if the matrix was dirty, will set the model matrix again,
        #     # marking as dirty the direction once again.
        #     # because of that, i think it's safer to not use the property for the matrix
        #     # and use it the internal
        #     self._right = pyrr.vector.normalize(
        #         pyrr.matrix44.apply_to_vector(self._model_mat, pyrr.Vector3([1, 0, 0]))
        #     )
        # return self._right
        # right up and forward are direction! they dont have to be translated nor scaled
        # but the final vector needs to be in world space
        np_vector = pyrr.matrix44.apply_to_vector(self.model_mat, pyrr.Vector4([1, 0, 0, 0]))
        # print("np_vector = {}".format(np_vector))
        result = pyrr.Vector3([np_vector[0], np_vector[1], np_vector[2]])
        # print("result = {}".format(result))
        # result = result.normalize()
        return pyrr.vector.normalize(result)

    @property
    def up(self):
        # if (self._model_dirty):
        #     self._set_model_matrix()
        #     self._up = pyrr.vector.normalize(
        #         pyrr.matrix44.apply_to_vector(self._model_mat, pyrr.Vector3([0, 1, 0]))
        #     )
        # # up is the second col of the model matrix
        # # and it's stored in numpy matrix as the second row (mat[1])
        # # return self.model_mat[1,:3]
        # return self._up
        np_vector = pyrr.matrix44.apply_to_vector(self.model_mat, pyrr.Vector4([0, 1, 0, 0]))
        result = pyrr.Vector3([np_vector[0], np_vector[1], np_vector[2]])
        return pyrr.vector.normalize(result)

    @property
    def forward(self):
        # if (self._model_dirty):
        #     self._set_model_matrix()
        #     self._forward = pyrr.vector.normalize(
        #         pyrr.matrix44.apply_to_vector(self._model_mat, pyrr.Vector3([0, 0, 1]))
        #     )
        # # up is the third col of the model matrix
        # # and it's stored in numpy matrix as the third row (mat[2])
        # # return self.model_mat[2,:3]
        # return self._forward
        np_vector = pyrr.matrix44.apply_to_vector(self.model_mat, pyrr.Vector4([0, 0, 1, 0]))
        result = pyrr.Vector3([np_vector[0], np_vector[1], np_vector[2]])
        return pyrr.vector.normalize(result)

    def rotate(self, euler_angles):
        """ rotate current transform by euler angles """
        rotation = Transform.quaternion_from_euler(euler_angles)
        # given rotation is applied on top of the current rotation
        self.local_rotation = Transform.quaternion_multiply(self._local_rotation, rotation)

    # utility to set the rotation matrix)
    def look_at(self, eye_pos, target, up):
        print("implement look at")
        traceback.print_stack()
        exit()
        # local positive z
        forward = (eye_pos - target)
        # forward = forward / np.sqrt(np.sum(forward**2))
        forward = pyrr.vector.normalize(forward)
        right = pyrr.vector3.cross(up, forward)
        up = pyrr.vector3.cross(forward, right)
        # this define us a rotation matrix
        # but we need to update the internal eurler angles
        # and then call _set_rotation_matrix
        # setting the rotation matrix is easy, but getting the
        # corresponding euler angles is not.

        # trying what was said in stackoverflow
        # the one citing wikipedia
        # https://stackoverflow.com/questions/11514063/extract-yaw-pitch-and-roll-from-a-rotationmatrix
        # roll : (rotation around z) phi
        # pitch : (look up and down) thetha
        # yaw: psi (rotation around up) (look left and right)

        # stackoverflow
        # phi (roll) = arctan2(A31, A32)
        # theta (pitch) = arccos(A33)
        # psi (yaw) = -arctan2(A13,A23)
        yaw = np.arcsin(self._rotation_mat[2][0])   # sin(b) = A13
        cos_beta = np.cos(yaw)
        pitch = np.arccos(self._rotation_mat[2][2]/cos_beta)
        roll = np.arccos(self._rotation_mat[0][0]/cos_beta)



    # private internal methods

    # these _set_<>_matrix methods needs to be called when the internal data has changed
    def _update_translation_matrix(self):
        self._translation_mat = pyrr.matrix44.create_from_translation(self._local_position)
        # print("translation matrix: {}".format(self._translation_mat))
        self._translation_dirty = False

    def _update_rotation_matrix(self):
        ############################################################################
        # OLD EULER CODE
        ############################################################################
        # print("implement _set_rotation_matrix")
        # traceback.print_stack()
        # exit()

        # # roll = math.radians(self._rotation.z)
        # # pitch = math.radians(self._rotation.x)
        # # yaw = math.radians(self._rotation.y)

        # # these have the right angle but are doing in the opposite direction
        # # and we want them to follow the right hand rule
        # # we need to invert them (transpose them)
        # individual_x = pyrr.matrix44.create_from_x_rotation(pitch)
        # individual_y = pyrr.matrix44.create_from_y_rotation(yaw)
        # individual_z = pyrr.matrix44.create_from_z_rotation(roll)

        # # transposing pyrr to be col-major using numpy .T
        # individual_x = individual_x.T
        # individual_y = individual_y.T
        # individual_z = individual_z.T

        # # btw. unity follow YXZ (following that order, it looks local)
        # # https://docs.unity3d.com/Packages/com.unity.mathematics@0.0/api/Unity.Mathematics.math.RotationOrder.html
        # # that means, regarding multiplication
        # # unity does:
        # # Ry * Rx * Rz * v
        # self._rotation_mat = pyrr.matrix44.multiply(
        #         pyrr.matrix44.multiply(individual_z, individual_y),
        #         individual_x)

        # # i should update the right, up and forward accordingly
        # # with pyrr: pyrr.matrix44.apply_to_vector(A, v)
        # self.right = pyrr.matrix44.apply_to_vector(self._rotation_mat, pyrr.Vector3([1, 0, 0]))
        # self.up = pyrr.matrix44.apply_to_vector(self._rotation_mat, pyrr.Vector3([0, 1, 0]))
        # self.forward = pyrr.matrix44.apply_to_vector(self._rotation_mat, pyrr.Vector3([0, 0, 1]))
        ############################################################################
        # END OLD EULER CODE
        ############################################################################
        self._rotation_mat = Transform.matrix_from_quaternion(self._local_rotation)
        self._rotation_dirty = False

    def _update_scale_matrix(self):
        self._scale_mat = pyrr.matrix44.create_from_scale(self._local_scale)
        self._scale_dirty = False

    # def _update_model_matrix(self):

    # def dirty_parent_model_matrix(self):
    #     self.


    # this is for the global model matrix
    # for now it's going to redirect to the local one
    # this needs to get called when reading a model matrix with a model_dirty flag set
    # def _set_model_matrix(self):
    #     pass

    # this is the 'local' model matrix
    # i think i'm mixing 'local' and global model matrices.
    # for instance, direction vectors property getters should check for the "global" model matrix.
    # when do we use a 'local' model matrix?
    # a) we use the local model matrix when chaining model matrices in a hierarchy
    def _update_local_model_matrix(self):
        if (self._translation_dirty):
            self._update_translation_matrix()
        if (self._rotation_dirty):
            self._update_rotation_matrix()
        if (self._scale_dirty):
            self._update_scale_matrix()
        self._local_model_mat = pyrr.matrix44.multiply(
                pyrr.matrix44.multiply(self._scale_mat, self._rotation_mat),
                self._translation_mat)
        self._local_model_dirty = False

    def _update_local_view_matrix(self):
        # do we need to check for the matrices dirty flag?
        # it doesn't seem we are using the matrices at all but the internal raw values
        # if (self._translation_dirty):
        #     self._update_translation_matrix()
        # if (self._rotation_dirty):
        #     self._update_rotation_matrix()
        # if (self._scale_dirty):
        #     self._update_scale_matrix()
        inverse_translation = pyrr.matrix44.create_from_translation(-self._local_position)
        inverse_quaternion = [
            -self._local_rotation[0],
            -self._local_rotation[1],
            -self._local_rotation[2],
            self._local_rotation[3]
        ]
        inverse_rotation = Transform.matrix_from_quaternion(inverse_quaternion)

        inverse_scale = pyrr.matrix44.create_from_scale(np.reciprocal(self._local_scale))
        # local view = inverse_scale * inverse_rotation * inverse_translation
        self._local_view_mat = pyrr.matrix44.multiply(
            pyrr.matrix44.multiply(inverse_translation, inverse_rotation),
            inverse_scale
        )
        self._local_view_mat_dirty = False

    # we might want a method to get the inverse but done
    # by knowing m = t * r * s

    ############################################################################
    # STATIC METHODS
    ############################################################################

    # static method don't take class type as first parameter
    # they don't modify the class at all compared to class methods
    # which have access to class data.
    @staticmethod
    def quaternion_from_euler(euler):
        # we need to create a rotation that is equivalent to rotate
        # RxRyRz with values specified by euler in degrees
        x_rad = math.radians(euler[0])
        y_rad = math.radians(euler[1])
        z_rad = math.radians(euler[2])

        # we can create 3 quaternions representing this individual rotations.
        # euler rotations are in world space so when constructing the quaternion,
        # we also need to create them using as axis a world space axis
        quaternion_x = Transform.versor_from_angle_axis(x_rad, [1, 0, 0])
        quaternion_y = Transform.versor_from_angle_axis(y_rad, [0, 1, 0])
        quaternion_z = Transform.versor_from_angle_axis(z_rad, [0, 0, 1])

        # in what order we multiply them now?
        # according to our book, to rotate by r first and them by q,
        # we should calculate t = q * r
        # i.e t = quaternion_multiply(q, r)
        # the following works! Rx*Ry*Rz
        rotation = Transform.quaternion_multiply(
            quaternion_x,
            Transform.quaternion_multiply(quaternion_y, quaternion_z)
        )

        # test:
        # let's see if we can get the right euler using wikipedia formula
        # if we use the specified order there: Ry*Rx*Rz (remember this is not pyrr!!)
        # it didn't work
        # rotation = Transform.quaternion_multiply(
        #     quaternion_y,
        #     Transform.quaternion_multiply(quaternion_x, quaternion_z)
        # )
        return rotation


    # implementing wikipedia's version
    # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Quaternion_to_Euler_angles_conversion
    # we are going to return them in degrees.
    # wikipedia formula was made for:
    # yaw (body-z) turning onto the runway
    # pitch (body-y) take off
    # rolls (body-x) in the air
    # but those seem to be local angles
    # if they are local angles, it's because they were done in that order
    # i.e product: Rv = Yaw * Pitch * Rolls * v
    # which for those refer to:
    # yaw -> Ry
    # pitch -> Rx
    # rolls -> Rz
    # let's see if we get the right conversation back if we generate the quaternion following: Ry*Rx*Rz * v
    # METHOD NOT COMPLETELY FNISHED AND NOT WORKING
    @staticmethod
    def euler_from_quaternion(quaternion):
        q0 = quaternion[0]
        q1 = quaternion[1]
        q2 = quaternion[2]
        q3 = quaternion[3]

        # maybe we are forgetting normalize the quaternion
        print("input quaternion: {}".format(quaternion))
        length = math.sqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3)
        q0 = q0 / length
        q1 = q1 / length
        q2 = q2 / length
        q3 = q3 / length
        print("normalized quaternion: {}, {}, {}, {}".format(q0, q1, q2, q3))

        a = np.arctan2(2 * (q0*q1 + q2*q3), 1 - 2 * (q1*q1 + q2*q2))
        b = np.arcsin(2 * (q0*q2 - q3*q1))
        c = np.arctan2(2 * (q0*q3 + q1*q2), 1 - 2 * (q2*q2 + q3*q3))

        # trying using the formulas from here
        # https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToEuler/
        a = np.arctan2(2 * (q0*q2 - q1*q3), 1 - 2 * (q2*q2 + q3*q3))
        b = np.arcsin(2 * (q1*q2 + q3*q0))
        c = np.arctan2(2 * (q0*q1 - q2*q3), 1 - 2 * (q1*q1 + q3*q3))

        a = math.degrees(a)
        b = math.degrees(b)
        c = math.degrees(c)

        return [a, b, c]



    # axis must be already normalized
    @staticmethod
    def versor_from_angle_axis(angle, axis):
        half_angle = angle/2.0
        sin_half_angle = np.sin(half_angle)
        q0 = np.cos(half_angle)
        q1 = sin_half_angle * axis[0]
        q2 = sin_half_angle * axis[1]
        q3 = sin_half_angle * axis[2]
        return (q0, q1, q2, q3)

    # quaterion multiplication
    @staticmethod
    def quaternion_multiply(q, r):
        t = [0, 0, 0, 0]
        t[0] = r[0] * q[0] - r[1] * q[1] - r[2] * q[2] - r[3] * q[3]
        t[1] = r[0] * q[1] + r[1] * q[0] - r[2] * q[3] + r[3] * q[2]
        t[2] = r[0] * q[2] + r[1] * q[3] + r[2] * q[0] - r[3] * q[1]
        t[3] = r[0] * q[3] - r[1] * q[2] + r[2] * q[1] + r[3] * q[0]
        return t

    @staticmethod
    def matrix_from_quaternion(q):
        # i need to fill up a numpy matrix.
        # we will make it so it's ready to be used as col major multiplication and storage
        w = q[0]
        x = q[1]
        y = q[2]
        z = q[3]
        m = np.identity(4)
        m[0] = [(1 - 2*y*y - 2*z*z), (2*x*y - 2*w*z), (2*x*z + 2*w*y), 0]
        m[1] = [(2*x*y + 2*w*z), (1 - 2*x*x - 2*z*z), (2*y*z - 2*w*x), 0]
        m[2] = [(2*x*z - 2*w*y), (2*y*z + 2*w*x), (1 - 2*x*x - 2*y*y), 0]
        m[3] = [0, 0, 0, 1]
        return m.T
