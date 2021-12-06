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

    def __init__(self):
        self.name = ""
        self.components = []
        self.transform = Transform()

    # should we accept instances or
    # we should take classes and instantiate components ourselves?
    def add_component(self, component):
        self.components.append(component)
