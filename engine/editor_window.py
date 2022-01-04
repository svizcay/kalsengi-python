import imgui
import cv2

from .fps_counter import FPSCounter
import engine.time
import math

import engine.material_manager
from engine.gui.camera_gui import CameraGUI
from engine.gui.transform_gui import TransformGUI
from engine.texture import Texture

class EditorWindow:

    def __init__(self, main_window):
        self.open = False   # this also means visible
        self.main_window = main_window

    # is this a good pattern in python to ensure there is a method
    # call update and draw in all child classes?
    def update(self):
        pass

    def draw(self):
        pass

class OpenCVWebcamWindow(EditorWindow):

    def __init__(self, main_window):
        super().__init__(main_window)
        # since we are releasing the video every time the window gets closed
        # we also need to get the reference every time we open the window
        # it's better to initialize the webcam only if we are going to use it
        self.vid = None#cv2.VideoCapture(0)
        self.texture_webcam = None

    def update(self):
        if self.open:

            if self.vid is None:
                self.vid = cv2.VideoCapture(0)

            ret, frame = self.vid.read()
            self.texture_webcam = Texture.from_opencv_mat(frame)

    def draw(self):
        if self.open and self.texture_webcam is not None:

            imgui.set_next_window_size(-1, -1)
            expanded, opened = imgui.begin(
                "OpenCV Webcam",
                closable=True,
                # flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE
                flags=imgui.WINDOW_NO_RESIZE
            )
            self.open = opened

            if self.texture_webcam is not None:
                imgui.image(
                    self.texture_webcam.texture,
                    self.texture_webcam.width,
                    self.texture_webcam.height,
                    (0,1), (1,0)    # we invert the v in uv coords
                )

            if not self.open:
                self.vid.release()
                self.vid = None

            imgui.end()

class SceneCameraWindow(EditorWindow):

    # let's follow the next convention:
    # we receive an instance of a camera component
    # that was added to a dummy game object
    # but this dummy game object was never added to the scene.
    # we can get the transform by the references hold in the camera component.
    # we are going to instantiate the right guis (transform and camera)
    def __init__(self, main_window, camera):
        super().__init__(main_window)

        # should we receive a game object
        # or a camera component?
        # 'Camera' is a component and can not exists without a game object
        # at the same time, the GameObjectGUI component was added by Scene
        # when we add game objects but that's not the case for the scene camera

        # for now, let's use this window just as an inspector for the camera
        # component and not the transform
        self.camera = camera

        self.camera_gui = CameraGUI(self.camera)
        self.camera_transform_gui = TransformGUI(self.camera.game_object.transform)

    def draw(self):
        if self.open:
            # setting size 0 = autofit
            imgui.set_next_window_size(-1, -1)
            expanded, opened = imgui.begin(
                "Scene Camera",
                closable=True,
                # flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE
                flags=imgui.WINDOW_NO_RESIZE
            )
            self.open = opened

            # imgui.text("scene window focused = {}".format(self.scene_imgui_window_focused))
            # imgui.separator()

            self.camera_transform_gui.draw()
            self.camera_gui.draw()

            imgui.end()


class MaterialManagerWindow(EditorWindow):

    def __init__(self, main_window):
        super().__init__(main_window)

    def draw(self):
        if self.open:
            # i need to constraint the max height of this window
            target_height = int(0.7 * self.main_window.height)

            # -1 works for getting the default needed space
            imgui.set_next_window_size(-1, target_height)
            expanded, opened = imgui.begin(
                "Materials",
                closable=True,
                # flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE
                flags=imgui.WINDOW_NO_RESIZE
            )
            self.open = opened

            available_materials = engine.material_manager.get_materials_ids()

            for idx, (uuid, _) in enumerate(available_materials):
                material = engine.material_manager.get_from_id(uuid)
                material.gui.draw()
                if idx != (len(available_materials) - 1):
                    imgui.separator()

            imgui.end()

class RenderingInfoWindow(EditorWindow):

    def __init__(self, main_window):
        super().__init__(main_window)
        self.fps_counter = FPSCounter()

    def update(self):
        # maybe this should only be done if the window is open
        # update fps counter to use our new time class
        self.fps_counter.update(engine.time.time, engine.time.delta_time)

    def draw(self):
        # since these are windows, they need to start the draw method
        # calling imgui.begin
        # and imgui.end at the end

        # maybe we can set a defulat starting position
        imgui.set_next_window_size(200, 200)
        if self.open:
            expanded, opened = imgui.begin(
                "Rendering Info",
                closable=True,
                # flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE
                flags=imgui.WINDOW_NO_RESIZE
            )
            self.open = opened

            # in order to avoid having the window 'resized'
            # we should control the number of decimals or with width of the window
            imgui.text("FPS: {}".format(math.trunc(self.fps_counter.fps)))
            # print("rendering info window expanded={}, opened={}".format(expanded, opened))

            changed, value = imgui.checkbox("vsync", self.main_window.vsync)
            if changed:
                self.main_window.vsync = value

            imgui.end()


