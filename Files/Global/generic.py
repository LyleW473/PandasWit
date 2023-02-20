from pygame import sprite

class Generic(sprite.Sprite):
    def __init__(self, x, y, image = None):

        # Image
        self.image = image

        # Get the rect from the image size
        self.rect = self.image.get_rect()

        # X and Y
        self.rect.x = x
        self.rect.y = y

        # Inherit from the pygame.sprite.Sprite class (For groups)
        sprite.Sprite.__init__(self)

    def draw(self, surface, x, y):
        
        # Draw the tile onto the surface
        surface.blit(self.image, (x, y))