import glfw

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import imgui
# integrator (backend for imgui)
from imgui.integrations.glfw import GlfwRenderer

# from testwindow import show_test_window
# we need to let imgui create its context (nothing to do with opengl context)
# the actual opengl context is created as always using glfw and we store the 'window' (opengl context ref)
# we then create an instance of a 'python' GlfwRenderer (passing to its constructor the glfw window)
# that's all for the setup

# for the render loop:
# check window's closing status as always with glfw should close
# poll glfw events as always with glfw.poll_events
# 'gl' calls are as always
# swap buffers are always with glfw
# addiotionally, we need to let 'imgui' process input (actually we ask that to the GlfwRenderer instance)

# render loop but only related to imgui:
# start new frame with imgui.new_frame(). there is no imgui.end_frame for glfw example??
# render loop should finish with:
# - imgui.render()
# - imp (instance of glfwRenderer) imp.render(imgui.get_draw_data())
# and the swap buffers with glfw
# after imgui.new_frame, add widgets between imgui.begin("label", bool)
# and imgui.end()

# for the tearing down:
# before terminating glfw, call the shutdown of the renderer (the instance of the GlfwRenderer)

from math import sin

from .base_mesh import Triangle, BaseMesh
from .shader import Shader
from .mesh_renderer import MeshRenderer
from .texture import Texture

def resize_callback(context, width, height):
    window = glfw.get_window_user_pointer(context)
    window.resize_window(width, height)

