import glfw

import OpenGL.GL as gl

import pyrr

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

from .base_mesh import BaseMesh, Triangle, Quad, Cube
from .shader import Shader
from .mesh_renderer import MeshRenderer
from .texture import Texture
from .framebuffer import Framebuffer
from . import VertexAttrib
from .camera import Camera
from .free_fly_camera import FreeFlyCamera
from .transform import Transform
from .gui import TransformGUI
from .gui import CameraGUI


# we are not getting this callback executed anymore
# since we started using imgui
def window_size_callback(context, width, height):
    print("window size {}x{}".format(width, height))
    window = glfw.get_window_user_pointer(context)
    window.resize_window(width, height)

def framebuffer_size_callback(context, width, height):
    print("framebuffer size {}x{}".format(width, height))
    window = glfw.get_window_user_pointer(context)
    window.resize_framebuffer(width, height)

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

        full_screen = False
        self.render_scene_to_window = False

        # windowed
        if full_screen:
            self._context = glfw.create_window(width, height, title, glfw.get_primary_monitor(), None)
        else:
            self._context = glfw.create_window(width, height, title, None, None)
        # full screen

        self.framebuffer_width = self.width = width
        self.framebuffer_height = self.height = height

        if not self._context:
            glfw.terminate()
            raise Exception("glfw could not open a window")

        if full_screen:
            glfw.set_window_pos(self._context, 0, 0)
        else:
            glfw.set_window_pos(self._context, 100, 100)

        # set glfw user window pointer for callbacks
        glfw.set_window_user_pointer(self._context, self)

        # maybe this needs to go before setting the context as current
        glfw.set_window_size_callback(self._context, window_size_callback)
        glfw.set_framebuffer_size_callback(self._context, framebuffer_size_callback)

        glfw.make_context_current(self._context)

        # self.clear_color = (0.2, 0.258, 0.258) # green-grey
        self.clear_color = (0.093, 0.108, 0.108) # green-grey

        # gl.glClearColor(0.302, 0.365, 0.325, 1)# greenish
        # gl.glClearColor(0.705, 0.980, 0.992, 1)# light blue
        gl.glClearColor(*self.clear_color, 1)# red
        # gl.glClearColor(0.2, 0.258, 0.258, 1)# gray

        # enabling depth, stencil, etc buffers it's not part of a global 'initial setup'.
        # this should be done for each "material" like in the same way is done in unity shaders
        # this needs to be explicit like that because we can not depend on what was rendered before had exactly the same 'opengl configuration'
        # config like that, can run in a 'pre-render' method at the shader/material level.
        # it's better to not do it at the model level (a model can be renderered with different materials which might need different opengl setup)
        gl.glEnable(gl.GL_DEPTH_TEST)

        # testing different viewport size and position
        # glViewport(524, 268, 450, 450)
        # gl.glEnable(gl.GL_SCISSOR_TEST); # needed to have multiple viewports and glClear to work in a constraint area

        # to enable transparency
        gl.glEnable(gl.GL_BLEND) # when working with transparency, we need to somehow 'blend' colors (what is already in the canvas + what is comming on top)
        # function to use for blending
        # src = what was already in the canvas
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        self.use_imgui = True

        # SCENE BEGIN
        # scene = collection of gameObjects
        scene = []

        # floor
        self.plane_object = {}
        self.plane_object["mesh"] = Quad()

        # cube
        self.cube_object = {}
        self.cube_object["mesh"] = Cube()

        # triangle = Triangle()
        # triangle = Triangle(VertexAttrib.POS)
        # triangle = Triangle(VertexAttrib.COLOR)
        # triangle = Triangle(VertexAttrib.POS | VertexAttrib.COLOR)
        # triangle = Triangle(VertexAttrib.UV | VertexAttrib.COLOR)
        # triangle = Triangle(VertexAttrib.UV | VertexAttrib.NORMAL | VertexAttrib.COLOR)
        # triangle = Triangle(VertexAttrib.UV | VertexAttrib.COLOR)

        # i want to test every triangle every shader?
        # shader = Shader(vertex_src, frag_src)
        # shader = Shader("engine/shaders/vertex/simple_vertex.glsl", "engine/shaders/fragment/flat_color.glsl")
        # shader = Shader("engine/shaders/vertex/simple_vertex.glsl", "engine/shaders/fragment/flat_color_uniform.glsl")
        # shader = Shader("engine/shaders/vertex/simple_vertex_color.glsl", "engine/shaders/fragment/vertex_color.glsl")
        # shader = Shader("engine/shaders/vertex/simple_vertex_uv.glsl", "engine/shaders/fragment/texture_color.glsl")
        # shader = Shader("engine/shaders/vertex/simple_vertex_uv.glsl", "engine/shaders/fragment/mix_textures.glsl")
        # shader = Shader("engine/shaders/vertex/simple_vertex_uv_color.glsl", "engine/shaders/fragment/texture_vertex_color.glsl")

        # mvp shaders
        # shader = Shader("engine/shaders/vertex/simple_mvp.glsl", "engine/shaders/fragment/flat_color.glsl")
        # shader = Shader("engine/shaders/vertex/simple_mvp_uv.glsl", "engine/shaders/fragment/texture_color.glsl")
        # self.shader = Shader("engine/shaders/vertex/simple_mvp.glsl", "engine/shaders/fragment/flat_time_color.glsl")

        self.plane_object["shader"] = Shader(
            "engine/shaders/vertex/simple_mvp.glsl",
            "engine/shaders/fragment/flat_color_uniform.glsl"
        )

        # self.cube_object["shader"] = Shader("engine/shaders/vertex/simple_mvp.glsl", "engine/shaders/fragment/texture_color.glsl")
        self.cube_object["shader"] = Shader(
            "engine/shaders/vertex/simple_mvp_uv.glsl",
            "engine/shaders/fragment/mix_textures.glsl"
        )
        # self.cube_object["shader"] = Shader("engine/shaders/vertex/simple_mvp.glsl", "engine/shaders/fragment/flat_time_color.glsl")

        self.plane_object["renderer"] = MeshRenderer(
            self.plane_object["mesh"],
            self.plane_object["shader"]
        )

        self.cube_object["renderer"] = MeshRenderer(
            self.cube_object["mesh"],
            self.cube_object["shader"]
        )

        self.plane_object["transform"] = Transform()
        self.plane_object["transform"].position = pyrr.Vector3([0, 0, -1])
        self.plane_object["transform"].rotation = pyrr.Vector3([270, 0, 0])
        self.plane_object["transform"].scale = pyrr.Vector3([10,10,10])

        self.cube_object["transform"] = Transform()
        self.cube_object["transform"].position = pyrr.Vector3([0, 0.5, 0])

        self.cube_object["transform-gui"] = TransformGUI(self.cube_object["transform"])

        # # setting up textures
        self.texture1 = Texture.from_image("img/ash_uvgrid01.jpg")
        self.texture2 = Texture.from_image("img/wall.jpg")
        self.texture3 = Texture.from_image("img/awesomeface.png")


        # material initial set up (uniforms)
        gl.glUseProgram(self.plane_object["shader"].program)
        self.plane_object["renderer"].set_uniform("color", 0.349, 0.349, 0.349)

        gl.glUseProgram(self.cube_object["shader"].program)
        self.texture1.bind()
        self.cube_object["renderer"].set_uniform("texture0", 0)
        self.texture2.bind(1)
        self.cube_object["renderer"].set_uniform("texture1", 1)

        self.editor_scene_size = (890, 500)

        # scene camera
        self.camera = Camera(self.editor_scene_size[0]/self.editor_scene_size[1])
        #self.camera_transform = Transform()
        self.camera.transform.position = pyrr.Vector3([0, 1.7, 5])
        self.camera_gui = CameraGUI(self.camera)
        self.camera_transform_gui = TransformGUI(self.camera.transform)
        self.free_fly_camera = FreeFlyCamera(self.camera)

        # game camera
        self.game_camera = Camera(self.editor_scene_size[0]/self.editor_scene_size[1])
        # no need to create another transform. camera has an internal transform object
        # self.game_camera_transform = Transform()
        self.game_camera.transform.position = pyrr.Vector3([0, 1.7, 5])
        self.game_camera_gui = CameraGUI(self.camera)

        # setting up frame bufffer for the editor scene
        self.scene_framebuffer = Framebuffer(*self.editor_scene_size)

        # setting up frame buffer for the game scene
        self.game_framebuffer = Framebuffer(*self.editor_scene_size)


        if self.use_imgui:
            # imgui stuff
            # initilize imgui context (see documentation)
            imgui.create_context() # imgui.context != opengl.context
            self.impl = GlfwRenderer(self._context)
            # do not do the following
            # imgui.get_io().display_size = 100, 100
            # imgui.get_io().fonts.get_tex_data_as_rgba32() this is giving me error when calling imgui.render()
            self.scene_imgui_window_focused = False

    def resize_window(self, width, height):
        print("resizing window to {}x{}".format(width, height))
        self.width = width
        self.height = height
        # gl.glViewport(0, 0, width, height)
        # we should also at this point update the projection matrix in order to reflect the new aspect ratio
        # and submit the new matrix to the uniform in the shader program

    def resize_framebuffer(self, width, height):
        print("resizing framebuffer to {}x{}".format(width, height))
        self.framebuffer_width = width
        self.framebuffer_height = height
        gl.glViewport(0, 0, self.framebuffer_width, self.framebuffer_height)
        # we should also at this point update the projection matrix in order to reflect the new aspect ratio
        # and submit the new matrix to the uniform in the shader program
        # i should update the scene and game render textures
        # self.camera.aspect_ratio = width/height
        # self.game_camera.aspect_ratio = width/height

    def process_input(self):
        if (glfw.get_key(self._context, glfw.KEY_ESCAPE) == glfw.PRESS):
            # glfw.SetWindowShouldClose(self._context, true)
            glfw.set_window_should_close(self._context, True)
        if self.scene_imgui_window_focused:
            self.free_fly_camera.process_input(self._context, self.delta_time)

    def render_scene(self):
        # for each gameObject, activate its program and draw it
        # self.shader.use()

        # now that the program is active, update uniforms
        # print("frame="+ str(frame_counter))

        # when drawing the scene, let's draw to an offscreen framebuffer
        if not self.render_scene_to_window:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.scene_framebuffer.fbo)
            gl.glViewport(0, 0, *self.editor_scene_size)
        gl.glClearColor(*self.camera.clear_color, 1)# light blue
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


        # # this should be avoided and done only when there are changes
        # self.mvp = pyrr.matrix44.multiply(self.transform.model_mat, self.camera.projection) # this works
        # # self.mvp = self.translation * self.camera.projection # it didn't work
        # # self.mvp = self.camera.projection * self.translation
        # self.mesh_renderer.set_uniform("mvp", self.mvp) # sample2D needs the texture unit
        # self.mesh_renderer.set_uniform("time", currentTime) # sample2D needs the texture unit

        # render
        # if self.draw_scene:
        #     self.mesh_renderer.render()

        # draw plane
        self.plane_object["shader"].use()
        plane_object_mvp = pyrr.matrix44.multiply(
            pyrr.matrix44.multiply(self.plane_object["transform"].model_mat, self.camera.transform.view_mat),
            self.camera.projection)
        self.plane_object["renderer"].set_uniform("mvp", plane_object_mvp)
        self.plane_object["renderer"].render()

        # draw cube
        # self.texture1.bind()
        self.cube_object["shader"].use()
        cube_object_mvp = pyrr.matrix44.multiply(
            pyrr.matrix44.multiply(self.cube_object["transform"].model_mat, self.camera.transform.view_mat),
            self.camera.projection)
        self.cube_object["renderer"].set_uniform("mvp", cube_object_mvp)
        # we don't need to update the uniform (saying which texture unit to use)
        # but we need to make sure
        # we have the right texture bound at each texture unit
        self.texture1.bind()
        self.texture2.bind(1)
        self.cube_object["renderer"].render()
        # self.cube_object["renderer"].set_uniform("time", currentTime)
        # self.texture1.bind()
        # self.cube_object["renderer"].set_uniform("texture0", 0)

        # restore framebuffer and viewport
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        # print("restoring framebuffer {}x{}".format(self.framebuffer_width, self.framebuffer_height))
        gl.glViewport(0, 0,self.framebuffer_width, self.framebuffer_height)

    def render_game(self):
        """ similar to render scene but using a game camera."""
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.game_framebuffer.fbo)
        gl.glViewport(0, 0, *self.editor_scene_size)
        gl.glClearColor(*self.game_camera.clear_color, 1)# light blue
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # draw plane
        self.plane_object["shader"].use()
        plane_object_mvp = pyrr.matrix44.multiply(
            pyrr.matrix44.multiply(self.plane_object["transform"].model_mat, self.game_camera.transform.view_mat),
            self.game_camera.projection)
        self.plane_object["renderer"].set_uniform("mvp", plane_object_mvp)
        self.plane_object["renderer"].render()

        # draw cube
        self.cube_object["shader"].use()
        cube_object_mvp = pyrr.matrix44.multiply(
            pyrr.matrix44.multiply(self.cube_object["transform"].model_mat, self.game_camera.transform.view_mat),
            self.game_camera.projection)
        self.cube_object["renderer"].set_uniform("mvp", cube_object_mvp)
        self.texture1.bind()
        self.texture2.bind(1)
        self.cube_object["renderer"].render()

        # restore framebuffer and viewport
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glViewport(0, 0,self.framebuffer_width, self.framebuffer_height)

    def draw_gui(self):
        # begin_main_menu_bar creates a full size window with a menu bar added
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                # submenu
                if imgui.begin_menu('Open Recent', True):
                    imgui.menu_item('doc.txt', None, False, True)
                    imgui.end_menu()

                imgui.end_menu()


            imgui.end_main_menu_bar()

        region_available = imgui.get_content_region_available()
        region_max = imgui.get_content_region_max()
        # print("region available {}\nmaxregion {}".format(region_available, region_max))

        # setting size 0 = autofit
        imgui.set_next_window_size(0, 0)
        imgui.begin("Hierarchy")
        # imgui.text("test text")
        imgui.text("scene window focused = {}".format(self.scene_imgui_window_focused))
        self.cube_object["transform-gui"].draw()
        imgui.separator()
        imgui.text("scene camera")
        self.camera_transform_gui.draw()
        self.camera_gui.draw()
        changed, clear_color = imgui.color_edit3("bg color", *self.clear_color)
        if changed:
            self.clear_color = clear_color
        imgui.end()

        # # pop up example
        # imgui.begin("Example: simple popup")

        # if imgui.button("select"):
        #     imgui.open_popup("select-popup")

        # imgui.same_line()

        # if imgui.begin_popup("select-popup"):
        #     imgui.text("Select one")
        #     imgui.separator()
        #     imgui.selectable("One")
        #     imgui.selectable("Two")
        #     imgui.selectable("Three")
        #     imgui.end_popup()

        # imgui.end()
        # # end pop up example

        # let's make the window a full screen window
        #imgui.set_next_window_size(self.width, self.height)
        #imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(0, 0)
        imgui.begin(
            "Scene", # window title
            False,                      # closable
            #flags=imgui.WINDOW_MENU_BAR
            #imgui.WINDOW_NO_MOVE|
            #imgui.WINDOW_NO_COLLAPSE|
            #imgui.WINDOW_NO_RESIZE
        )


        # # # draw text label inside of current window
        # imgui.text("Hello world!")
        # the first returned value from checkbox returns click event
        # _, self.draw_scene = imgui.checkbox("draw scene?", self.draw_scene)
        # self.draw_imgui_example_gui()

        # imgui.image is considering uv=(0,0) being the top-left and (1,1) the bottom-right
        # render an image with imgui
        imgui.image(
            self.scene_framebuffer.render_texture.texture,
            self.scene_framebuffer.render_texture.width,
            self.scene_framebuffer.render_texture.height,
            (0,1), (1,0)    # we invert the v in uv coords
        )

        self.scene_imgui_window_focused = imgui.core.is_window_focused()

        # imgui.text("render scene = {}; fov = {}".format(self.draw_scene, self.vfov))
        # # # close current window context
        imgui.end()

        # game window
        imgui.set_next_window_size(0, 0)
        imgui.begin(
            "Game", # window title
            False,                      # closable
            #flags=imgui.WINDOW_MENU_BAR
            #imgui.WINDOW_NO_MOVE|
            #imgui.WINDOW_NO_COLLAPSE|
            #imgui.WINDOW_NO_RESIZE
        )
        imgui.image(
            self.game_framebuffer.render_texture.texture,
            self.game_framebuffer.render_texture.width,
            self.game_framebuffer.render_texture.height,
            (0,1), (1,0)    # we invert the v in uv coords
        )
        imgui.end()

    def render_gui(self):
        imgui.render()
        self.impl.render(imgui.get_draw_data())


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
        # render loop suggested by learnopengl.com (shaders lesson)
        # - process input (processLocalInput)
        # - clear framebuffer
        # - activate program of the obj to be rendered
        # - update uniforms of tha program
        # - (render commands) bind vao and emit draw calls (meshrenderer -> mesh)
        # - swap buffers
        # - check and call events (glfwPollEvents)-> changes are going to be ready for next frame
        # when should we clear the framebuffer? does it make any difference making it at the end or at the beginning?
        # a) since 2003, clearing the framebuffer doesn't actually go through individual pixels clearing the color and depth buffer to some value.
        # what it does now, it stores internally the "clearing value", and then, when rendering, if no value was written into the pixel, then the clear value is used.

        # integration with imgui
        # - process our input
        # - process imgui input
        # - clear framebuffer
        # - tell imgui this is a new frame
        # - render our scene
        # - declare imgui widgets
        # - render imgui (both imgui and implementation)
        # - glfw swap buffers
        # - glfw poll events
        self.previous_time = glfw.get_time()
        while not glfw.window_should_close(self._context):

            self.current_time = glfw.get_time()
            self.delta_time = self.current_time - self.previous_time

            self.process_input()

            if self.use_imgui:
                self.impl.process_inputs()

            gl.glViewport(0, 0,self.framebuffer_width, self.framebuffer_height)
            gl.glClearColor(*self.clear_color, 1)# gray
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


            if self.use_imgui:
                # # # start new frame context
                imgui.new_frame()

            self.render_scene()
            self.render_game()

            if self.use_imgui:
                self.draw_gui()
                self.render_gui()
                # do i need to call imgui.end_frame()?
                # a) no. end_frame is called automatically by imgui.render()

            frame_counter = frame_counter + 1

            glfw.swap_buffers(self._context)

            glfw.poll_events()

            self.previous_time = self.current_time

        if self.use_imgui:
            self.impl.shutdown()
        glfw.terminate()
