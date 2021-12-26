import imgui

from .transform import Transform

# we need to take the decision whether we use
# a gameObject or a transform as handler
# like for parenting gameObjects
# and making the scene tree

# let's use gameObjects
# in the same way unity does.
# unity doesn't allow you to create instances of transform
# by yourself.
# Transforms are created when creating gameObjects

# in unity, to go through a hierarchy, we do it using
# the transform and not the gameObject

class GameObject:
    nr_instances = 0

    def __init__(self, name=""):
        self.id = GameObject.nr_instances
        self.name = name
        self.components = []
        self.transform = Transform(game_object=self)

        GameObject.nr_instances = GameObject.nr_instances + 1

    # should we accept instances or
    # we should take classes and instantiate components ourselves?
    # no need to do weird things, just past the type as parameter
    # and then use the parameter name as a constructor.
    # a unity, let's return the component
    def add_component(self, component_type, *params):
        component = component_type(self, *params)
        self.components.append(component)
        return component