class Window:
    # new in python 3.5:
    # even though python doesn't enforce specifying the data type for parameters
    # they can still be specified to be used by 3rd party tools
    # like type checkers, IDEs, linters, etc.
    # for paraters: <name>: <type>
    # for return values def function() -> <type>:
    def __init__(self, width: int, height: int, title: str):
        if not glfw.init():
            raise Exception("glfw could not be initialized")

        self._context = glfw.create_window(width, height, title, None, None)

        if not self._context:
            glfw.terminate()
            raise Exception("glfw could not open a window")

        glfw.set_window_pos(self._context, 400, 200)

        # set glfw user window pointer for callbacks
        glfw.set_window_user_pointer(self._context, self)

        # maybe this needs to go before setting the context as current
        glfw.set_window_size_callback(self._context, resize_callback)

        glfw.make_context_current(self._context)

        glClearColor(0.302, 0.365, 0.325, 1)

        # enabling depth, stencil, etc buffers it's not part of a global 'initial setup'.
        # this should be done for each "material" like in the same way is done in unity shaders
        # this needs to be explicit like that because we can not depend on what was rendered before had exactly the same 'opengl configuration'
        # config like that, can run in a 'pre-render' method at the shader/material level.
        # it's better to not do it at the model level (a model can be renderered with different materials which might need different opengl setup)
        glEnable(GL_DEPTH_TEST)

        # testing different viewport size and position
        # glViewport(524, 268, 450, 450)
        glEnable(GL_SCISSOR_TEST); # needed to have multiple viewports and glClear to work in a constraint area

        # to enable transparency
        glEnable(GL_BLEND) # when working with transparency, we need to somehow 'blend' colors (what is already in the canvas + what is comming on top)
        # function to use for blending
        # src = what was already in the canvas
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # i want to test every combination of vertex attributes
        # triangles = []
        # for uv in (True, None):
        #     for normal in (True, None):
        #         for color in (True, None):
        #             # triangle = Triangle(vertices, uvs=uvs, normals=normals, colors=colors)
        #             triangle = Triangle()
        #             triangles.append(triangle)
        # print(len(triangles))
        # triangle = Triangle()

        # vertex data for a triangle
        vertices = [-0.5, -0.5, 0,  # lower-left
                    0.5, -0.5, 0,   # lower-right
                    0, 0.5, 0]      # top-center

        uvs = [
            0.0, 0.0,
            1.0, 0.0,
            0.5, 1.0,
        ]

        normals = [0, 0, 1, # lower-left
                0, 0, 1,    # lower-right
                0, 0, 1]    # top-center

        colors = [1, 0, 0,
                    0, 1, 0,
                    0, 0, 1]
        triangle = BaseMesh(vertices, uvs=uvs, normals=normals, colors=colors)

        # i want to test every triangle every shader?
        # shader = Shader(vertex_src, frag_src)
        # shader = Shader("engine/shaders/simple_vertex.glsl", "engine/shaders/flat_color.glsl")
        # shader = Shader("engine/shaders/simple_vertex_color.glsl", "engine/shaders/vertex_color.glsl")
        # shader = Shader("engine/shaders/simple_vertex_uv.glsl", "engine/shaders/texture_color.glsl")
        shader = Shader("engine/shaders/simple_vertex_uv_color.glsl", "engine/shaders/texture_vertex_color.glsl")

        # mesh_renderers = []
        # for triangle in triangles:
        #     mesh_renderer = MeshRenderer(triangle, shader)
        #     mesh_renderers.append(mesh_renderer)
        # self.mesh_renderers = mesh_renderers
        self.mesh_renderer = MeshRenderer(triangle, shader)

        glUseProgram(shader.program)

        self.rotation_loc = glGetUniformLocation(shader.program, "rot");

        # # setting up textures
        texture1 = Texture("img/ash_uvgrid01.jpg")
        # texture1 = Texture("img/wall.jpg")

        # when using multiple textures, we need to get the uniform sampler location
        self.sampler0Loc = glGetUniformLocation(shader.program, "texture0");
        self.sampler1Loc = glGetUniformLocation(shader.program, "texture1");

        # imgui stuff
        # initilize imgui context (see documentation)
        # imgui.create_context() # imgui.context != opengl.context
        # self.impl = GlfwRenderer(self._context)
        # do not do the following
        # imgui.get_io().display_size = 100, 100
        # imgui.get_io().fonts.get_tex_data_as_rgba32() this is giving me error when calling imgui.render()

    def resize_window(self, width, height):
        # print("resizing window to" + str(width) + "x" + str(height))
        glViewport(0, 0, width, height)
        # we should also at this point update the projection matrix in order to reflect the new aspect ratio
        # and submit the new matrix to the uniform in the shader program

    def process_input(self):
        if (glfw.get_key(self._context, glfw.KEY_ESCAPE) == glfw.PRESS):
            # glfw.SetWindowShouldClose(self._context, true)
            glfw.set_window_should_close(self._context, True)

    def draw_imgui_example_gui(self):
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()


        imgui.begin("Custom window", True)
        imgui.text("Bar")
        imgui.text_ansi("B\033[31marA\033[mnsi ")
        imgui.text_ansi_colored("Eg\033[31mgAn\033[msi ", 0.2, 1., 0.)
        imgui.extra.text_ansi_colored("Eggs", 0.2, 1., 0.)
        imgui.end()

    def run(self):
        frame_counter = 0
        # render loop suggested by learnopengl.com
        # - process input (processLocalInput)
        # - render commands (drawTriangles, etc)
        # - check and call events -> changes are going to be ready for next frame
        # - swap buffers
        # when should we clear the framebuffer? does it make any difference making it at the end or at the beginning?
        # a) since 2003, clearing the framebuffer doesn't actually go through individual pixels clearing the color and depth buffer to some value.
        # what it does now, it stores internally the "clearing value", and then, when rendering, if no value was written into the pixel, then the clear value is used.
        while not glfw.window_should_close(self._context):

            # print("frame="+ str(frame_counter))
            currentTime = glfw.get_time()
            self.process_input()
            glfw.poll_events()
            # self.impl.process_inputs()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # self.mesh_renderers[0].render()
            self.mesh_renderer.render()
            # self.draw_cube()

            # # # start new frame context
            # imgui.new_frame()

            # # # open new window context
            # imgui.begin("Your first window!", True)

            # # # draw text label inside of current window
            # imgui.text("Hello world!")

            # # # close current window context
            # imgui.end()


            # # pass all drawing comands to the rendering pipeline
            # # and close frame context
            # imgui.render()
            # self.impl.render(imgui.get_draw_data())
            # # imgui.end_frame()

            # imgui.new_frame()

            # self.draw_imgui_example_gui()

            # imgui.render()
            # self.impl.render(imgui.get_draw_data()) # it's crashing when imgui.get_io().fonts.get_tex_data_as_rgba32()

            glfw.swap_buffers(self._context)

            frame_counter = frame_counter + 1

        # self.impl.shutdown()
        glfw.terminate()
