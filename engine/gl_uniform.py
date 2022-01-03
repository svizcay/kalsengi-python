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

# for performance, maybe i should try to link more directly
# the uniform shader type to the right function to call

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

glUniformXi2 = {
    1 : gl.glUniform1i,
    2 : gl.glUniform2i,
    3 : gl.glUniform3i,
    4 : gl.glUniform4i,
}

glUniformXf2 = {
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

# at the final opengl glUniform, then we need to unpack
def gl_uniform2(loc, values):
    # print("array id={} entry point of glUniform2 loc={} values={}".format(id(values),loc,values))
    """ up to four scalars either ints or floats """
    if isinstance(values[0], int):
        # print("calling int version of glUniform for values {} len={}".format(values, len(values)))
        glUniformXi2[len(values)](loc, *values)
        # if (len(values) == 1):
        #     gl.glUniform1i(loc, values[0])
        # else:
        #     glUniformXi[len(values)](loc, *values)
    elif isinstance(values[0], float):
        # print("calling float version of glUniform for values {} len={}".format(values, len(values)))
        glUniformXf2[len(values)](loc, *values)
    else:
        print("couldn't determine the type for glUniform for values {}".format(values))

# for this case, we know we are dealing with vectors
def gl_uniform_matrix(loc, vector_of_values):
    # glUniformMatrix4fv(loc, 1, GL_FALSE, value)
    # print(vector_of_values)
    glUniformMatrixNfv[len(vector_of_values)](loc, 1, gl.GL_FALSE, vector_of_values)

def gl_uniform_matrix2(loc, vector_of_values):
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

gl_uniform_type_to_function = {
    gl.GL_FLOAT         : gl.glUniform1f,
    gl.GL_FLOAT_VEC2    : gl.glUniform2f,
    gl.GL_FLOAT_VEC3    : gl.glUniform3f,
    gl.GL_FLOAT_VEC4    : gl.glUniform4f,
    gl.GL_INT           : gl.glUniform1i,
    gl.GL_INT_VEC2      : gl.glUniform2i,
    gl.GL_INT_VEC3      : gl.glUniform3i,
    gl.GL_INT_VEC4      : gl.glUniform4i,
    gl.GL_SAMPLER_2D    : gl.glUniform1i,
    gl.GL_FLOAT_MAT4    : gl.glUniformMatrix4fv,
}

gl_uniform_type_to_f2 = {
    gl.GL_FLOAT         : gl_uniform2,
    gl.GL_FLOAT_VEC2    : gl_uniform2,
    gl.GL_FLOAT_VEC3    : gl_uniform2,
    gl.GL_FLOAT_VEC4    : gl_uniform2,
    gl.GL_INT           : gl_uniform2,
    gl.GL_INT_VEC2    : gl_uniform2,
    gl.GL_INT_VEC3    : gl_uniform2,
    gl.GL_INT_VEC4    : gl_uniform2,
    gl.GL_SAMPLER_2D    : gl_uniform2,
    gl.GL_FLOAT_MAT4    : gl_uniform_matrix2,
}

# entry point for setting uniforms
# this is the actual function called from the mesh renderer
# warning, we expect values to be passed as many individual parameters
# example, for color, we expect r, g, b and not a vec3 nor a python array
def set_uniform(uniform_type, loc, *values):
    # print("calling gl_uniform::set_uniform")
    gl_uniform_type_to_f[uniform_type](loc, *values)

# 2nd version that always receive a list
# therefore, the caller needs to put the values in a list
# independently of the nr of values
# there is a huge performance drop by calling this function
# even if inside this function we set the uniform directly.

# now that i tested again, we got that it takes the
# same amount of time if i call directly inside here
def set_uniform2(uniform_type, loc, values):
    # print("calling gl_uniform::set_uniform")
    # the next line is the bottle neck!!!
    # gl_uniform_type_to_f2[uniform_type](loc, values)

    # debugging. we know we are testing this with a vec3
    gl.glUniform3f(loc, *values)

    # debugging 2: semi-direct
    # this is also kind of okay
    # glUniformXf2[3](loc, *values)

    # debugging 3: semi-direct
    # a tiny bit of performance drop (around 5fps)
    # gl_uniform2(loc, values)

    # debugging 4: semi-direct while getting the function
    # huge performance drop
    # even without setting the uniform (just by checking what's the function)
    # f = gl_uniform_type_to_f2[uniform_type]
    # print("uniform type {} and function {}".format(uniform_type, f))
    # a tiny bit of performance drop (around 5fps)
    # gl_uniform2(loc, values)

    # let's try to avoid the dictionary-switch-statement
    # by a simple if-else
    # horrible performance. i could say even worse than before
    # type of uniform_type is a numpy uintc (c compatible unsgined)
    # print(type(uniform_type))
    # is the problem using this data type as key and comparing keys?
    # if (
    #     uniform_type == gl.GL_FLOAT or
    #     uniform_type == gl.GL_FLOAT_VEC2 or
    #     uniform_type == gl.GL_FLOAT_VEC3 or
    #     uniform_type == gl.GL_FLOAT_VEC4 or
    #     uniform_type == gl.GL_INT or
    #     uniform_type == gl.GL_INT_VEC2 or
    #     uniform_type == gl.GL_INT_VEC3 or
    #     uniform_type == gl.GL_INT_VEC4 or
    #     uniform_type == gl.GL_SAMPLER_2D
    # ):
    #     # gl_uniform2(loc, values)
    #     gl.glUniform3f(loc, *values)
