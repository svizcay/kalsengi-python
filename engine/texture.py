import OpenGL.GL as gl
from PIL import Image

class Texture:

    def __init__(self, path_to_img):
        texture = gl.glGenTextures(1)
        # activate the texture unit first BEFORE binding texture
        gl.glActiveTexture(gl.GL_TEXTURE0);
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

        # # wrapping parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

        # # filtering parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        # # load image with pillow
        image = Image.open(path_to_img)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        # RGBA is a 32 bit data type for each pixel
        # 8 bits per channel = 2 hex per channel
        image_data = image.convert("RGBA").tobytes()

        # transfer data
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,  # target
            0,              # level of detail 0=base; n=nth mipmap reduction
            gl.GL_RGBA,        # internal format (how data is stored in gpu) (texture data)
            image.width,
            image.height,
            0,              # border
            gl.GL_RGBA,        # how data is stored in client side (pixel data)
            gl.GL_UNSIGNED_BYTE,   # how is the representation of the data in client side (we transformed to byte before [0, 255]
            image_data      # data
        )

        # for binding textures for drawing
        # glActiveTexture(GL_TEXTURE0);
        # glBindTexture(GL_TEXTURE_2D, self.texture0);
        # glActiveTexture(GL_TEXTURE1);
        # glBindTexture(GL_TEXTURE_2D, self.texture1);
        # glUniform1i(self.sampler0Loc, 0)
        # glUniform1i(self.sampler1Loc, 1)    # 2nd argument is the texture unit (and not the id generted by genTextures??)


