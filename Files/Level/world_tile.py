from Global.generic import Generic

class WorldTile(Generic):
    def __init__(self, x, y, image):

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x, y = y, image = image)