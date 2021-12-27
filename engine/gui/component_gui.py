class ComponentGUI:

    # label it's the visible part of the 'label'
    @staticmethod
    def get_unique_imgui_label(label, unique_id, classname):
        return "{}##{}{}".format(label, unique_id, classname)

