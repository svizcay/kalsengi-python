import imgui

from .gui import GameObjectGUI

class Scene:

    def __init__(self):
        self.game_objects = []
        self.selected = None
        self.expanded = []
        self.guis = {}

        # for debugging. it should not be a list
        # self.selected_flags = []

    def add_game_object(self, game_object):
        self.game_objects.append(game_object)

        gui = GameObjectGUI(game_object)
        self.guis[game_object.id] = gui

        # whenever we add a game object to the scene, we are going to create its editor gui here

        self.expanded.append(False)

        # for debugging
        # self.selected_flags.append(False)

    def draw_scene(self):
        """ this method will call draw on all game objects """
        pass

    def draw_overlay(self):
        """" this method will draw things that need to be on top of everything like gizmos """
        pass

    def draw_gui(self):
        # behaviour i want.
        # scene tree
        # double click in game object will open its inspector (which can be closed)
        # single click will just make it 'selected'
        """ this will draw the scene hierarchy as a scrollable list """
        # let's make this its "own" window (like in unity is a dockable panel)
        imgui.begin("Scene Hierarchy")
        # for the list i can try to use:
        # - imgui.collapsing_header(text, visible_header, tree_flags) -> expanded, visible_header
        # for game_obj in self.game_objects:
        #     # we should display the expandable option only of the gameObject has children
        #     expanded_visible = imgui.collapsing_header(game_obj.name, None)
        #     if imgui.is_item_active():
        #         imgui.text("{} active".format(game_obj.name))
        #     if imgui.is_item_clicked():
        #         imgui.text("{} clicked".format(game_obj.name))
        #     if imgui.is_item_focused():
        #         imgui.text("{} focused".format(game_obj.name))
        #     if imgui.is_item_hovered():
        #         imgui.text("{} hovered".format(game_obj.name))

        # display list states
        # for idx, game_obj in enumerate(self.game_objects):
        interaction_values = []

        # - imgui.list_box_header/footer with imgui.selectable
        # the returned tuple has to be interpreted as:
        # opened (or clicked) if the item was click during this frame
        # selected if the current internal state of this item is selected
        imgui.listbox_header("hierarchy tree")
        for idx, game_obj in enumerate(self.game_objects):
            # opened, selected = imgui.selectable(game_obj.name, True if self.selected == game_obj else False)
            clicked, selected = imgui.selectable(
                    "> {}".format(game_obj.name),
                    True if self.selected == game_obj else False,
                    imgui.SELECTABLE_ALLOW_DOUBLE_CLICK)

            if selected:
                self.selected = game_obj
            if clicked:
                self.expanded[idx] = not self.expanded[idx]

            # detect double click in selectable
            open_inspector = imgui.is_item_hovered() and imgui.is_mouse_double_clicked()
            if open_inspector:
                self.guis[self.selected.id].opened = True

            interaction = {
                "clicked" : clicked,
                "selected" : selected,
            }
            interaction_values.append(interaction)

            # is_mouse_double_clicked is a global event (not linked to any widget)
            # double_click = imgui.is_mouse_double_clicked()
            # if (double_click):
            #     imgui.text("double click")

            # if (self.expanded[idx]):
            #     imgui.text("{} expanded".format(game_obj.name))

        imgui.listbox_footer()

        for interaction_val in interaction_values:
            imgui.text("clicked={} selected={}".format(interaction_val["clicked"], interaction_val["selected"]))

        imgui.end()

        # we need to display maybe multiple inspectors and not only the one that are active
        for game_object_id, gui in self.guis.items():
            if gui.opened:
                gui.draw_gui()
        # there are two windows to render, the hierarchy and the inspector
        # of the currrent selected object
        # if self.selected is not None and self.guis[self.selected.id].opened:
        #     self.guis[self.selected.id].draw_gui()
        #     # self.selected.draw_gui()
        #     print("gui expanded {}; gui opened {}".format(self.guis[self.selected.id].expanded, self.guis[self.selected.id].opened))
