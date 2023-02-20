from Global.generic import Generic
from pygame.sprite import Sprite as pygame_sprite_Sprite
from pygame import Rect as pygame_Rect
from math import pi, cos, sin, radians, degrees
from Global.settings import TILE_SIZE
from pygame.image import load as load_image
from pygame.transform import scale as scale_image
from random import randrange as random_randrange

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

class StompNode(pygame_sprite_Sprite):

    # This image is only used for masks
    base_image = load_image("graphics/BossAttacks/StompAttack.png").convert_alpha()

    def __init__(self, x, y, radius, maximum_radius, angle):

        # Inherit from the pygame.sprite.Sprite class
        pygame_sprite_Sprite.__init__(self)

        # The stomp attack will start below the center of the boss, b
        self.rect = pygame_Rect(x - radius, y - radius, radius * 2, radius * 2)

        # Add the node to the stomp nodes group
        StompController.nodes_group.add(self)

        # ------------------------------------------------------------------------------
        # Movement

        # The total distance travelled (including the horizontal and vertical components)
        desired_distance_travelled = 4 * TILE_SIZE

        # The time for the projectile to cover the desired distance travelled
        time_to_travel_distance_at_final_velocity = 0.35 # t

        # Calculate the horizontal and vertical distance the projectile must travel based on the desired distance travelled
        horizontal_distance = desired_distance_travelled * cos(angle)
        vertical_distance = desired_distance_travelled * sin(angle)

        # Calculate the horizontal and vertical gradients
        self.horizontal_gradient = horizontal_distance / time_to_travel_distance_at_final_velocity
        self.vertical_gradient = vertical_distance / time_to_travel_distance_at_final_velocity

        # The attributes that will hold the new x and y positions of the projectile / node (for more accurate movement as the floating point values are saved)
        self.new_position_centerx = self.rect.centerx
        self.new_position_centery = self.rect.centery   

        # ------------------------------------------------------------------------------
        # Dynamic radius

        # Time to increase from the minimum radius to the maximum radius
        time_to_increase_from_min_to_max_radius = 2.5
        
        # The rate of change in the radius over time
        self.radius_time_gradient = (maximum_radius - radius) / time_to_increase_from_min_to_max_radius

        # Attribute to save the radius for floating point accuracy when rounding
        self.new_radius = radius

        # ------------------------------------------------------------------------------
        # Other

        # Image used for mask collision
        self.image = scale_image(StompNode.base_image, (radius * 2, radius * 2))

        # The radius of the stomp node
        self.radius = radius

        # The amount of damage that the stomp node deals
        self.damage_amount = 10

        # --------------------------------------
        # Reflected

        # Attribute used so that the boss only takes damage when the projectile was reflected at it
        self.reflected = False

        # The additive colour added on top of the default colours for the stomp attack node
        self.reflected_additive_colour = [200, 200] # 1st item is the original, 2nd item is the one that changes

        # The rate of change of the angle over time (time in seconds)
        self.reflected_angle_time_gradient = (360 - 0) / 2

        # The sin angle used to assign the current colour
        self.reflected_current_sin_angle = 0

    def move(self, delta_time):

        # Moves the projectile / node

        # Horizontal movement
        self.new_position_centerx += self.horizontal_gradient * delta_time
        self.rect.centerx = round(self.new_position_centerx)

        # Vertical movement
        self.new_position_centery += self.vertical_gradient * delta_time
        self.rect.centery = round(self.new_position_centery)

    def increase_size(self, delta_time):

        # Increases the size of the stomp node, in place
        
        # Save the center of the stomp node before adjusting the radius
        # Note: This is because adjusting with small values of the radius is inaccurate
        center_before_changing = self.rect.centerx

        # Increase the radius
        self.new_radius += self.radius_time_gradient * delta_time
        self.radius = round(self.new_radius)

        # Set the width and height as the new radius
        self.rect.width = self.radius * 2
        self.rect.height = self.radius * 2

        # Set the center back to the original center 
        self.rect.centerx = center_before_changing

    def rescale_image(self):

        # Rescales the image for pixel-perfect collision 
        # Note: This is done when the rect of the stomp attack node collides with something (So that we only scale the image when we want to check for pixel perfect collision)

        # Rescale to be the diameter of the image
        self.image = scale_image(StompNode.base_image, (self.radius * 2, self.radius * 2))

    def change_reflected_colour_value(self, delta_time):
        
        # Changes the colour value of the reflected additive colour over time

        # Set the reflected additive colour to oscillate between 0 and the original reflected additive colour
        self.reflected_additive_colour[1] = self.reflected_additive_colour[0]  * (sin(radians(self.reflected_current_sin_angle)) ** 2)

        # Increase the current sin angle over time
        self.reflected_current_sin_angle += self.reflected_angle_time_gradient * delta_time