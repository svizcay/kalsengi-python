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
        # how can i get the GUI instances of each component without having
        # the components having a reference to them?
        # we need some manager that links components with componentsGUIs
        # and then we need to ask that manager to see if a given component has some gui to draw.
        # sound a bit complicated for now.
        # let's make each component to hold an instance to some componentGUI instance
        for component in self.game_object.components:
            if component.gui is not None:
                component.gui.draw()
        #     if isinstance(component, MeshRenderer):

        imgui.end()
