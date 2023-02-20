from Global.generic import Generic
from pygame.image import load as pygame_image_load
from pygame.transform import scale as pygame_transform_scale
from pygame.mask import from_surface as pygame_mask_from_surface
from pygame import Surface as pygame_Surface
from math import sin, radians

class DiveBombAttackController(Generic):

    divebomb_circle_image = pygame_image_load("graphics/Projectiles/DiveBombCircle.png")

    def __init__(self, x, y, damage_amount, knockback_multiplier):

        # --------------------------------
        # Sin angle to change the circle radius and alpha level of the alpha surface

        self.current_sin_angle = 0
        self.new_sin_angle = 0

        # --------------------------------
        # Circles

        # The radius of the smaller circle inside the large circle that grows

        self.minimum_growing_circle_radius = 20
        self.new_growing_circle_radius = self.minimum_growing_circle_radius
        self.growing_circle_radius = self.minimum_growing_circle_radius

        # The maximum radius of the circles
        self.maximum_circle_radius = 200

        # --------------------------------
        # Alpha surface


        self.alpha_level = 0
        self.new_alpha_level = 0
        self.maximum_alpha_level = 200

        self.alpha_surface = pygame_Surface((self.maximum_circle_radius * 2, self.maximum_circle_radius * 2))
        self.alpha_surface.set_alpha(0)
        self.alpha_surface.set_colorkey("black")
        
        # -----------------------------------------------------------------------------
        # Shockwave circles

        # Alive time
        self.shockwave_circle_alive_time = 1.5
        self.shockwave_circle_alive_timer = None

        # Radius for the large circle
        self.shockwave_circle_minimum_radius = 30
        self.shockwave_circle_current_radius = self.shockwave_circle_minimum_radius
        self.shockwave_circle_maximum_radius = 150

        # Alpha level
        self.shockwave_circle_starting_alpha_level = 130
        self.shockwave_circle_alpha_level = self.shockwave_circle_starting_alpha_level 

        # Gradients
        self.shockwave_circle_alpha_level_time_gradient = (0 - self.shockwave_circle_alpha_level) / self.shockwave_circle_alive_time
        self.shockwave_circle_radius_time_gradient = (self.shockwave_circle_maximum_radius - self.shockwave_circle_minimum_radius) / (self.shockwave_circle_alive_time / 4)

        # Alpha surface for shockwave circles
        self.shockwave_circle_alpha_surface = pygame_Surface(((self.shockwave_circle_maximum_radius * 10), (self.shockwave_circle_maximum_radius * 10)))
        self.shockwave_circle_alpha_surface_size = self.shockwave_circle_alpha_surface.get_size()
        self.shockwave_circle_alpha_surface.set_alpha(255)
        self.shockwave_circle_alpha_surface.set_colorkey("black")

        # --------------------------------
        # Main

        # Inherit from the Generic class, which has basic attributes and methods. (Inherits from Generic and pygame.sprite.Sprite)
        Generic.__init__(self, x = x, y = y, image = pygame_transform_scale(DiveBombAttackController.divebomb_circle_image.convert_alpha(), (self.maximum_circle_radius * 2, self.maximum_circle_radius * 2)))

        # This will be set to the player's center
        self.landing_position = None   

        # The center of the divebomb attack will be set to the center of the locked in player position
        self.rect.centerx = x
        self.rect.centery = y

        # The amount of damage
        self.damage_amount = damage_amount

        # How impactful the knockback is
        self.knockback_multiplier = knockback_multiplier
        
        # Create / update a mask for pixel - perfect collisions
        self.mask = pygame_mask_from_surface(self.image)

    def reset_divebomb_attributes(self):

        # Landing position
        self.landing_position = None

        # Angles
        self.sin_angle_time_gradient = None
        self.new_sin_angle = 0
        self.current_sin_angle = 0
        
        # Alpha level
        self.alpha_level = 0
        self.new_alpha_level = 0
        self.alpha_surface.set_alpha(0)

        # Growing radius
        self.growing_circle_radius = self.minimum_growing_circle_radius
        self.new_growing_circle_radius = self.minimum_growing_circle_radius
        
    def change_visual_effects(self, proportional_time_remaining, delta_time):

        # Change the sin angle gradient according to how much time is left before the boss lands
        self.sin_angle_time_gradient = 360 / proportional_time_remaining

        # Increase the current sin anlge
        self.new_sin_angle += self.sin_angle_time_gradient * delta_time
        self.current_sin_angle = round(self.new_sin_angle)

        # Growing circle radius
        self.new_growing_circle_radius = min(self.maximum_circle_radius, self.minimum_growing_circle_radius + ((self.maximum_circle_radius - self.minimum_growing_circle_radius) * (sin(radians(self.current_sin_angle)))))
        self.growing_circle_radius = round(self.new_growing_circle_radius)

        # Alpha level
        self.new_alpha_level = min(125 + ((self.maximum_alpha_level - 125) * sin(radians(self.current_sin_angle))), self.maximum_alpha_level)
        self.alpha_level = round(self.new_alpha_level)
        self.alpha_surface.set_alpha(self.alpha_level)

    def change_shockwave_circles_visual_effect(self, delta_time):

        # Decrease the alpha level of the shockwave circle alpha surface
        self.shockwave_circle_alpha_level = max(0, self.shockwave_circle_alpha_level + (self.shockwave_circle_alpha_level_time_gradient * delta_time))
        self.shockwave_circle_alpha_surface.set_alpha(self.shockwave_circle_alpha_level)

        # Increase the radius of the shockwave circle
        self.shockwave_circle_current_radius += self.shockwave_circle_radius_time_gradient * delta_time

        # Decrease the timer
        self.shockwave_circle_alive_timer -= 1000 * delta_time

        # If the timer has finished counting down
        if self.shockwave_circle_alive_timer <= 0:
            # Set the timer back to None
            self.shockwave_circle_alive_timer = None
            
            # Set the alpha level back to the starting alpha level
            self.shockwave_circle_alpha_level = self.shockwave_circle_starting_alpha_level
            self.shockwave_circle_alpha_surface.set_alpha(self.shockwave_circle_alpha_level)
            self.shockwave_circle_current_radius = self.shockwave_circle_minimum_radius