import OpenGL.GL as gl

# links to check
# https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glGetActiveUniform.xhtml
# https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glUniform.xhtml

# set of utilities to deal with gl uniforms
# the pythonic way of writing static classes (with static methods)
# is just to put free functions in a module (no need for a class)

# global dictionary that maps a type to the right glUniform call.
# given than we need a common interface, we will have to wrap all glUniform calls

# this is getting executed only when the module is somehow imported (or something from this module)
# like in the case from .gl.uniform import test_function
# print("IS THIS GETTING EXECUTED?")

# how to check parameters datatypes:
# we can use isinstance(value, datatype) -> bool
# or we can use type(value) -> datatype and then compare it.
# the difference is when value is an instance of a child class
# isinstance(value, parent_class) -> True
# but type(value) -> child_class

# wrappers
def gl_uniform_matrix(loc, value):
    # print("setting mat4 uniform")
    glUniformMatrix4fv(loc, 1, GL_FALSE, value)

# wrapper for glUniform1f,2f,3f,4f
def gl_uniform_f_(loc, *values):
    pass
    # (gl.glUniform1f(loc, values[0]) if len(values) == 1)
    # (gl.glUniform2f(loc, values[0], values[1]) if len(values) == 2)
    # (gl.glUniform3f(loc, values[0], values[1], ) if len(values) == 3)

# we can tell easily apart int from float
# can we do the same for int and uint?
# when do we need to used unsigned in glUniform?
# a) when we have in glsl unsigned int, uvec2, uvec3 or uvec4
# let's leave the unsigned part for later

# dictionary for mapping glUniformXi for different number of paraters
# used in int ivec2, ivec3, ivec4, sampler2D
glUniformXi = {
    1 : gl.glUniform1i,
    2 : gl.glUniform2i,
    3 : gl.glUniform3i,
    4 : gl.glUniform4i,
}

glUniformXf = {
    1 : gl.glUniform1f,
    2 : gl.glUniform2f,
    3 : gl.glUniform3f,
    4 : gl.glUniform4f,
}

# for matrices, we can receive the values listed as different
# parameters or they can be packed into a 'vector'

# for matrices packed as vectors (vector of N floats)
glUniformMatrixNfv = {
    2 : gl.glUniformMatrix2fv,
    3 : gl.glUniformMatrix3fv,
    4 : gl.glUniformMatrix4fv,
}

# we don't call this directly from the mesh_render
# we need to perform the 'switch' statement for other cases first
def gl_uniform(loc, *values):
    # print("entry point of glUniform loc={} values={}".format(loc,values))
    """ up to four scalars either ints or floats """
    if isinstance(values[0], int):
        # print("calling int version of glUniform for values {} len={}".format(values, len(values)))
        glUniformXi[len(values)](loc, *values)
        # if (len(values) == 1):
        #     gl.glUniform1i(loc, values[0])
        # else:
        #     glUniformXi[len(values)](loc, *values)
    elif isinstance(values[0], float):
        # print("calling float version of glUniform for values {} len={}".format(values, len(values)))
        glUniformXf[len(values)](loc, *values)
    else:
        print("couldn't determine the type for glUniform for values {}".format(values))

# for this case, we know we are dealing with vectors
def gl_uniform_matrix(loc, vector_of_values):
    # glUniformMatrix4fv(loc, 1, GL_FALSE, value)
    # print(vector_of_values)
    glUniformMatrixNfv[len(vector_of_values)](loc, 1, gl.GL_FALSE, vector_of_values)

# dictionary that maps opengl enum data types to
# our own custom methods
gl_uniform_type_to_f = {
    gl.GL_FLOAT         : gl_uniform,
    gl.GL_FLOAT_VEC2    : gl_uniform,
    gl.GL_FLOAT_VEC3    : gl_uniform,
    gl.GL_FLOAT_VEC4    : gl_uniform,
    gl.GL_INT           : gl_uniform,
    gl.GL_INT_VEC2    : gl_uniform,
    gl.GL_INT_VEC3    : gl_uniform,
    gl.GL_INT_VEC4    : gl_uniform,
    gl.GL_SAMPLER_2D    : gl_uniform,
    gl.GL_FLOAT_MAT4    : gl_uniform_matrix,
}

# entry point for setting uniforms
# this is the actual function called from the mesh renderer
# warning, we expect values to be passed as many individual parameters
# example, for color, we expect r, g, b and not a vec3 nor a python array
def set_uniform(uniform_type, loc, *values):
    # print("calling gl_uniform::set_uniform")
    gl_uniform_type_to_f[uniform_type](loc, *values)
