from Global.generic import Generic
from Level.Objects.projectiles import ChilliProjectile
from Level.Objects.projectiles import StompNode

from math import sin, cos, radians, degrees, pi
from random import randrange as random_randrange

from pygame.image import load as pygame_image_load
from pygame.transform import scale as pygame_transform_scale
from pygame.mask import from_surface as pygame_mask_from_surface
from pygame import Surface as pygame_Surface


class ChilliProjectileController:

    # projectiles_dict self.chilli_projectiles_dict (Set when the Golden Monkey boss is spawned)


    # spiral_attack_angle_time_gradient = ?? (Set to be synced with the duration of the monkey)
    
    # Displacement so that the chillis spawn a small distance from the center of the boss
    displacement_from_center_position = 20

    # An additional y displacement so that the chillis are spawned a little bit further down from the center of the boss (looks better)
    additional_y_displacement_to_position_under_boss = 15

    # Base damage for each chilli projectile
    base_damage = 15

    def __init__(self):
        # The starting angle of the spiral attack
        self.spiral_attack_starting_angle = 0

        # (Will be set when the boss starts attacking)
        self.boss_center_position = None
        
        # The number of spiral lines
        self.number_of_spiral_lines = 3

    def increase_spiral_attack_angle(self, delta_time):

        # Increases the angle of the spiral attack

        self.spiral_attack_starting_angle += ChilliProjectileController.spiral_attack_angle_time_gradient * delta_time

    def create_spiral_attack(self):

        # Creates the spiral attack
        
        # For each spiral line
        for i in range(0, self.number_of_spiral_lines):
            
            # The projectile angle
            projectile_angle = radians(self.spiral_attack_starting_angle + (i * (360 / self.number_of_spiral_lines)))

            # Create a chilli projectile (automatically added to the chilli projectiles dict)
            self.create_chilli_projectile(

                                    x_pos = self.boss_center_position[0] + (ChilliProjectileController.displacement_from_center_position * cos(projectile_angle)),
                                    y_pos = (self.boss_center_position[1] - (ChilliProjectileController.displacement_from_center_position * sin(projectile_angle))) + ChilliProjectileController.additional_y_displacement_to_position_under_boss,
                                    angle = projectile_angle,
                                    damage_amount = ChilliProjectileController.base_damage
            )

    def update_chilli_projectiles(self, delta_time, camera_position, surface):
        
        # For each chilli projectile
        for chilli_projectile in ChilliProjectileController.projectiles_dict.keys():

            # Update the chilli projectile's delta time
            chilli_projectile.delta_time = delta_time

            # Move the projectile
            chilli_projectile.move_projectile()

            # Draw the projectile
            chilli_projectile.draw(
                                surface = surface,
                                x = chilli_projectile.rect.x - camera_position[0],
                                y = chilli_projectile.rect.y - camera_position[1],
                                )

    def create_chilli_projectile(self, x_pos, y_pos, angle, damage_amount):

        # Creates a single chilli projectile (automatically added to the chilli projectiles dict)

        ChilliProjectile(
                        x = x_pos,
                        y = y_pos,
                        angle = angle,
                        damage_amount = damage_amount
                        )

class StompController:

    # stomp_controller_nodes_group = pygame.sprite.Group() [Created when the golden monkey boss is spawned]

    def __init__(self, scale_multiplier):

        # Series of "nodes", which will spread out to a maximum distance 

        # Starting / minimum radius of each node
        self.minimum_node_radius = 20 / scale_multiplier
            
        # Maximum radius of each node
        self.maximum_node_radius = 40 / scale_multiplier
        
        # Starting angle for the stomp nodes
        self.starting_angle = 0

        # Save the last animation index that the stomp attacks were created, so that only one set of stomp attack nodes are created per stomp
        self.last_animation_index = None

    def create_stomp_nodes(self, center_of_boss_position, desired_number_of_nodes, attack_variation):

        # -----------------------------------------------------------------------
        # Calculations for the radius of each stomp node and the angle change
        
        # Given a desired number of "nodes" and the radius of each node, calculate the circumference and diameter
        radius_of_each_node = self.minimum_node_radius 

        # Equation: Radius of each node = (circumference / number of nodes) / 2, rearranged to calculate circumference
        calculated_circumference = 2 * radius_of_each_node * desired_number_of_nodes

        # Equation: Circumference = pi x diameter, rearranged to find diameter
        calculated_diameter = calculated_circumference / pi

        # Radius = 1/2 * diameter
        calculated_radius = calculated_diameter / 2

        # The angle change between each node should be 2pi / the number of nodes
        angle_change = (2 * pi / desired_number_of_nodes)

        # -----------------------------------------------------------------------
        # Setting the attack variation

        # If this is the first variation
        # No angle change
        if attack_variation == 0:
            if self.starting_angle != 0:
                self.starting_angle = 0

        # If this is the second variation
        # Changes angle every stomp
        elif attack_variation == 1:
            # Increase the starting angle by half the angle change
            self.starting_angle += (angle_change / 2)

            # If the starting angle is around 360 degrees, reset the starting angle
            if round(degrees(self.starting_angle)) == 360:
                self.starting_angle = 0

        # If this is the third variation
        # Random angle change every stomp
        elif attack_variation == 2:
            # Choose a random starting angle from 0 to 360 degrees
            self.starting_angle = radians(random_randrange(0, 360))

        # -----------------------------------------------------------------------
        # Creating the stomp nodes

        for i in range(0, desired_number_of_nodes):

            # Create a stomp node (automatically added to the stomp nodes group when instantiated)
            StompNode(
                    x = center_of_boss_position[0] + (calculated_radius * cos(self.starting_angle + (i * angle_change))), 
                    y = center_of_boss_position[1] + (calculated_radius * sin(self.starting_angle + (i * angle_change))) + 20, # + 20 so that the stomp nodes are displaced to be positioned below the boss
                    radius = self.minimum_node_radius,
                    maximum_radius = self.maximum_node_radius,
                    angle = self.starting_angle + (i * angle_change) # Angle that the node will travel towards
                     ),

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
