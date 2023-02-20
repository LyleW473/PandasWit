from Global.generic import Generic
from Global.settings import TILE_SIZE
from pygame.image import load as pygame_image_load

class BambooPile(Generic):

    # Bamboo pile image
    pile_image = pygame_image_load("graphics/Misc/BambooPile.png")
    
    # Dictionary containing information relating to bamboo piles
    bamboo_pile_info_dict = {
                            "BambooResourceReplenishAmount": 15,
                            "HealthReplenishmentAmount": 20,
                            "SpawningCooldown": 2500, 
                            "SpawningCooldownTimer": 2500,
                            "MinimumSpawningDistanceFromMiddle": 5 * TILE_SIZE,
                            "MaximumSpawningDistanceFromMiddle": 25 * TILE_SIZE,
                            "MaximumNumberOfPilesAtOneTime": 6,
                            }

    def __init__(self, x, y):

        # Inherit from the Generic class, which has basic attributes and methods. (Inherits from Generic and pygame.sprite.Sprite)
        Generic.__init__(self, x = x, y = y, image = BambooPile.pile_image)