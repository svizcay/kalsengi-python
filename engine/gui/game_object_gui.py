import imgui

from .transform_gui import TransformGUI

class GameObjectGUI:

    def __init__(self, game_object):
        self.game_object = game_object

        self.expanded = True
        self.opened = False # by default, they need to be open by double clicking in the inspector

        self.transform_gui = TransformGUI(game_object.transform)

    def draw_gui(self):
        # do not set the 'label' (id) of the window to the name of the game object.
        # the id ideally needs to be unique and invariant
        self.expanded, self.opened = imgui.begin("Inspector##{}".format(self.game_object.id), closable=True)

        self.transform_gui.draw()

        # for each component, draw its gui
        imgui.end()
