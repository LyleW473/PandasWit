from Global.generic import Generic
from math import sin, cos, degrees, radians
from Global.settings import *
from pygame.image import load as pygame_image_load
from pygame.transform import rotozoom as pygame_transform_rotozoom

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

class ChilliProjectile(Generic):

    # Image for all chillis
    chilli_image = pygame_image_load("graphics/Projectiles/ChilliProjectile.png")

    # Default time to cover the distance travelled
    default_time_to_travel_distance_at_final_velocity = 0.22

    def __init__(self, x, y, angle, damage_amount):

        # --------------------------------------------------------------------------------
        # Movement

        # The total distance travelled (including the horizontal and vertical components)
        desired_distance_travelled = 5 * TILE_SIZE

        # Set the time for the projectile to cover the desired distance travelled to be the default time
        time_to_travel_distance_at_final_velocity = ChilliProjectile.default_time_to_travel_distance_at_final_velocity # t

        # Calculate the horizontal and vertical distance the projectile must travel based on the desired distance travelled
        horizontal_distance = desired_distance_travelled * cos(angle)
        vertical_distance = desired_distance_travelled * sin(angle)

        # Calculate the horizontal and vertical gradients
        self.horizontal_gradient = horizontal_distance / time_to_travel_distance_at_final_velocity
        self.vertical_gradient = vertical_distance / time_to_travel_distance_at_final_velocity
        """
        self.delta_time = 0
        """
        
        # -------------------------------------------------------------------------------
        # Images

        # The original image of the chilli projectile
        self.original_image = pygame_transform_rotozoom(surface = ChilliProjectile.chilli_image.convert_alpha(), angle = degrees(angle), scale = 1.25)

        # Inherit from the Generic class, which has basic attributes and methods. (Inherits from Generic and pygame.sprite.Sprite)
        Generic.__init__(self, x = x, y = y, image = self.original_image)

        # -------------------------------------------------------------------------------
        # Positioning

        """ Override the rect position, and instead position the center of the projectile at the x and y co-ordinate:
        - As the image is rotated, the image may be resized, therefore this ensures that the center of the projectile will always be at the center of the player.
        """
        self.rect.centerx = x
        self.rect.centery = y

        # The attributes that will hold the new x and y positions of the projectile (for more accurate shooting as the floating point values are saved)
        self.new_position_x = self.rect.x
        self.new_position_y = self.rect.y
    
        # Used for VFX
        self.angle = angle

        # --------------------------------------------------------------------------------
        # Damage

        # The damage amount (the damage depends on what weapon this was shot from)
        self.damage_amount = damage_amount

        # --------------------------------------------------------------------------------
        # Adding to chilli projectiles group

        ChilliProjectileController.projectiles_dict[self] = 0


    def move_projectile(self):

        # Moves the projectile

        # Horizontal movement
        self.new_position_x += self.horizontal_gradient * self.delta_time
        self.rect.x = round(self.new_position_x)

        # Vertical movement
        self.new_position_y -= self.vertical_gradient * self.delta_time
        self.rect.y = round(self.new_position_y)