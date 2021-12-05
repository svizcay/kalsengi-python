from .transform import Transform

# we need to take the decision whether we use
# a gameObject or a transform as handler
# like for parenting gameObjects
# and making the scene tree

class GameObject:

    def __init__(self):
        self.components = []
        self.transform = Transform()

    def add_component(self, component):
        self.components.append(component)
