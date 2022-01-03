import OpenGL.GL as gl
from PIL import Image
import cv2

# do we need a vao or some shader program
# to be bound to set up textures?
class Texture:

    def __init__(self, width, height, data, texture_format, client_format):
        """ create an empty texture for rendering """
        self.width = width
        self.height = height
        self.format = texture_format
        self.client_format = client_format
        self._create_texture()
        self._transfer_data(data)

    @classmethod
    def from_image(cls, path_to_img):
        """ create a texture from an image """
        # # load image with pillow
        image = Image.open(path_to_img)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        # RGBA is a 32 bit data type for each pixel
        # 8 bits per channel = 2 hex per channel
        image_data = image.convert("RGBA").tobytes()
        return cls(image.width, image.height, image_data, gl.GL_RGBA, gl.GL_RGBA)

    @classmethod
    def from_opencv_mat(cls, mat_data):
        image = cv2.flip(mat_data, 0);
        # internal data in py-opencv is numpy
        # to get the dimensions, we use 'shape' -> height, width, channels
        height, width, channels = image.shape
        return cls(width, height, image, gl.GL_RGB, gl.GL_BGR)


    @classmethod
    def create(cls, width, height):
        return cls(width, height, None, gl.GL_RGB, gl.GL_RGB)

    def bind(self, offset = 0):
        # textures need to be bound to some texture unit
        # which of course needs to be active

        # to tell the sampler2D to use a specific texture unit,
        # we need to say so by glUniform1i (loc, tex_unit)
        texture_unit = gl.GL_TEXTURE0 + offset

        # activating the texture unit is always
        # before binding it.
        # and we need to do it every time
        # because we don't know if someone else activate
        # last time another texture unit.
        # if that were the case, then our binding would
        # happend to that texture unit and
        # our shader programs might be expecting the textures somewhere else

        gl.glActiveTexture(texture_unit);
        # print("texture {} getting bound to texture unit {} GL_TEXTURE_0={}".format(self.texture, texture_unit, gl.GL_TEXTURE0))
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture);

    def _create_texture(self):
        self.texture = gl.glGenTextures(1)
        # activate the texture unit first BEFORE binding texture
        gl.glActiveTexture(gl.GL_TEXTURE0);
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        # # wrapping parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

        # # filtering parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    def _transfer_data(self, data):
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,       # target
            0,                      # level of detail 0=base; n=nth mipmap reduction
            self.format,            # internal format (how data is stored in gpu) (texture data) -> convert to
            self.width,
            self.height,
            0,                      # border
            self.client_format,     # how data is stored in client side (pixel data) -> input image format
            gl.GL_UNSIGNED_BYTE,    # how is the representation of the data in client side (we transformed to byte before [0, 255]
            data                    # data
        )
