import OpenGL.GL as gl

from .texture import Texture

class Framebuffer:

    def __init__(self, width, height):
        self.widht = width
        self.height = height
        self.fbo = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo)

        # texture for color buffer
        self.render_texture = Texture.create(width, height)

        # attach texture to framebuffer
        gl.glFramebufferTexture2D(
            gl.GL_FRAMEBUFFER,
            gl.GL_COLOR_ATTACHMENT0,
            gl.GL_TEXTURE_2D,
            self.render_texture.texture,
            0   # mipmap level
        );

        # render buffer for depth and stencil buffers
        self.depth_stencil_render_buffer = gl.glGenRenderbuffers(1)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.depth_stencil_render_buffer);
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, width, height);
        # do we need to unbind render buffer once done configuring?
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0);
        # attach render buffer to framebuffer
        gl.glFramebufferRenderbuffer(
            gl.GL_FRAMEBUFFER,
            gl.GL_DEPTH_STENCIL_ATTACHMENT,
            gl.GL_RENDERBUFFER,
            self.depth_stencil_render_buffer
        );

        if (gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE):
            print("error creating frame buffer")

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
