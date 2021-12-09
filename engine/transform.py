import pyrr
import math
import numpy as np
import sys, traceback

# A*B
# to multiply matrices with pyrr, only use pyrr.matrix44.multiply(B, A)
# never use '*'.
# example:
# we want Projection * Model
# therefore we use pyrr.matrix44.multiply(Model, Projection)

################################
# # for more than 2 matrices:
#   t1 = pyrr.matrix44.create_from_translation(pyrr.Vector3([1, 1, 1]))
#   t2 = pyrr.matrix44.create_from_translation(pyrr.Vector3([10, 10, 10]))
#   s = pyrr.matrix44.create_from_scale(pyrr.Vector3([2, 2, 2]))
#
#   # I want (t2 * s * t1) * v
#   # i.e move the vector 1 at each direciton
#   # scale it by 2
#   # move it extra 10 units at each direction
#
#   print("t1 (move +1) = {}".format(t1))
#   print("s (scale x2) = {}".format(s))
#   print("t2 (move +10) = {}".format(t2))
#
#   print("t1 (move +1) = {}".format(t1))
#
#   st1 = pyrr.matrix44.multiply(t1, s)
#   t2st1 = pyrr.matrix44.multiply(st1, t2)
#   therefore:
#   t2st1 = multiply(multiply(t1,s),t2)
#   remember that mvp its actually p * v * m
#   in pyrr, to make that product
#   mvp = multiply(multiply(m, v), p)   # p * v * m
#
#   for affine transformations:
#   affine = T * R * S * v
#   the product in pyrr should be
#   affine = multiply(multiply(S,R), T)
#
#   print("st1 (move +1 then scale x2) = {}".format(st1))
#   print("t2st1 (move +1 then scale x2 then move +10) = {}".format(t2st1))
################################
# P * V * M * v


# A*v
# with pyrr: pyrr.matrix44.apply_to_vector(A, v)

class Transform:

    # clients don't set matrices
    # they only set values such as position, orientation and scales
    # whenever those values are set, we dirty the matrices.
    # the renderers read those matrices and if the values are dirtied,
    # they are recalculated
    def __init__(self, game_object = None, pos = None, euler_angles = None, scale = None):
        # a tranform can not exists without a gameObject
        print("creating transform for gameObject={}".format(game_object))
        self.game_object = game_object

        # internal data
        self._position = pos if pos is not None else pyrr.Vector3([0, 0, 0])

        self._euler_angles = euler_angles if euler_angles is not None else pyrr.Vector3([0, 0, 0])
        # for each euler angle:
        # if the euler angle is zero -> whatever is the direction we use, the quaternion is (1, 0, 0, 0)
        self.rotation = Transform.quaternion_from_euler(self._euler_angles) # identity quaternion
        self._scale = scale if scale is not None else pyrr.Vector3([1, 1, 1])

        # internal matrices
        self._translation_dirty = True
        self._rotation_dirty = True
        self._scale_dirty = True

        self._model_dirty = True
        self._view_dirty = True

        # directions (they should be extracted from the model matrix
        # self.right = pyrr.Vector3([1, 0, 0])
        # self.up = pyrr.Vector3([0, 1, 0])
        # self.forward = pyrr.Vector3([0, 0, 1])

        ### # test for generating matrices and quaternion form euler angles -> success
        print("**********************")
        print("testing rotation matrix from quaternion")
        ### # euler_rotation = [0, 90, 0] # 90 degrees yaw direction (lateral view)
        euler_rotation = [10, 20, 30] # 90 degrees yaw direction (lateral view)
        print("euler = {}".format(euler_rotation))
        quaternion = Transform.quaternion_from_euler(euler_rotation)
        rotation_matrix = Transform.matrix_from_quaternion(quaternion)
        resulting_euler = Transform.euler_from_quaternion(quaternion)
        print("euler back = {}".format(resulting_euler))
        exit()
        ### # testing values
        ### print("rotation matrix")
        print(rotation_matrix)
        ### print("rotating x")
        ### print(pyrr.matrix44.apply_to_vector(rotation_matrix, pyrr.Vector3([1, 0, 0])))
        ### print("rotating y")
        ### print(pyrr.matrix44.apply_to_vector(rotation_matrix, pyrr.Vector3([0, 1, 0])))
        ### print("rotating z")
        ### print(pyrr.matrix44.apply_to_vector(rotation_matrix, pyrr.Vector3([0, 0, 1])))
        exit()

        ### print("using only rotation matrices:")
        ### roll = math.radians(euler_rotation[2])
        ### pitch = math.radians(euler_rotation[0])
        ### yaw = math.radians(euler_rotation[1])
        ### individual_x = pyrr.matrix44.create_from_x_rotation(pitch)
        ### individual_y = pyrr.matrix44.create_from_y_rotation(yaw)
        ### individual_z = pyrr.matrix44.create_from_z_rotation(roll)
        ### # transpose pyrr rotation matrices
        ### individual_x = individual_x.T
        ### individual_y = individual_y.T
        ### individual_z = individual_z.T
        ### rotation_matrix_old = pyrr.matrix44.multiply(
        ###         pyrr.matrix44.multiply(individual_z, individual_y),
        ###         individual_x)
        ### print(rotation_matrix_old)
        ### print("rotating x")
        ### print(pyrr.matrix44.apply_to_vector(rotation_matrix_old, pyrr.Vector3([1, 0, 0])))
        ### print("rotating y")
        ### print(pyrr.matrix44.apply_to_vector(rotation_matrix_old, pyrr.Vector3([0, 1, 0])))
        ### print("rotating z")
        ### print(pyrr.matrix44.apply_to_vector(rotation_matrix_old, pyrr.Vector3([0, 0, 1])))
        ### exit()
        ### # end test -> sucess

        # print("testing translation matrix numpy order")
        # it seems numpy data is layered by rows
        # if matrix =   | a b c |
        #               | d e f |
        #               | f g h |
        # then, that would be created in numpy as:
        # mat = np.array( [a,b,c], [d,e,f], [g,h,i] )
        # and the linear iteration will also go for rows
        # for idx, x in np.ndenumerate(arr):
        # idx is a tuple where idx[0] is the row and idx[1] is the col (x is the actual value)
        # np_translation_matrix = pyrr.matrix44.create_from_translation(pyrr.Vector3([1, 2, 3]))
        # pyrr will put the translation in the last ROW of the numpy matrix
        # which can be interpreted as well as a matrix stored by cols, i.e
        # instead of considering the last element of the numpy matrix as a row,
        # we can consider it as a col.
        # the way pyrr does it is as follows:
        # - create an identity 4x4 matrix
        # - set mat[3, 0:3] = vec[:3]
        # which also works for row major multiplication when data is considered to be layout
        # by rows
        # print(np_translation_matrix)
        # for idx, x in np.ndenumerate(np_translation_matrix):
        #     print("T[{},{}]={}".format(idx[0], idx[1], x))
        # for i in range len(np_translation_matrix):
        #     for j in range len(np_translation_matrix[i]):
        #         print("T[{},{}]={}".format(i, j, np_translation_matrix[i, j]))
        #     print("")
        # print("")
        # exit()

        # 'raw' values which are expected to be set by clients
        # we are going to use properties so we can update the internal matrices accordingly
        # most pyrr functions work on pyrr.VectorX objects.
        # and pyrr.Vector3 is constructed from a python array.

        # self._rotation = rotation if rotation is not None else pyrr.Vector3([0, 0, 0])

        # let's also provide shortcuts for
        # right, up, forward.
        # should we allow setting them?
        # i dont think so, better to provide lookAt method that set thems all together

        # the quaternion is going to be the actual internal data and not the euler angles
        # we were calling until now 'rotation' to the vec3 representing the euler angles.
        # testing our own quaternion
        # angle (scalar), x,y,z (axis)
        # the actual versor is constructed as follows (in radians):
        # making a 'versor' is similar to making a rotation matrix based on some euler angles
        # qo = cos(angle/2)
        # q1 = sin(angle/2) * x
        # q2 = sin(angle/2) * y
        # q3 = sin(angle/2) * z
        # the resulting versor needs to have norm=1


        # we are going to keep track of the following dirty matrices
        # translation, rotation, scale, model, view

        # internal matrices which are only read for rendering
        # we need:
        # - individual translation, rotation and scale matrices
        # - model matrix = translation * rotation * scale
        # - 'view' matrix which is the inverse of the model
        # we could also have utilities to set them as lookat
        # maybe we might not want to calculate inverse matrices all the time
        # and we should do it only when they are requested and they are dirty

        # to multiply transformations we can use the regular '*' but that doesn't work in pygmae.
        # for pygame, use '@' as operator for matrix multiplication.
        # another alternative is to use pyrr multiplecation method that takes two matrices: pyrr.matrix44.multiply(a,b)

        # view matrix
        # takes 3 pyrr.Vector3 (which were constructed from python arrays):
        # camera position, target, up
        # view = pyrr.matrix44.create_look_at()

        # adding support to traverse the hierarchy:
        self.parent = None
        self.children = []

    # internal getters
    @property
    def position(self):
        return self._position

    @property
    def rotation(self):
        return self._rotation

    @property
    def scale(self):
        return self._scale

    # internal setters
    @position.setter
    def position(self, value):
        # print("dirtying position to {}".format(value))
        # traceback.print_stack()
        self._position = value
        self._translation_dirty = True
        self._model_dirty = True
        self._view_dirty = True

    # we were calling 'rotation' the euler angles
    # should we allow this setter?
    # yes, the 'inspector' can work based on these values
    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self._rotation_dirty = True
        self._model_dirty = True
        self._view_dirty = True

    @scale.setter
    def scale(self, value):
        self._scale = value
        self._scale_dirty = True
        self._model_dirty = True
        self._view_dirty = True

    # public api (getters)
    @property
    def translation_mat(self):
        if (self._translation_dirty):
            self._set_translation_matrix()
        return self._translation_mat

    @property
    def rotation_mat(self):
        if (self._rotation_dirty):
            self._set_rotation_matrix()
        return self._rotation_mat

    @property
    def scale_mat(self):
        if (self._scale_dirty):
            self._set_scale_matrix()
        return self._scale_mat

    @property
    def model_mat(self):
        if (self._model_dirty):
            self._set_model_matrix()
        return self._model_mat

    @property
    def view_mat(self):
        # print("getting view matrix dirty={}".format(self._view_dirty))
        if (self._view_dirty):
            self._set_view_matrix()
        return self._view_mat

    @property
    def right(self):
        if (self._model_dirty):
            self._set_model_matrix()
        # right is the first col of the model matrix
        # and it's stored in numpy matrix as the first row (mat[0])
        return self.model_mat[0,:3]

    @property
    def up(self):
        if (self._model_dirty):
            self._set_model_matrix()
        # up is the second col of the model matrix
        # and it's stored in numpy matrix as the second row (mat[1])
        return self.model_mat[1,:3]

    @property
    def forward(self):
        if (self._model_dirty):
            self._set_model_matrix()
        # up is the third col of the model matrix
        # and it's stored in numpy matrix as the third row (mat[2])
        return self.model_mat[2,:3]

    # utility to set the rotation matrix)
    def look_at(self, eye_pos, target, up):
        # local positive z
        forward = (eye_pos - target)
        # forward = forward / np.sqrt(np.sum(forward**2))
        forward = pyrr.vector.normalise(forward)
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



    # private methods
    def _set_translation_matrix(self):
        self._translation_mat = pyrr.matrix44.create_from_translation(self._position)
        self._translation_dirty = False

    def _set_rotation_matrix(self):
        # for now this is called when we modified the euler angles

        # print("updating rotation matrix of {} dirty={}".format(self.game_object.name, self._rotation_dirty))
        # traceback.print_stack()
        # rot_x = pyrr.Matrix44.from_x_rotation(self._rotation[0])
        # rot_y = pyrr.Matrix44.from_y_rotation(self._rotation[1])
        # rot_z = pyrr.Matrix44.from_z_rotation(self._rotation[2])

        # self._rotation_mat = pyrr.matrix44.create_from_translation(self._position)
        # pyrr from_eurler expects roll, pitch, yaw (that order)
        # and in radians
        # for us:
        # roll=z
        # pitch=x
        # yaw=y
        roll = math.radians(self._rotation.z)
        pitch = math.radians(self._rotation.x)
        yaw = math.radians(self._rotation.y)
        # using create from euler is not swaping
        # roll with pitch apart of being in the opposite direction (clockwise)
        # we want anticlockwise for positive angles (right hand rule)
        # euler = pyrr.euler.create(roll, pitch, yaw)
        # print("pitch={} yaw={} roll={}".format(
        #     pyrr.euler.pitch(euler),
        #     pyrr.euler.yaw(euler),
        #     pyrr.euler.roll(euler)
        # ))
        # print("rot mat")
        # print(self._rotation_mat)
        # let's debug the results

        # these have the right angle but are doing in the opposite direction
        # and we want them to follow the right hand rule
        # we need to invert them (transpose them)
        individual_x = pyrr.matrix44.create_from_x_rotation(pitch)
        individual_y = pyrr.matrix44.create_from_y_rotation(yaw)
        individual_z = pyrr.matrix44.create_from_z_rotation(roll)

        # transposing form pyrr be col-major using numpy .T
        individual_x = individual_x.T
        individual_y = individual_y.T
        individual_z = individual_z.T

        # print("rot mat x")
        # print(individual_x)
        # print("rot mat y")
        # print(individual_y)
        # print("rot mat z")
        # print(individual_z)

        # this didn't work
        # self._rotation_mat = pyrr.matrix44.create_from_eulers(euler)

        # using multiplication of individual matrices now
        # let's follow the convention
        # RxRyRz i.e we rotate first along z, then y then x
        # that mean, if we rotate in the inspector
        # first modifying x, then y and then z, the rotations
        # look right using the local space (x,y,z) space each time
        # we change an angle.
        # btw. unity follow YXZ (following that order, it looks local)
        # https://docs.unity3d.com/Packages/com.unity.mathematics@0.0/api/Unity.Mathematics.math.RotationOrder.html
        # that means, regarding multiplication
        # unity does:
        # Ry * Rx * Rz * v
        self._rotation_mat = pyrr.matrix44.multiply(
                pyrr.matrix44.multiply(individual_z, individual_y),
                individual_x)
        # print("rot mat x")
        # print(self._rotation_mat)
        # # trying to print every individual element to see if we are accessing them correctly
        # for row in range(4):
        #     for col in range(4):
        #         print("[{},{}]={}".format(row, col, self._rotation_mat[row][col]))
        #     print()
        # print()
        # since we interpret the matrix as stored by cols,
        # to get the matematical position of A(i,j) we do Mat[col, row]
        # print("checking if extraction euler angles from rot matrix is doable")
        # print("original pitch={}, yaw={}, roll={}".format(pitch, yaw, roll))
        # phi (roll) = arctan2(A31, A32)
        # theta (pitch) = arccos(A33)
        # psi (yaw) = -arctan2(A13,A23)
        # roll = 0#np.arctan2(self._rotation_mat[0][2], self._rotation_mat[1][2])
        # pitch = np.arccos(self._rotation_mat[2][2])
        # yaw = -np.arctan2(self._rotation_mat[2][0], self._rotation_mat[2][1])
        yaw = np.arcsin(self._rotation_mat[2][0])   # sin(b) = A13
        cos_beta = np.cos(yaw)
        pitch = np.arccos(self._rotation_mat[2][2]/cos_beta)
        roll = np.arccos(self._rotation_mat[0][0]/cos_beta)

        # print("original pitch={}, yaw={}, roll={}".format(pitch, yaw, roll))


        # i should update the right, up and forward accordingly
        # with pyrr: pyrr.matrix44.apply_to_vector(A, v)
        self.right = pyrr.matrix44.apply_to_vector(self._rotation_mat, pyrr.Vector3([1, 0, 0]))
        self.up = pyrr.matrix44.apply_to_vector(self._rotation_mat, pyrr.Vector3([0, 1, 0]))
        self.forward = pyrr.matrix44.apply_to_vector(self._rotation_mat, pyrr.Vector3([0, 0, 1]))

        self._rotation_dirty = False

    def _set_scale_matrix(self):
        self._scale_mat = pyrr.matrix44.create_from_scale(self._scale)
        self._scale_dirty = False

    def _set_model_matrix(self):
        if (self._translation_dirty):
            self._set_translation_matrix()
        if (self._rotation_dirty):
            self._set_rotation_matrix()
        if (self._scale_dirty):
            self._set_scale_matrix()
        self._model_mat = pyrr.matrix44.multiply(
                pyrr.matrix44.multiply(self._scale_mat, self._rotation_mat),
                self._translation_mat)
        self._model_dirty = False

    def _set_view_matrix(self):
        # print("setting view matrix t={} r={} s={} m={}".format(self._translation_dirty, self._rotation_dirty, self._scale_dirty, self._model_dirty))
        # traceback.print_stack()
        if (self._translation_dirty):
            self._set_translation_matrix()
        if (self._rotation_dirty):
            self._set_rotation_matrix()
        if (self._scale_dirty):
            self._set_scale_matrix()
        if (self._model_dirty):
            self._set_model_matrix()
        # we can either invert the model matrix
        # or we can make the inverse 'manually'
        # knowing that the view matrix is
        # view = inverse_rotation * inverse translation
        # inverse_rotation is the transpose of the rotation mat
        # and inverse_translation is using -position
        inverse_rotation = self._rotation_mat.T
        inverse_translation = pyrr.matrix44.create_from_translation(-self._position)
        self._view_mat = pyrr.matrix44.multiply(inverse_translation, inverse_rotation)
        self._view_dirty = False

    # we might want a method to get the inverse but done
    # by knowing m = t * r * s

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



