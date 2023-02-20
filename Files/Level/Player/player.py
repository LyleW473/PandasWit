from Global.generic import Generic
from Global.settings import *
from Level.Player.building_tile import BuildingTile
from Level.Player.bamboo_projectiles import BambooProjectile
from math import degrees, sin, cos, atan2, pi, dist
from Global.functions import change_image_colour
from Global.functions import sin_change_object_colour
from os import listdir as os_list_dir
from pygame.image import load as pygame_image_load
from pygame.transform import flip as pygame_transform_flip
from pygame.sprite import Sprite as pygame_sprite_Sprite
from pygame.key import get_pressed as pygame_key_get_pressed
from pygame import K_w as pygame_K_w
from pygame import K_a as pygame_K_a
from pygame import K_s as pygame_K_s
from pygame import K_d as pygame_K_d
from pygame import K_r as pygame_K_r
from pygame import K_SPACE as pygame_K_SPACE
from pygame import Rect as pygame_Rect
from pygame.mouse import get_pressed as pygame_mouse_get_pressed
from pygame.mouse import get_pos as pygame_mouse_get_pos
from pygame.draw import rect as pygame_draw_rect
from pygame.draw import circle as pygame_draw_circle
from pygame.mask import from_surface as pygame_mask_from_surface
from random import choice as random_choice
from math import radians


class Player(Generic):
    
    def __init__(self, x, y, surface, sprite_groups):
        
        # Surface that the player is drawn onto
        self.surface = surface

        # The sprite groups that the player interacts with
        self.sprite_groups = sprite_groups

        # Saves the original player's position so that when the game is reset, the player can be repositioned at the same spawn location
        self.original_player_position = (x, y)

        # ---------------------------------------------------------------------------------
        # Movement

        self.declare_movement_attributes()

        # ---------------------------------------------------------------------------------
        # Animations

        # Load the animation images
        self.load_animations()

        # Inherit from the Generic class, which has basic attributes and methods (The image is set to the thinnest image)
        Generic.__init__(self, x = x, y = y, image = self.animations_dict[self.current_player_element]["Idle"]["Right"][self.animation_index])

        # Inherit from pygame's sprite class
        pygame_sprite_Sprite.__init__(self) 

        # ---------------------------------------------------------------------------------
        # Collisions
        """
        self.camera_position = None # Position of the camera. This is updated inside "Game" class
        self.last_tile_position = None # Position of the last tile that the player can be on. This will be updated by "Game" when the level is created
        self.boss_rect = None # Reference to the current boss' rect, updated by the "Game" when a boss has been spawned
        """
        self.neighbouring_tiles_dict = {} # Used to hold the neighbouring tiles near the player (i.e. within 1 tile of the player, horizontally and vertically)
        self.dx = 0 # The distance the player can move based on if there were any collisions
        self.dy = 0 # The distance the player can move based on if there were any collisions

        # Collision tolerance
        """ Explanation:
        - This is because the difference between the points of collision most likely won't always be 0
        - This means that as soon as we find a collision between a tile and a player, where the difference between the two points (i.e. the sides of each item) is less than the collision tolerance, then this will register as a collision.
        - So if the difference between the points of collision is less than the collision tolerance, then this will be detected as a collision
        """
        self.collision_tolerance = 18
        
        # ---------------------------------------------------------------------------------
        # Angles
        """
        self.look_angle = 0
        """

        # ---------------------------------------------------------------------------------
        # Shooting, building etc.

        # Note: Time and cooldowns are measured in milliseconds

        # A dictionary containing information such as the HP the player has, the current tool equipped, amount of bamboo resource, etc.
        self.player_gameplay_info_dict = {

                                        # Holds a boolean value to allow the player to shoot / move, etc, depending on if the camera panning for spawning the boss has been completed
                                        "CanStartOperating": True, # This will be set to False when the camera panning starts, and then back to True once complete

                                        # Current tool equipped
                                        "CurrentToolEquipped": "BambooAssaultRifle",

                                        # Bamboo resource
                                        "AmountOfBambooResource": 90,
                                        "MaximumAmountOfBambooResource": 90,

                                        # Health
                                        "CurrentHealth": 100,
                                        "MaximumHealth": 100,

                                        # ------------------------------------------------
                                        # Frenzy mode
                                        "CurrentFrenzyModeValue": 0, # The starting frenzy mode value
                                        "MaximumFrenzyModeValue": 100,
                                        
                                        # Values for increasing the current frenzy mode value depending on what the player did
                                        "DealDamageFrenzyModeIncrement": 0.5, 
                                        "TakeDamageFrenzyModeIncrement": 0.5,
                                        "BlockDamageFrenzyModeIncrement": 0.25,
                                        "ReflectDamageFrenzyModeIncrement": 0.75, 
                                        "StunEnemyFrenzyModeIncrement": 5,
                                        
                                        # Time 
                                        "FrenzyModeTime": 6000, # Duration of the frenzy mode in milliseconds
                                        "FrenzyModeTimer": None,
                                        
                                        # Gradient to decrease the frenzy mode value from the highest value to the lowest value
                                        "FrenzyModeValueGradient": ((0 - 100)) / 6,
                                        "FrenzyModeFireRateBoost": 1, # The increased fire rate multiplier
                                        
                                        
                                        # Frenzy mode visual effect
                                        "FrenzyModeVisualEffectMinMaxColours" : ((128, 50, 128), (255, 50, 180)),
                                        "FrenzyModeVisualEffectColour": [255 , 50, 180], # Have the visual effect colour start at either min or max colour (does not matter which one)
                                        "FrenzyModeVisualEffectAngleTimeGradient": (360 - 0) / 0.8, # The rate of change of the angle over time (time in seconds)
                                        "FrenzyModeVisualEffectCurrentSinAngle": 0,
                                        "FrenzyModeVisualEffectRGBValuesPlusOrMinus": (1, 0, -1),

                                        # ------------------------------------------------
                                        # Damage flash effect
                                        "DamagedFlashEffectTime": 150, # The time that the flash effect should play when the player is damaged
                                        "DamagedFlashEffectTimer": None,


                                        # ------------------------------------------------
                                        # Knockback

                                        "KnockbackTime": 320, # Time that the player is knocked back for in milliseconds
                                        "KnockbackTimer": None,
                                        "KnockbackDistanceTravelled": 8 * TILE_SIZE, # The distance the player will travel 

                                        # Gradients are set when the player is knocked back by a boss
                                        # "KnockbackHorizontalDistanceTimeGradient": None,
                                        # "KnockbackVerticalDistanceTimeGradient": None,

                                        # ------------------------------------------------
                                        # Invincibility timer (used after the player is knocked back by the boss so that they aren't stuck inside corners, etc.)
                                        "InvincibilityTime": 3000,
                                        "InvincibilityTimer": None,
                                        "BlinkingInvincibilityVisualEffectAngleChange": 35,
                                        "BlinkingInvincibilityVisualEffectAngleTimeGradient": 35 / 1, # Keep the first number to be the same as the angle change (they are the same thing)
                                        "BlinkingInvincibilityVisualEffectCurrentSinAngle": 0,
                                        "BlinkingInvincibilityVisualEffectOriginalColour": (0, 100, 125),
                                        "BlinkingInvincibilityVisualEffectColourAdjusterIndex": (0, 1, 1), # Which RGB values in the colour should be adjusted (0 = don't adjust, 1 = adjust)
                                        "BlinkingInvincibilityVisualEffectColour": [0, 100, 125],


                                        # ------------------------------------------------
                                        # Angled Polygons visual effect

                                        "AngledPolygonsShootingSpawningPosition": 0,
                                        "AngledPolygonsShootingAngle": 0
                                         }


        # A dictionary containing the tools and information relating to those tools
        self.tools  =  {
                        "BuildingTool": {
                                        "Images": { 
                                            "IconImage": pygame_image_load("graphics/Weapons/BuildingTool/IconImage.png").convert_alpha(),
                                            "Up": pygame_image_load("graphics/Weapons/BuildingTool/Default.png").convert_alpha(),
                                            "TileImage": pygame_image_load("graphics/Weapons/BuildingTool/BuildingTile.png").convert()
                                                  },
                                        "MaximumBuildingTileHP": 100,
                                        "MaximumPlacingAndRemovingDistance": 7 * TILE_SIZE , #25 * TILE_SIZE, #7 * TILE_SIZE,
                                        "MinimumPlacingDistance": 1.5 * TILE_SIZE,
                                        "ExistingBuildingTilesList": [],
                                        "MaximumNumberOfTilesAtOneTime": 5,

                                        # Timers
                                        "RemovalCooldown": 150,
                                        "RemovalCooldownTimer": None,
                                        
                                        # Additional
                                        "BambooResourceDepletionAmount": 2,
                                        "ReflectionDamageMultiplier": 5
                                        },

                        "BambooAssaultRifle": { 
                            "Images" : {
                                "IconImage": pygame_image_load("graphics/Weapons/BambooAR/UpRight.png").convert_alpha(),
                                "Left": pygame_transform_flip(surface = pygame_image_load(f"graphics/Weapons/BambooAR/Right.png").convert_alpha(), flip_x = True, flip_y = False),
                                "Right": pygame_image_load("graphics/Weapons/BambooAR/Right.png").convert_alpha(),
                                "Up": pygame_image_load("graphics/Weapons/BambooAR/Up.png").convert_alpha(),
                                "Up Left": pygame_transform_flip(surface = pygame_image_load("graphics/Weapons/BambooAR/UpRight.png").convert_alpha(), flip_x = True, flip_y = False),"UpLeft": pygame_transform_flip(surface = pygame_image_load(f"graphics/Weapons/BambooAR/UpRight.png").convert_alpha(), flip_x = True, flip_y = False),
                                "Up Right": pygame_image_load("graphics/Weapons/BambooAR/UpRight.png").convert_alpha(),
                                "Down": pygame_transform_flip(surface = pygame_image_load("graphics/Weapons/BambooAR/Up.png").convert_alpha(), flip_x = False, flip_y = True),
                                "Down Left": pygame_transform_flip(surface = pygame_image_load("graphics/Weapons/BambooAR/DownRight.png").convert_alpha(), flip_x = True, flip_y = False),
                                "Down Right": pygame_image_load("graphics/Weapons/BambooAR/DownRight.png").convert_alpha()
                                        },
                            "ShootingCooldown": 125,
                            "ShootingCooldownTimer": None, # 150 so that the player starts off being unable to shoot (after pressing the play button)
                            "BambooResourceDepletionAmount": 0.5,
                            "WeaponDamage": 25
                                        
                                             },
                    
                        "BambooLauncher": {
                                            "Images": {
                                                "IconImage": pygame_image_load("graphics/Weapons/BambooLauncher/DownRight.png").convert_alpha(),
                                                "Left": pygame_transform_flip(surface = pygame_image_load(f"graphics/Weapons/BambooLauncher/Right.png").convert_alpha(), flip_x = True, flip_y = False),
                                                "Right": pygame_image_load("graphics/Weapons/BambooLauncher/Right.png").convert_alpha(),
                                                "Up": pygame_image_load("graphics/Weapons/BambooLauncher/Up.png").convert_alpha(),
                                                "Up Left": pygame_transform_flip(surface = pygame_image_load("graphics/Weapons/BambooLauncher/UpRight.png").convert_alpha(), flip_x = True, flip_y = False),"UpLeft": pygame_transform_flip(surface = pygame_image_load(f"graphics/Weapons/BambooLauncher/UpRight.png").convert_alpha(), flip_x = True, flip_y = False),
                                                "Up Right": pygame_image_load("graphics/Weapons/BambooLauncher/UpRight.png").convert_alpha(),
                                                "Down": pygame_transform_flip(surface = pygame_image_load("graphics/Weapons/BambooLauncher/Up.png").convert_alpha(), flip_x = False, flip_y = True),
                                                "Down Left": pygame_transform_flip(surface = pygame_image_load("graphics/Weapons/BambooLauncher/DownRight.png").convert_alpha(), flip_x = True, flip_y = False),
                                                "Down Right": pygame_image_load("graphics/Weapons/BambooLauncher/DownRight.png").convert_alpha()
                                                      },
                                            "ShootingCooldown": 700, 
                                            "ShootingCooldownTimer": None,
                                            "BambooResourceDepletionAmount": 15,
                                            "WeaponDamage": 120,
                                            "MiniProjectilesDamage": 10,
                                            "NumberOfMiniProjectiles": 12
                                          },

                        }

    # ---------------------------------------------------------------------------------
    # Animations

    def reset_player(self):

        # Resets all the attributes that need to be reset when the game is restarted
        # Note: Building tiles list and neighbouring tiles dict is reset as part of the game reset method so that empty tiles can be added back to the empty tiles dictionary
        
        # -----------------------------------------------------------------------------------------
        # Animation / direction
        self.current_player_element = "Normal"
        self.current_animation_state = "Idle"
        self.player_direction = ["Down"]
        self.current_look_direction = "Down"
        self.animation_index = 0
        self.animation_frame_counter = 0

        # -----------------------------------------------------------------------------------------
        # Main gameplay
        self.player_gameplay_info_dict["CanStartOperating"] = True
        self.player_gameplay_info_dict["CurrentToolEquipped"] = "BambooAssaultRifle"
        self.player_gameplay_info_dict["CurrentFrenzyModeValue"] = 0
        self.player_gameplay_info_dict["AmountOfBambooResource"] = self.player_gameplay_info_dict["MaximumAmountOfBambooResource"]
        self.player_gameplay_info_dict["CurrentHealth"] = self.player_gameplay_info_dict["MaximumHealth"]

        # Reset boss rect back to None, so that the player does not lose bamboo when shooting or building before a boss has been spawned
        self.boss_rect = None
        
        # -----------------------------------------------------------------------------------------
        # Movement
        self.declare_movement_attributes()

        # -----------------------------------------------------------------------------------------
        # Timers

        # Resetting timers in the player gameplay information dictionary
        for component in self.player_gameplay_info_dict.keys():
            # If the timer inside the player gameplay information dictionary is not None
            if "Timer" in component and self.player_gameplay_info_dict[component] != None:
                # Set it to None
                self.player_gameplay_info_dict[component] = None

        # Resetting the timers for each tool
        for tool_dict in self.tools.keys():
            # For component for each tool
            for component in self.tools[tool_dict].keys():
                # If the timer for the tool is not None
                if "Timer" in component and self.tools[tool_dict][component] != None:
                    # Set it to None
                    self.tools[tool_dict][component] = None

    def load_animations(self):
        
        # Loads the animation images for the player and places them inside their respective dictionaries.

        # Set the default player version, state , player direction and look direction
        self.current_player_element = "Normal"
        self.current_animation_state = "Idle"
        self.player_direction = ["Down"]
        self.current_look_direction = "Down"

        # A dictionary that will hold all of the animations
        self.animations_dict = {"Normal": {
        "Idle": {
            "Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Player/Normal/Idle/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os_list_dir("graphics/Player/Normal/Idle/Right")))),
            "Right": tuple(pygame_image_load(f"graphics/Player/Normal/Idle/Right/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Idle/Right")))),
            "Up": tuple(pygame_image_load(f"graphics/Player/Normal/Idle/Up/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Idle/Up")))),
            "Up Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Player/Normal/Idle/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os_list_dir("graphics/Player/Normal/Idle/UpRight")))),
            "Up Right": tuple(pygame_image_load(f"graphics/Player/Normal/Idle/UpRight/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Idle/UpRight")))),
            "Down": tuple(pygame_image_load(f"graphics/Player/Normal/Idle/Down/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Idle/Down")))),
            "Down Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Player/Normal/Idle/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os_list_dir("graphics/Player/Normal/Idle/DownRight")))),
            "Down Right": tuple(pygame_image_load(f"graphics/Player/Normal/Idle/DownRight/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Idle/Downright")))),
                },
    
        "Run": {
            "Left": tuple(pygame_transform_flip(surface = pygame_image_load( f"graphics/Player/Normal/Run/Body/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os_list_dir("graphics/Player/Normal/Run/Body/Right")))),
            "Right": tuple(pygame_image_load(f"graphics/Player/Normal/Run/Body/Right/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Run/Body/Right")))),
            "Up": tuple(pygame_image_load(f"graphics/Player/Normal/Run/Body/Up/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Run/Body/Up")))),
            "Down": tuple(pygame_image_load(f"graphics/Player/Normal/Run/Body/Down/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Run/Body/Down")))),
               }
                                         }
                               }

        self.head_dict = {"Normal": {
            "Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Player/Normal/Run/Head/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os_list_dir("graphics/Player/Normal/Run/Head/Right")))),
            "Right": tuple(pygame_image_load(f"graphics/Player/Normal/Run/Head/Right/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Run/Head/Right")))),   
            "Up": tuple(pygame_image_load(f"graphics/Player/Normal/Run/Head/Up/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Run/Head/Up")))),
            "Up Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Player/Normal/Run/Head/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os_list_dir("graphics/Player/Normal/Run/Head/UpRight")))),
            "Up Right": tuple(pygame_image_load(f"graphics/Player/Normal/Run/Head/UpRight/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Run/Head/UpRight")))),
            "Down": tuple(pygame_image_load(f"graphics/Player/Normal/Run/Head/Down/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Run/Head/Down")))),
            "Down Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Player/Normal/Run/Head/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os_list_dir("graphics/Player/Normal/Run/Head/DownRight")))),
            "Down Right": tuple(pygame_image_load(f"graphics/Player/Normal/Run/Head/DownRight/{i}.png").convert_alpha() for i in range(len(os_list_dir("graphics/Player/Normal/Run/Head/DownRight")))),   
                                    }
                        }

        # Create attributes used for the animations
        self.animation_index = 0 # Tracks which animation frame to show
        self.animation_frame_counter = 0 # Used to track how much time has passed since the last frame update
        
        # Dictionary to hold the time between each animation frame for each animation 
        # Values are in ms
        self.animation_frame_cooldowns_dict = {"Idle": 100,
                                            "Run": 100}

    def change_players_animation_state(self):

        # Changes the player's animation state if the conditions are met

        # If the player is allowed to start performing actions (i.e. not during the camera panning when a boss is spawned)
        if self.player_gameplay_info_dict["CanStartOperating"] == True:

            # If the player is moving left, right, up or down
            if pygame_key_get_pressed()[pygame_K_a] or pygame_key_get_pressed()[pygame_K_d] or pygame_key_get_pressed()[pygame_K_w] or pygame_key_get_pressed()[pygame_K_s]:

                """ 
                Play the idle animation:
                    - If the player is at the beginning or end of the tile map
                    or 
                    - If the player is colliding with a neighbouring tile in the direction that the player is going in
                    - If there are two directions the player is going and there is a collision on both directions
                    - If the player isn't pressing any of the movement input keys (The elif statement)
                """
                # If this dictionary does not already exist
                if hasattr(self, "direction_collisions") == False:
                    # Create a dictionary that holds the collisions in the direction that the player is facing
                    self.direction_collisions = {
                                                "Left": pygame_Rect(self.rect.x - 3, self.rect.y, self.rect.width, self.rect.height),
                                                "Right": pygame_Rect(self.rect.x + 3, self.rect.y, self.rect.width, self.rect.height),
                                                "Up": pygame_Rect(self.rect.x, self.rect.y - 3, self.rect.width, self.rect.height),
                                                "Down": pygame_Rect(self.rect.x, self.rect.y + 3, self.rect.width, self.rect.height)
                                                }
                # If this dictionary already exists
                else:
                    # Update the dictionary's rect values
                    self.direction_collisions["Left"]  = pygame_Rect(self.rect.x - 3, self.rect.y, self.rect.width, self.rect.height)
                    self.direction_collisions["Right"] = pygame_Rect(self.rect.x + 3, self.rect.y, self.rect.width, self.rect.height)
                    self.direction_collisions["Up"] = pygame_Rect(self.rect.x, self.rect.y - 3, self.rect.width, self.rect.height)
                    self.direction_collisions["Down"]  = pygame_Rect(self.rect.x, self.rect.y + 3, self.rect.width, self.rect.height)

                # Create a tuple of the directions the player is currently moving in
                current_directions = [key for key in self.direction_variables_dict.keys() if self.direction_variables_dict[key] == True]
    
                if (self.rect.x == 0 or self.rect.right == self.last_tile_position[0]) or \
                    len(current_directions) == 1 and self.direction_collisions[current_directions[0]] != None and self.direction_collisions[current_directions[0]].collidedict(self.neighbouring_tiles_dict) != None or \
                    len(current_directions) == 2 and (self.direction_collisions[current_directions[0]] != None and self.direction_collisions[current_directions[1]] != None) and \
                    (self.direction_collisions[current_directions[0]].collidedict(self.neighbouring_tiles_dict) != None and self.direction_collisions[current_directions[1]].collidedict(self.neighbouring_tiles_dict) != None):

                    # If the current animation state has not been set to "Idle" yet
                    if self.current_animation_state != "Idle":
                        # Set the current animation state to "Idle"
                        self.current_animation_state = "Idle"

                        # Reset the animation frame counter and index
                        self.animation_frame_counter = 0
                        self.animation_index = 0

                # If the player isn't colliding with a neighbouring tile or is not at the beginning or end of the tile map
                else:
                    # If the current animation state has not been set to "Run" yet
                    if self.current_animation_state != "Run":
                        # Set the current animation state to "Run"
                        self.current_animation_state = "Run"

                        # Reset the animation frame counter and index
                        self.animation_frame_counter = 0
                        self.animation_index = 0

            # If the player has stopped running left or right
            elif pygame_key_get_pressed()[pygame_K_a] == False and pygame_key_get_pressed()[pygame_K_d] == False and pygame_key_get_pressed()[pygame_K_w] == False and pygame_key_get_pressed()[pygame_K_s] == False:

                # If the current animation state has not been set to "Idle" yet
                if self.current_animation_state != "Idle":
                    # Set the current animation state to "Idle"
                    self.current_animation_state = "Idle"

                # If the animation index is not 0
                if self.animation_index != 0:
                    # Reset the animation frame counter and index
                    self.animation_frame_counter = 0
                    self.animation_index = 0

    def play_animations(self):

        # Plays the animations of the player

        # Check whether we need to change the player's animation state based on what the player is doing
        self.change_players_animation_state()

        # Increment the animation frame counter based on time
        self.animation_frame_counter += 1000 * self.delta_time

        # Update the damage flash effect timer (if it has been set to the damage flash effect timer)
        self.update_damage_flash_effect_timer()

        # --------------------------------------
        # Identifying the direction that the player is looking toward.
        """ 
        Note: This is used to:
            - Assign which idle animation should be playing if the player is shooting depending on where the player is shooting
            - Assign the correct head onto the torso depending on where the player is looking
        
        Note 2: 360 / 8 (8 directions), = 45, offset everything by half of that so that each direction has a cone like radius 
        """
        segment_offset = 45 / 2

        match self.look_angle:
            # Right
            case _ if (0 <= degrees(self.look_angle) < segment_offset) or ((360 - segment_offset) <= degrees(self.look_angle) < 360):
                self.current_look_direction = "Right"
            # UpRight
            case _ if (segment_offset <= degrees(self.look_angle) < segment_offset + 45):
                self.current_look_direction = "Up Right"
            # Up
            case _ if (90 - segment_offset) <= degrees(self.look_angle) < (90 + segment_offset):
                self.current_look_direction = "Up"
            # UpLeft
            case _ if (90 + segment_offset) <= degrees(self.look_angle) < (90 + segment_offset + 45):
                self.current_look_direction = "Up Left"
            # Left
            case _ if (180 - segment_offset) <= degrees(self.look_angle) < (180 + segment_offset):
                self.current_look_direction = "Left"
            # DownLeft
            case _ if (180 + segment_offset) <= degrees(self.look_angle) < (180 + segment_offset + 45):
                self.current_look_direction = "Down Left"
            # Down
            case _ if (270 - segment_offset) <= degrees(self.look_angle) < (270 + segment_offset):
                self.current_look_direction = "Down" 
            # DownRight
            case _ if (270 + segment_offset) <= degrees(self.look_angle) < (270 + segment_offset + 45):
                self.current_look_direction = "Down Right"

        # --------------------------------------
        # Assigning animation list and image

        """ Temporary variables to store the: 
            - Current player animation state's list, e.g. The list containing the images of the "Idle" animation
            - The current animation image
            """
        
        # If the player's current animation state is not "Death" (i.e. the player is alive)
        if self.current_animation_state != "Death":
            # Idle animation state
            if self.current_animation_state == "Idle":
                # If there is only one direction the player is going in (i.e. Left, Right, Up or Down)
                if len(self.player_direction) == 1:
                    current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]]

                    # Note: There is a bug with animations when running into building tiles (not quite sure on the reason for the bug)
                    try:
                        # If the follow command results in a "tuple index "out of range" error
                        current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]][self.animation_index]

                    # Reset the animation index and assign the image again
                    except:
                        self.animation_index = 0
                        current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]][self.animation_index]

                
                # If there are two directions the player is going in (i.e Up Left, Up Right, Down Left, Down Right)
                elif len(self.player_direction) > 1:
                    # Concatenate the strings (e.g. Up Right
                    two_direction = self.player_direction[0] + " " + self.player_direction[1]
                    current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][two_direction]
                    current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][two_direction][self.animation_index]

            # Run animation state
            if self.current_animation_state == "Run":
                """ 
                Note: Only the first player direction is checked, therefore if the playing was moving Up and Right, the player direction would be ["Right", "Up"], as the x direction is checked before the y direction.
                - If the player is running Right, the body will face Right as long as the player looks between Up, Up Right, Right and Down Right, Down. Otherwise, the body will face in the direction the player is pointing towards.
                (The same applies for all directions i.e. Up, Down, Left and Right)
                """
                # Moving up or down
                if self.player_direction[0] == "Up" or self.player_direction[0] == "Down":

                    # If the player is looking towards any direction in front of where they are moving
                    # E.g. Moving down and looking Left, DownLeft, Down, DownRight, Right
                    if (self.player_direction[0] == "Down" and 180 <= degrees(self.look_angle) < 360) or (self.player_direction[0] == "Up" and 0 <= degrees(self.look_angle) < 180):
                        # Set the body (torso) to point towards where the player is moving
                        current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]]
                        current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]][self.animation_index]

                    # If the player is looking towards the opposite direction of where the player is moving towards
                    else:
                        if 0 <= degrees(self.look_angle) < 180 :
                            body_direction = "Up"
                        elif 180 <= degrees(self.look_angle) < 360:
                            body_direction = "Down"
                        
                        # Set the body (torso) to point towards where the player is looking towards (with the mouse)
                        current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][body_direction]
                        current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][body_direction][self.animation_index]

                # Moving left or right
                if self.player_direction[0] == "Left" or self.player_direction[0] == "Right":
                    # If the player is looking towards any direction in front of where they are moving
                    # E.g. Moving Left and looking Up, UpLeft, Left, DownLeft, Down
                    if self.player_direction[0] == "Right" and (0 <= degrees(self.look_angle) < 90 or 270 <= degrees(self.look_angle) < 360) or \
                        self.player_direction[0] == "Left" and (90 <= degrees(self.look_angle) < 270):

                        # Set the body (torso) to point towards where the player is moving
                        current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]]
                        current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]][self.animation_index]
                    
                    # If the player is looking towards the opposite direction of where the player is moving towards
                    else:
                        # If the player is looking left
                        if self.player_direction[0] == "Left":
                            if degrees(self.look_angle) <= 90 :
                                body_direction = "Up"
                            elif degrees(self.look_angle) >= 270:
                                body_direction = "Down"
                        
                        # If the player is looking right
                        elif self.player_direction[0] == "Right":
                            if 180 <= degrees(self.look_angle) <= 270:
                                body_direction = "Down"
                            elif 90 <= degrees(self.look_angle) < 180:
                                body_direction = "Up"

                        # Set the body (torso) to point towards where the player is looking towards (with the mouse)
                        current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][body_direction]
                        current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][body_direction][self.animation_index]

            # ---------------------------------------------------------------------------------
            # Set the image to be this animation frame

            # If the player has been damaged
            if self.player_gameplay_info_dict["DamagedFlashEffectTimer"] != None:
                # Set the current animation image to be a flashed version of the current animation image (a white flash effect)
                current_animation_image = change_image_colour(current_animation_image = current_animation_image, desired_colour = random_choice(((255, 255, 255), (40, 40, 40))))

            # If the player is in frenzy mode
            elif self.player_gameplay_info_dict["FrenzyModeTimer"] != None:
                # Colour the player as the current frenzy mode colour
                current_animation_image = change_image_colour(current_animation_image = current_animation_image, desired_colour = self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"])

            # If the invincibility timer has been set off (The player was knocked back)
            # Note: If statement so that it will also play over the frenzy mode colour
            if self.player_gameplay_info_dict["InvincibilityTimer"] != None:
                # Colour the player as the current invincibility mode colour
                current_animation_image = change_image_colour(current_animation_image = current_animation_image, desired_colour = self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectColour"])
        
        # If the player's current animation is "Death" (i.e. the player is not alive)
        elif self.current_animation_state == "Death":
            # Set the current animation list to be "Death"
            current_player_state_animation_list = self.animations_dict["Death"] 
            # Set the current animation image based on the animation index
            current_animation_image = current_player_state_animation_list[self.animation_index]

        # Set the image to be this animation frame
        self.image = current_animation_image

        # ---------------------------------------------------------------------------------
        # Changing the animation frame

        # Update the animation frames based on the current animation state
        match self.current_animation_state:

            case "Idle":
                # If enough time has passed since the last frame was played or since the animation was reset
                if self.animation_frame_counter >= self.animation_frame_cooldowns_dict["Idle"]:

                    # If the animation index isn't at the end of the list 
                    if self.animation_index < (len(current_player_state_animation_list) - 1):
                        # Increment the animation index
                        self.animation_index += 1

                    # If the animation index is at the end of the list
                    else:
                        # Reset the animation index
                        self.animation_index = 0
                
                    # Reset the animation frame counter
                    self.animation_frame_counter = 0

            case "Run":
                # If enough time has passed since the last frame was played or since the animation was reset
                if self.animation_frame_counter >= self.animation_frame_cooldowns_dict["Run"]:

                    # If the animation index isn't at the end of the list 
                    if self.animation_index < (len(current_player_state_animation_list) - 1):
                        # Increment the animation index
                        self.animation_index += 1

                    # If the animation index is at the end of the list
                    else:
                        # Reset the animation index
                        self.animation_index = 0
                
                    # Reset the animation frame counter
                    self.animation_frame_counter = 0

            case "Death":

                """ Only play the animation once"""

                # If enough time has passed since the last frame was played or since the animation was reset
                if self.animation_frame_counter >= self.animation_frame_cooldowns_dict["Death"]:

                    # If the animation index isn't at the end of the list 
                    if self.animation_index < (len(current_player_state_animation_list) - 1):
                        # Increment the animation index
                        self.animation_index += 1

                        # Reset the animation frame counter
                        self.animation_frame_counter = 0
        # ---------------------------------------------------------------------------------
        # Draw the player onto the main screen

        """
        - The camera position must be subtracted so that the image is drawn within the limits of the screen.
        - Half of the image width and height is subtracted so that the rotation of the player image is centered within the player rect.
        """
        # pygame_draw_rect(self.surface, "purple", (self.rect.x - self.camera_position[0], self.rect.y - self.camera_position[1], self.rect.width, self.rect.height), 0)
        
        # If the current animation state is "Run"
        if self.current_animation_state == "Run":

            # ---------------------------------------------------------------------------------
            # Assigning the head image

            # Set the head image to be the default version of the head image
            head_image = self.head_dict[self.current_player_element][self.current_look_direction][self.animation_index]

            # If the damage flash effect timer is counting down (i.e. the player has been damaged)
            if self.player_gameplay_info_dict["DamagedFlashEffectTimer"] != None:
                # Set the head image to be the flashed version of the head image (a white flash effect)
                head_image = change_image_colour(current_animation_image = head_image, desired_colour = (255, 255, 255))
            
            # If the player is in frenzy mode
            elif self.player_gameplay_info_dict["FrenzyModeTimer"] != None:
                # Colour the player as the current frenzy mode colour
                head_image = change_image_colour(current_animation_image = head_image, desired_colour = self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"])

            # If the invincibility timer has been set off (The player was knocked back)
            # Note: If statement so that it will also play over the frenzy mode colour
            if self.player_gameplay_info_dict["InvincibilityTimer"] != None:
                # Colour the player as the current invincibility mode colour
                head_image = change_image_colour(current_animation_image = head_image, desired_colour = self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectColour"])

            # ---------------------------------------------------------------------------------
            # Drawing the torso and the head

            # Temporary variable for the position that the torso should be drawn at
            torso_position = ((self.rect.centerx - self.camera_position[0]) - int(self.image.get_width() / 2), (self.rect.midbottom[1] - self.image.get_height() - self.camera_position[1]))

            # Draw the torso at the bottom of the player rect
            self.draw(surface = self.surface, x = torso_position[0], y = torso_position[1])

            # Adjusting the head image depending on the direction the player is looking towards
            # Note: This is because for some directions, the head may be placed too high or too low
            match self.current_look_direction:
                # Up
                case _ if self.current_look_direction == "Up Left" or self.current_look_direction == "Up" or self.current_look_direction == "Up Right":
                    head_adjustment_y = 2
                # Down
                case _ if self.current_look_direction == "Down Left" or self.current_look_direction == "Down" or self.current_look_direction == "Down Right":
                    head_adjustment_y = 3
                # Left or right
                case _ if self.current_look_direction == "Left" or self.current_look_direction == "Right":
                    head_adjustment_y = 0
            
            # Draw the head on top the torso
            self.surface.blit(head_image, ((self.rect.centerx - self.camera_position[0]) - int(head_image.get_width()/ 2), head_adjustment_y + torso_position[1] - head_image.get_height()))

        # If the current animation state is "Idle" and the player is pressing the left mouse button
        elif self.current_animation_state == "Idle":

            # If the player is pressing the left mouse button
            if pygame_mouse_get_pressed()[0] == True or self.player_gameplay_info_dict["CanStartOperating"] == False:
                """ There is an error where the animation index is not reset when switching to this "shooting idle" animation. 
                Therefore, if the animation index + 1 is greater than the number of frames in the current animation list, the animation index should be reset.

                - The second check is so that the player can move their character around whilst the camera is panning.
                """
                if (self.animation_index + 1) > len(self.animations_dict[self.current_player_element]["Idle"][self.current_look_direction]):
                    # Reset the animation index
                    self.animation_index = 0

                # ------------------------------------------------------------------------------------------------------------
                # Updating the player direction so that the player will point to that direction once the player stops shooting

                # Count the number of capital letters inside the string
                capital_letter_count = sum(map(str.isupper, self.current_look_direction))

                # If there is only 1 capital letter, then current direction is one direction e.g. Right
                if capital_letter_count == 1:
                    self.player_direction = [self.current_look_direction]

                # If there are 2 capital letters, then the current direction is two directions e.g Up Left
                elif capital_letter_count == 2:
                    # Set the player direction into a list consisting of the two directions the player is facing. E.g. ["Up", "Left"]
                    self.player_direction = self.current_look_direction.split()

            # Draw the idle animation
            self.draw(surface = self.surface, x = (self.rect.centerx - self.camera_position[0]) - int(self.image.get_width() / 2), y = (self.rect.centery - self.camera_position[1]) - int(self.image.get_height() / 2))

        # If the current animation state is "Death" (i.e. the player is not alive)
        elif self.current_animation_state == "Death":
            # Draw the death animation
            self.draw(surface = self.surface, x = (self.rect.centerx - self.camera_position[0]) - int(self.image.get_width() / 2), y = (self.rect.centery - self.camera_position[1]) - int(self.image.get_height() / 2))

    def update_damage_flash_effect_timer(self):
        
        # Updates the damage flash effect timer

        # If there has been a timer set for the damage flash effect
        if self.player_gameplay_info_dict["DamagedFlashEffectTimer"] != None:

            # If the timer has not finished counting
            if self.player_gameplay_info_dict["DamagedFlashEffectTimer"] > 0:
                # Decrease the timer
                self.player_gameplay_info_dict["DamagedFlashEffectTimer"] -= 1000 * self.delta_time
            
            # If the timer has finished counting
            if self.player_gameplay_info_dict["DamagedFlashEffectTimer"] <= 0:
                # Set the damage flash effect timer back to None
                self.player_gameplay_info_dict["DamagedFlashEffectTimer"] = None

    # ---------------------------------------------------------------------------------
    # Movement       

    def declare_movement_attributes(self):

        # Declares all the movement attributes (used to avoid "crowding" in the init method)

        """
        self.delta_time = delta_time (Used for framerate independence)

        """
        # Dictionary that holds which direction the player is currently facing 
        self.direction_variables_dict = {"Up": False, "Down": False ,"Left": False, "Right": False}

        # ---------------------------------------
        # Movement

        # Set the initial movement velocity to be 0
        self.movement_suvat_u = 0
        # The movement distance the player can move
        self.movement_suvat_s = 0

        # Calculate the velocity that the player moves at given a distance that the player travels within a given time span

        # After re-arranging s = vt + 1/2(a)(t^2), v is given by the equation: (2s - a(t)^2) / 2t, where a is 0 because acceleration is constant
        time_to_travel_distance_at_final_movement_velocity = 0.5 # t
        distance_travelled_at_final_movement_velocity = 4 * TILE_SIZE # s 
        # Full version: self.movement_suvat_v = ((2 * distance_travelled_at_final_movement_velocity) - (0 * (time_to_travel_distance_at_final_movement_velocity ** 2)) / (2 * time_to_travel_distance_at_final_movement_velocity))
        # Simplified version:
        self.movement_suvat_v = ((2 * distance_travelled_at_final_movement_velocity) / (2 * time_to_travel_distance_at_final_movement_velocity))

        # Calculate the acceleration needed for the player to reach self.movement_suvat_v within a given time span

        # After re-arranging v = u + at, a is given by the equation: (v - u) / t, where u is 0
        time_to_reach_final_movement_velocity = 0.15
        # Full version: self.movement_suvat_a = (self.movement_suvat_v - 0) / time_to_reach_final_movement_velocity
        # Simplified version:
        self.movement_suvat_a = self.movement_suvat_v / time_to_reach_final_movement_velocity

        # Deceleration
        self.decelerating = False
        
        # Calculate the deceleration required for the player to decelerate from the final movement velocity to 0 (Store as absolute value)

        # After re-arranging v = u + at, a is given by the equation: (v - u) / t, where v is 0
        self.time_taken_to_decelerate_from_final_movement_velocity = 0.10
        # Full version: self.deceleration_from_final_movement_velocity = abs((0 - self.movement_suvat_v) / time_taken_to_decelerate_from_final_movement_velocity)
        # Simplified version:
        self.deceleration_from_final_movement_velocity = self.movement_suvat_v / self.time_taken_to_decelerate_from_final_movement_velocity

        # Floating point correction:  
        # Note: Used for accuracy in movement when the distance to travel is less than 1 (small floating point values)
        self.floating_point_correction_x = 0
        self.floating_point_correction_y = 0

    def update_direction_variables(self):

        # Updates the direction variables inside the dictionary direction variables dictionary. Creates a list of the direction the player is moving towards.
        if self.player_gameplay_info_dict["CanStartOperating"] == True:

            # Left
            if pygame_key_get_pressed()[pygame_K_a] == False:
                self.direction_variables_dict["Left"] = False
            elif pygame_key_get_pressed()[pygame_K_a] == True:
                self.direction_variables_dict["Left"] = True
            
            # Right
            if pygame_key_get_pressed()[pygame_K_d] == False:
                self.direction_variables_dict["Right"] = False
            elif pygame_key_get_pressed()[pygame_K_d] == True:
                self.direction_variables_dict["Right"] = True
            # Up
            if pygame_key_get_pressed()[pygame_K_w] == False:
                self.direction_variables_dict["Up"] = False
            elif pygame_key_get_pressed()[pygame_K_w] == True:
                self.direction_variables_dict["Up"] = True
            # Down
            if pygame_key_get_pressed()[pygame_K_s] == False:
                self.direction_variables_dict["Down"] = False
            elif pygame_key_get_pressed()[pygame_K_s] == True:
                self.direction_variables_dict["Down"] = True

            # Create a list that stores the direction(s) that the player is moving towards
            self.player_direction = [key for key in self.direction_variables_dict.keys() if self.direction_variables_dict[key] == True]

    def movement_acceleration(self):

        # Executes the movement acceleration of the player

        # If the current velocity has not reached the final velocity set for the player
        if self.movement_suvat_u < self.movement_suvat_v:
            # Increase the current velocity
            self.movement_suvat_u += (self.movement_suvat_a * self.delta_time)

        # Limit the current velocity to the final velocity set for the player (in case that the current velocity is greater)
        self.movement_suvat_u = min(self.movement_suvat_u, self.movement_suvat_v)

        # Set the distance travelled based on the current velocity
        self.movement_suvat_s = ((self.movement_suvat_u * self.delta_time) + (0.5 * self.movement_suvat_a * (self.delta_time ** 2)))

    def handle_player_movement(self):

        # Handles the movement of the player

        # Only allow the player to move if they have not been knocked back
        if self.player_gameplay_info_dict["KnockbackTimer"] == None:

            # (For floating point accuracy)
            next_position_x = self.rect.x
            next_position_y = self.rect.y

            # If the "a" key is pressed
            if pygame_key_get_pressed()[pygame_K_a] and pygame_key_get_pressed()[pygame_K_d] == False:

                # If the player is decelerating currently
                if self.decelerating == True:
                    # Stop decelerating
                    self.decelerating = False

                # Update the direction variables
                self.update_direction_variables()

                # ------------------------------------
                # Adjusting distance moved based on the direction the player is moving 
                """ Notes: 
                - This is so that the player does not move faster when walking diagonally
                - abs() because the distance to travel must be the absolute value of the distance travelled 
                """

                # If the player is only moving in one direction
                if len(self.player_direction) == 1:
                    # Set the distance to travel to be the movement distance travelled
                    distance_to_travel = self.movement_suvat_s + self.floating_point_correction_x

                # If the player is moving in two directions
                elif len(self.player_direction) > 1:
                    # If the vertical direction is "Up"
                    if self.player_direction[0] == "Up":
                        # Calculate the horizontal distance to travel based on the angle
                        distance_to_travel = abs((self.movement_suvat_s * cos(radians(45))) + self.floating_point_correction_x)

                    # If the vertical direction is "Down"
                    elif self.player_direction[0] == "Down":
                        # Calculate the horizontal distance to travel based on the angle
                        distance_to_travel = abs((self.movement_suvat_s * cos(radians(315))) + self.floating_point_correction_x)

                # Handle tile collisions
                self.handle_tile_collisions(
                                            distance_to_travel = distance_to_travel,
                                            check_x = True,
                                            check_y = False
                                            )

                # If the player isn't decelerating currently
                if self.decelerating == False:

                    # ---------------------------------------------------------------------------------
                    # Acceleration

                    # Execute the movement acceleration method
                    self.movement_acceleration()

                    # ---------------------------------------------------------------------------------
                    # Moving the player

                    """ Reasons for the following check:
                    - Rounding the position could result in the player constantly being 1 pixel away from the tile)
                    - Int is so that if self.dx = 0.123925 or a number close to 0, this would still cause the same problem
                    """
                    if int(self.dx) != 0:

                        # If moving left will place the player out of the screen
                        if self.rect.left - self.movement_suvat_s <= 0:
                            # Set the player's x position to be at 0
                            self.rect.left = 0

                        # Otherwise
                        elif self.rect.left - self.movement_suvat_s > 0:
                            # Move the player left
                            next_position_x -= self.dx
                            self.rect.x = round(next_position_x)

            # If the "d" key is pressed
            elif pygame_key_get_pressed()[pygame_K_d] and pygame_key_get_pressed()[pygame_K_a] == False:

                # If the player is decelerating currently
                if self.decelerating == True:
                    # Stop decelerating
                    self.decelerating = False
                
                # Update the direction variables
                self.update_direction_variables()
                
                # ------------------------------------
                # Adjusting distance moved based on the direction the player is moving 
                """ Notes: 
                - This is so that the player does not move faster when walking diagonally
                - abs() because the distance to travel must be the absolute value of the distance travelled 
                """

                # If the player is only moving in one direction
                if len(self.player_direction) == 1:
                    # Set the distance to travel to be the movement distance travelled
                    distance_to_travel = self.movement_suvat_s + self.floating_point_correction_x

                # If the player is moving in two directions
                elif len(self.player_direction) > 1:
                    # If the vertical direction is "Up"
                    if self.player_direction[0] == "Up":
                        # Calculate the horizontal distance to travel based on the angle
                        distance_to_travel = abs((self.movement_suvat_s * cos(radians(135))) + self.floating_point_correction_x)

                    # If the vertical direction is "Down"
                    elif self.player_direction[0] == "Down":
                        # Calculate the horizontal distance to travel based on the angle
                        distance_to_travel = abs((self.movement_suvat_s * cos(radians(225))) + self.floating_point_correction_x)

                # Handle tile collisions
                self.handle_tile_collisions(
                                            distance_to_travel = distance_to_travel,
                                            check_x = True,
                                            check_y = False
                                            )

                # If the player isn't decelerating currently
                if self.decelerating == False:
                    
                    # ---------------------------------------------------------------------------------
                    # Acceleration

                    # Execute the movement acceleration method
                    self.movement_acceleration()

                    # ---------------------------------------------------------------------------------
                    # Moving the player 

                    """ Reasons for the following check:
                    - Rounding the position could result in the player constantly being 1 pixel away from the tile)
                    - Int is so that if self.dx = 0.123925 or a number close to 0, this would still cause the same problem
                    """       
                    if int(self.dx) != 0:

                        # If moving right will place the player out of the tile map / out of the screen
                        if self.rect.right + self.movement_suvat_s >= self.last_tile_position[0]:
                            # Set the player's right position to be at the last tile position in the tile map
                            self.rect.right = self.last_tile_position[0]

                        # Otherwise
                        elif self.rect.right + self.movement_suvat_s < self.last_tile_position[0]:
                            # Move the player right
                            next_position_x += self.dx
                            self.rect.x = round(next_position_x)

            # If the "w" key is pressed
            if pygame_key_get_pressed()[pygame_K_w] and pygame_key_get_pressed()[pygame_K_s] == False:

                # If the player is decelerating currently
                if self.decelerating == True:
                    # Stop decelerating
                    self.decelerating = False
                
                # Update the direction variables
                self.update_direction_variables()

                # ------------------------------------
                # Adjusting distance moved based on the direction the player is moving 
                """ Notes: 
                - This is so that the player does not move faster when walking diagonally
                - abs() because the distance to travel must be the absolute value of the distance travelled 
                """

                # If the player is only moving in one direction
                if len(self.player_direction) == 1:
                    # Set the distance to travel to be the movabs(ement distance travelled
                    distance_to_travel = self.movement_suvat_s + self.floating_point_correction_y

                # If the player is moving in two directions
                elif len(self.player_direction) > 1:
                    # If the horizontal direction is "Left"
                    if self.player_direction[1] == "Left":
                        # Calculate the vertical distance to travel based on the angle
                        distance_to_travel = abs((self.movement_suvat_s * sin(radians(135))) + self.floating_point_correction_y)

                    # If the horizontal direction is "Right"
                    elif self.player_direction[1] == "Right":
                        # Calculate the vertical distance to travel based on the angle
                        distance_to_travel = abs((self.movement_suvat_s * sin(radians(45))) + self.floating_point_correction_y)

                # Handle tile collisions
                self.handle_tile_collisions(
                                            distance_to_travel = distance_to_travel,
                                            check_x = False,
                                            check_y = True
                                            )

                # If the player isn't decelerating currently
                if self.decelerating == False:
                    
                    # ---------------------------------------------------------------------------------
                    # Acceleration

                    # Execute the movement acceleration method
                    self.movement_acceleration()

                    # ---------------------------------------------------------------------------------
                    # Moving the player

                    """ Reasons for the following check:
                    - Rounding the position could result in the player constantly being 1 pixel away from the tile)
                    - Int is so that if self.dy = 0.2348232 or a number close to 0, this would still cause the same problem
                    """
                    if int(self.dy) != 0:
                        # If moving up will place the player out of the screen
                        if self.rect.top - self.movement_suvat_s < 0:
                            # Set the player's top position to be at the top of the screen 
                            self.rect.top = 0

                        # Otherwise
                        elif self.rect.top - self.movement_suvat_s >= 0:
                            # Move the player up
                            next_position_y -= self.dy
                            self.rect.y = round(next_position_y)

            # If the "s" key is pressed
            elif pygame_key_get_pressed()[pygame_K_s] and pygame_key_get_pressed()[pygame_K_w] == False:

                # If the player is decelerating currently
                if self.decelerating == True:
                    # Stop decelerating
                    self.decelerating = False

                # Update the direction variables
                self.update_direction_variables()

                # ------------------------------------
                # Adjusting distance moved based on the direction the player is moving 
                """ Note: This is so that the player does not move faster when walking diagonally"""

                # If the player is only moving in one direction
                if len(self.player_direction) == 1:
                    # Set the distance to travel to be the movement distance travelled
                    distance_to_travel = self.movement_suvat_s + self.floating_point_correction_y

                # If the player is moving in two directions
                elif len(self.player_direction) > 1:
                    # If the horizontal direction is "Left"
                    if self.player_direction[1] == "Left":
                        # Calculate the vertical distance to travel based on the angle
                        distance_to_travel = abs(((self.movement_suvat_s) * sin(radians(225))) + self.floating_point_correction_y)

                    # If the horizontal direction is "Right"
                    elif self.player_direction[1] == "Right":
                        # Calculate the vertical distance to travel based on the angle
                        distance_to_travel = abs(((self.movement_suvat_s) * sin(radians(315))) + self.floating_point_correction_y)

                # Handle tile collisions
                self.handle_tile_collisions(
                                            distance_to_travel = distance_to_travel,
                                            check_x = False,
                                            check_y = True
                                            )

                # If the player isn't decelerating currently
                if self.decelerating == False:
                    
                    # ---------------------------------------------------------------------------------
                    # Acceleration

                    # Execute the movement acceleration method
                    self.movement_acceleration()

                    # ---------------------------------------------------------------------------------
                    # Moving the player

                    """ Reasons for the following check:
                    - Rounding the position could result in the player constantly being 1 pixel away from the tile)
                    - Int is so that if self.dy = 0.2348232 or a number close to 0, this would still cause the same problem
                    """
                    if int(self.dy) != 0:

                        # If moving down will place the player out of the tile map
                        if self.rect.bottom + self.movement_suvat_s > self.last_tile_position[1]:
                            # Set the player's bottom position to the y position of the last tile position
                            self.rect.bottom = self.last_tile_position[1] 

                        # Otherwise
                        elif self.rect.bottom + self.movement_suvat_s <= self.last_tile_position[1]:
                            # Move the player down
                            next_position_y += self.dy
                            self.rect.y = round(next_position_y)

            # ---------------------------------------------------------------------------------
            # Deceleration

            # If the player has let go of all movement input keys or if the deceleration has already started
            if (pygame_key_get_pressed()[pygame_K_a] == False and pygame_key_get_pressed()[pygame_K_d] == False and pygame_key_get_pressed()[pygame_K_w] == False and pygame_key_get_pressed()[pygame_K_s] == False and self.movement_suvat_u > 0) or self.decelerating == True:

                # (For floating point accuracy)
                # Note: This is declared here because self.rect.x or self.rect.y may have changed 
                next_position_x_2 = self.rect.x
                next_position_y_2 = self.rect.y
                    
                if self.decelerating == False:
                    # Set the decelerating player attribute to True
                    self.decelerating = True

                # If the player has stopped decelerating
                if self.movement_suvat_u <= 0:
                    # Set the decelerating player attribute back to False
                    self.decelerating = False
                    # If the current velocity of the player is less than 0
                    if self.movement_suvat_u < 0:
                        # Set the current velocity to 0
                        self.movement_suvat_u = 0

                # If the player's current velocity is greater than 0
                if self.movement_suvat_u > 0:
                    # Decelerate the player / decrease the velocity
                    self.movement_suvat_u -= (self.deceleration_from_final_movement_velocity * self.delta_time)

                # Limit the current velocity to 0
                self.movement_suvat_u = max(self.movement_suvat_u, 0)

                # Set the distance travelled based on the current velocity
                self.movement_suvat_s = ((self.movement_suvat_u * self.delta_time) + (0.5 * self.movement_suvat_a * (self.delta_time ** 2)))

                # Handle tile collisions again
                # Note: When decelerating, dx/dy will have to keep changing

                # If the player's last direction was moving towards was left or right
                if self.direction_variables_dict["Left"] == True or self.direction_variables_dict["Right"] == True:
                    # Check x collisions
                    self.handle_tile_collisions(
                                                distance_to_travel = self.movement_suvat_s + self.floating_point_correction_x, 
                                                check_x = True, 
                                                check_y = False
                                                )
                # If the player's last direction was moving towards was up or down                      
                elif self.direction_variables_dict["Up"] == True or self.direction_variables_dict["Down"] == True:
                    # Check y collisions
                    self.handle_tile_collisions(
                                                distance_to_travel = self.movement_suvat_s + self.floating_point_correction_y, 
                                                check_x = False, 
                                                check_y = True
                                                )

                # ---------------------------------------------------------------------------------
                # Decelerating in the last direction the player was moving towards

                """ Reasons for the following int(self.dx) or int(self.dy) checks:
                - Rounding the position could result in the player constantly being 1 pixel away from the tile)
                - Int is so that if self.dx = 0.123925 or a number close to 0, this would still cause the same problem
                """               
                # If the player was moving right
                if self.direction_variables_dict["Right"] == True:

                    if int(self.dx) != 0:

                        # If moving right will place the player out of the tile map / out of the screen
                        if self.rect.right + self.movement_suvat_s >= self.last_tile_position[0]:
                            # Set the player's right position to be at the last tile position in the tile map
                            self.rect.right = self.last_tile_position[0]

                        # Otherwise
                        elif self.rect.right + self.movement_suvat_s < self.last_tile_position[0]:
                            # Move the player right
                            next_position_x_2 += self.dx
                            self.rect.x = round(next_position_x_2)

                # If the player was moving left
                elif self.direction_variables_dict["Left"] == True:

                    if int(self.dx) != 0:
            
                        # If moving left will place the player out of the screen
                        if self.rect.left - self.movement_suvat_s <= 0:
                            # Set the player's x position to be at 0
                            self.rect.left = 0

                        # Otherwise
                        elif self.rect.left - self.movement_suvat_s > 0:
                            # Move the player left
                            next_position_x_2 -= self.dx
                            self.rect.x = round(next_position_x_2)

                # If the player was moving up
                elif self.direction_variables_dict["Up"] == True:

                    if int(self.dy) != 0:

                        # If moving up will place the player out of the screen
                        if self.rect.top - self.movement_suvat_s < 0:
                            # Set the player's top position to be at the top of the screen 
                            self.rect.top = 0

                        # Otherwise
                        elif self.rect.top - self.movement_suvat_s >= 0:
                            # Move the player up
                            next_position_y_2 -= self.dy
                            self.rect.y = round(next_position_y_2)
                    
                # If the player was moving down
                elif self.direction_variables_dict["Down"] == True:

                    if int(self.dy) != 0:

                        # If moving down will place the player out of the tile map
                        if self.rect.bottom + self.movement_suvat_s > self.last_tile_position[1]:
                            # Set the player's bottom position to the y position of the last tile position
                            self.rect.bottom = self.last_tile_position[1] 

                        # Otherwise
                        elif self.rect.bottom + self.movement_suvat_s <= self.last_tile_position[1]:
                            # Move the player down
                            next_position_y_2 += self.dy
                            self.rect.y = round(next_position_y_2)

    # ---------------------------------------------------------------------------------
    # Collisions      

    def handle_tile_collisions(self, distance_to_travel, check_x, check_y):
        
        # Handles collisions between tiles and the player

        # Note: A collision is only triggered when one rect is overlapping another rect by less than self.collision_tolerance.

        # If the distance to travel is greater or equal to 1
        if abs(distance_to_travel) >= 1:
            
            if check_x == True:
                # ---------------------------------------------------------------------------------
                # Horizontal collisions

                # Find the x collisions to the left and right of the player
                x_collisions_left = pygame_Rect(self.rect.x - distance_to_travel , self.rect.y, self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)
                x_collisions_right = pygame_Rect(self.rect.x + distance_to_travel , self.rect.y, self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)

                # If there is an x collision to the right of the player
                if x_collisions_right != None:

                    # If the difference between the player's right and the tile's left is less than the collision tolerance (there is a collision) and the player is trying to move right
                    if abs(self.rect.right - x_collisions_right[0].rect.left) < self.collision_tolerance and self.direction_variables_dict["Right"] == True:
                        # Set the player's right to the tile's left
                        self.rect.right = x_collisions_right[0].rect.left
                        # Don't allow the player to move
                        self.dx = 0

                    # If the difference between the player's right and the tile's left is less than the collision tolerance (there is a collision) and the player is trying to move in any direction but right
                    elif abs(self.rect.right - x_collisions_right[0].rect.left) < self.collision_tolerance and self.direction_variables_dict["Right"] != True:
                        # Allow the player to move
                        self.dx = distance_to_travel
                        # Reset floating point correction x
                        self.floating_point_correction_x = 0

                # If there is an x collision to the left of the player
                if x_collisions_left != None:

                    # If the difference between the player's left and the tile's right is less than the collision tolerance (there is a collision) and the player is trying to move left
                    if abs(self.rect.left - x_collisions_left[0].rect.right) < self.collision_tolerance and self.direction_variables_dict["Left"] == True:
                        # Set the player's left to the tile's right
                        self.rect.left = x_collisions_left[0].rect.right
                        # Don't allow the player to move
                        self.dx = 0
                    
                    # If the difference between the player's left and the tile's right is less than the collision tolerance (there is a collision) and the player is trying to move in any direction but left
                    elif abs(self.rect.left - x_collisions_left[0].rect.right) < self.collision_tolerance and self.direction_variables_dict["Left"] != True:
                        # Allow the player to move
                        self.dx = distance_to_travel
                        # Reset floating point correction x
                        self.floating_point_correction_x = 0

                # If there is no x collision to the left of the player and there is no x collision to the right of the player
                elif x_collisions_left == None and x_collisions_right == None:
                    # Allow the player to move
                    self.dx = distance_to_travel
                    # Reset floating point correction x
                    self.floating_point_correction_x = 0

            # ---------------------------------------------------------------------------------
            # Vertical collisions      

            if check_y == True:

                # Find the collisions above and below the player
                y_collisions_up = pygame_Rect(self.rect.x, self.rect.y - distance_to_travel, self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)     
                y_collisions_down = pygame_Rect(self.rect.x, self.rect.y + distance_to_travel, self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)     

                # If there is an y collision above the player
                if y_collisions_up != None:

                    # If the difference between the player's top and the tile's bottom is less than the collision tolerance (there is a collision) and the player is trying to move up
                    if abs(self.rect.top - y_collisions_up[0].rect.bottom) < self.collision_tolerance and self.direction_variables_dict["Up"] == True:
                        # Set the player's top to the tile's bottom
                        self.rect.top = y_collisions_up[0].rect.bottom
                        # Don't allow the player to move
                        self.dy = 0

                    # If the difference between the player's top and the tile's bottom is less than the collision tolerance (there is a collision) and the player is trying to move in any direction but up
                    elif abs(self.rect.top - y_collisions_up[0].rect.bottom) < self.collision_tolerance and self.direction_variables_dict["Up"] != True:
                        # Allow the player to move
                        self.dy = distance_to_travel
                        # Reset floating point correction y
                        self.floating_point_correction_y = 0

                # If there is an y collision below the player
                if y_collisions_down != None:

                    # If the difference between the player's bottom and the tile's top is less than the collision tolerance (there is a collision) and the player is trying to move down
                    if abs(self.rect.bottom - y_collisions_down[0].rect.top) < self.collision_tolerance and self.direction_variables_dict["Down"] == True:
                        # Set the player's bottom to the tile's top
                        self.rect.bottom = y_collisions_down[0].rect.top
                        # Don't allow the player to move
                        self.dy = 0

                    # If the difference between the player's bottom and the tile's top is less than the collision tolerance (there is a collision) and the player is trying to move in any direction but down
                    elif abs(self.rect.bottom - y_collisions_down[0].rect.top) < self.collision_tolerance and self.direction_variables_dict["Down"] != True:
                        # Allow the player to move
                        self.dy = distance_to_travel
                        # Reset floating point correction y
                        self.floating_point_correction_y = 0

                # If there is no y collision above the player and there is no y collision below the player
                elif y_collisions_up == None and y_collisions_down == None:
                    # Allow the player to move
                    self.dy = distance_to_travel
                    # Reset floating point correction y
                    self.floating_point_correction_y = 0

        # If the distance to travel is less than 1
        elif abs(distance_to_travel) < 1:
            
            # If this was the horizontal distance to travel
            if check_x == True:
                # Add the distance to travel to the floating point correction x
                self.floating_point_correction_x += distance_to_travel
                # Set dx as 0 (i.e. don't let the player move)
                self.dx = 0
            
            # If this was the vertical distance to travel
            elif check_y == True:
                # Add the distance to travel to the floating point correction y
                self.floating_point_correction_y += distance_to_travel
                # Set dy as 0 (i.e. don't let the player move)
                self.dy = 0

    # ---------------------------------------------------------------------------------
    # Mouse

    def find_mouse_position_and_angle(self):

        # Finds the mouse position according to the position inside the tile map. Finds the angle between the center of the player and the mouse.

        # Retrieve the mouse position
        """
        - The scale multiplier refers to how much the surface that everything will be drawn onto has been scaled by 
        """
        mouse_position = pygame_mouse_get_pos()  
        scale_multiplier = (screen_width / self.surface.get_width(), screen_height / self.surface.get_height())
        self.mouse_position = ((mouse_position[0] / scale_multiplier[0]) + self.camera_position[0] , (mouse_position[1] / scale_multiplier[1]) + self.camera_position[1])
        self.mouse_rect = pygame_Rect(self.mouse_position[0], self.mouse_position[1], 1, 1)

        # Find the distance between the mouse and the center of the player in their horizontal and vertical components
        dx, dy = self.mouse_position[0] - self.rect.centerx, self.mouse_position[1] - self.rect.centery
        
        # Find the angle between the mouse and the center of the player
        """
        - Modulo is so that the value of angle will always be in between 0 and 2pi.
        - If the angle is negative, it will be added to 2pi.
        - "-dy" because the y axis is flipped in PYgame
        """
        self.look_angle = atan2(-dy, dx) % (2 * pi)
    # ---------------------------------------------------------------------------------
    # Gameplay

    def switch_tool(self, tool):

        # Switches between tools
        
        # If the current tool is not the tool the player wants to switch to
        if self.player_gameplay_info_dict["CurrentToolEquipped"] != tool:
            # Switch to the tool
            self.player_gameplay_info_dict["CurrentToolEquipped"] = tool
    
    def draw_player_tool(self):

        # Draws the weapon onto main surface
        
        # If the player is pressing the left mouse button
        if pygame_mouse_get_pressed()[0]:
            
            # ---------------------------------------------------------------------------------------------------
            # Assigning tool image

            # If the current tool is the "BuildingTool"
            if self.player_gameplay_info_dict["CurrentToolEquipped"] == "BuildingTool":
                # Set the tool image as the building tool
                tool_image = self.tools[self.player_gameplay_info_dict["CurrentToolEquipped"]]["Images"]["Up"]

            # If the current tool is anything but the "BuildingTool":
            elif self.player_gameplay_info_dict["CurrentToolEquipped"] != "BuildingTool":

                # Assign the weapon image
                tool_image = self.tools[self.player_gameplay_info_dict["CurrentToolEquipped"]]["Images"][self.current_look_direction]
            
            # ---------------------------------------------------
            # Checking for if we need to change the image colour if there is a visual effect that must be played

            # If the player has been damaged
            if self.player_gameplay_info_dict["DamagedFlashEffectTimer"] != None:
                # Set the tool to be a flashed version of the current animation image (a white flash effect)
                tool_image = change_image_colour(current_animation_image = tool_image, desired_colour = (255, 255, 255))

            # If the player is in frenzy mode
            elif self.player_gameplay_info_dict["FrenzyModeTimer"] != None:
                # Colour the weapon as the current frenzy mode colour
                tool_image = change_image_colour(current_animation_image = tool_image, desired_colour = self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"])

            # ---------------------------------------------------------------------------------------------------
            # Assigning the weapon position
            
            # The following distance will ensure that the weapon is always "hypot_distance" away from the center of the player
            hypot_distance = 10
            distance_x = hypot_distance * cos(self.look_angle)
            distance_y = hypot_distance * sin(self.look_angle)
            
            # Depending on the current look direction, 
            match self.current_look_direction:
                
                # (For up and down, the weapon is centered more with a "-5")
                case _ if self.current_look_direction == "Up" or self.current_look_direction == "Down":
                    self.weapon_position = (
                        ((self.rect.centerx - 5)) + distance_x, 
                        ((self.rect.centery - (tool_image.get_height() / 2))) - distance_y
                    )
                # All other directions
                case _:
                    self.weapon_position = (
                        ((self.rect.centerx - (tool_image.get_width() / 2))) + distance_x, 
                        ((self.rect.centery - (tool_image.get_height() / 2))) - distance_y
                    )

            # ---------------------------------------------------------------------------------------------------
            # Draw the weapon at the position

            # pygame_draw_circle(self.scaled_surface, "white", (self.rect.centerx - self.camera_position[0], self.rect.centery - self.camera_position[1]), hypot_distance, 1)
            self.surface.blit(tool_image, (self.weapon_position[0] - self.camera_position[0], self.weapon_position[1] - self.camera_position[1]))

    def activate_frenzy_mode(self):
        
        # Activates frenzy mode if the player presses the correct input key and the frenzy mode meter is completely filed up
        
        # If the frenzy mode meter / bar is completely filled up
        if (self.player_gameplay_info_dict["CurrentFrenzyModeValue"] == self.player_gameplay_info_dict["MaximumFrenzyModeValue"]):
            
            # If the player presses the "space" key
            if pygame_key_get_pressed()[pygame_K_SPACE]:

                # Set the frenzy mode fire rate boost to 2
                self.player_gameplay_info_dict["FrenzyModeFireRateBoost"] = 2

                # Set the frenzy mode timer to start
                self.player_gameplay_info_dict["FrenzyModeTimer"] = self.player_gameplay_info_dict["FrenzyModeTime"]
                
    def update_frenzy_mode_timer(self):
    
        # Updates the frenzy mode timer

        # If a frenzy mode timer has been set to start counting down 
        if self.player_gameplay_info_dict["FrenzyModeTimer"] != None:
            
            # --------------------------------------
            # Updating timers

            # If the timer is greater than 0 
            if self.player_gameplay_info_dict["FrenzyModeTimer"] > 0:

                # Decrease the frenzy mode timer
                self.player_gameplay_info_dict["FrenzyModeTimer"] -= 1000 * self.delta_time

                # Decrease the current frenzy mode value (The player cannot increase their frenzy mode value whilst frenzy mode is activated)
                # Limit the lowest the current frenzy mode value can be to 0
                self.player_gameplay_info_dict["CurrentFrenzyModeValue"] = max(self.player_gameplay_info_dict["CurrentFrenzyModeValue"] + (self.player_gameplay_info_dict["FrenzyModeValueGradient"] * self.delta_time), 0)

            # If the timer is less than or equal to 0
            if self.player_gameplay_info_dict["FrenzyModeTimer"] <= 0:

                # Set the frenzy mode timer back to None
                self.player_gameplay_info_dict["FrenzyModeTimer"] = None

                # Reset the frenzy mode fire rate boost back to 1
                self.player_gameplay_info_dict["FrenzyModeFireRateBoost"] = 1

    def update_frenzy_mode_colour(self):
        
        # Updates the frenzy mode colour

        # Change the colour of the player and update the current sin angle
        self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"], self.player_gameplay_info_dict["FrenzyModeVisualEffectCurrentSinAngle"] = sin_change_object_colour(
                                                                                                                                
                                                                                                                                # The current sin angle
                                                                                                                                current_sin_angle = self.player_gameplay_info_dict["FrenzyModeVisualEffectCurrentSinAngle"],

                                                                                                                                # The rate of change in the sin angle over time
                                                                                                                                angle_time_gradient = self.player_gameplay_info_dict["FrenzyModeVisualEffectAngleTimeGradient"], 

                                                                                                                                # Set the colour that will be changed (the return value)
                                                                                                                                colour_to_change = self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"],

                                                                                                                                # Set the original colour as either the min or max colour 
                                                                                                                                # Note:  The order does not matter because the colour will always start at the midpoint RGB value
                                                                                                                                original_colour = self.player_gameplay_info_dict["FrenzyModeVisualEffectMinMaxColours"][0],

                                                                                                                                # The minimum and maximum colours
                                                                                                                                min_max_colours = self.player_gameplay_info_dict["FrenzyModeVisualEffectMinMaxColours"],

                                                                                                                                # A list containing values indicating whether we should subtract or add for each RGB value at a given angle, e.g. (-1, 0, 1)
                                                                                                                                plus_or_minus_list = self.player_gameplay_info_dict["FrenzyModeVisualEffectRGBValuesPlusOrMinus"],

                                                                                                                                # Delta time to increase the angle over time
                                                                                                                                delta_time = self.delta_time
                                                                                                                                                                            )
    
    def perform_knockback(self):

        # Performs the knockback if the player collides with the current boss
        
        # If the knockback timer has been set to start counting down
        if self.player_gameplay_info_dict["KnockbackTimer"] != None:


            """Notes:
            - To avoid re-writing the collision checking system again: 
                - First check the x collisions with the horizontal distance that the player should move
                - Then check the y collisions with the vertical distance that the player should move
            """
            
            # Temp variables to hold the center of the player
            new_position_center_x = self.rect.centerx 
            new_position_center_y = self.rect.centery

            # ---------------------------------------------------------------------------------------------------------------------------------
            # Updating the direction variables for collision checking 

            # If the horizontal distance time gradient is less than 0
            if self.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] < 0: 
                # Check for collisions to the left of the player
                self.direction_variables_dict["Left"] = True
            # If the horizontal distance time gradient is greater than 0
            elif self.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] > 0:
                # Check for collisions to the right of the player
                self.direction_variables_dict["Right"] = True

            # If the vertical distance time gradient is less than 0
            if self.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] > 0:
                # Check for collisions above the player
                self.direction_variables_dict["Up"] = True
            # If the vertical distance time gradient is greater than 0
            elif self.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] < 0:
                # Check for collisions below the player
                self.direction_variables_dict["Down"] = True

            # ---------------------------------------------------------------------------------------------------------------------------------
            # Horizontal collision checking and movement

            # Handle tile collisions with the x distance to travel
            self.handle_tile_collisions(
                                        distance_to_travel = self.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] * self.delta_time + self.floating_point_correction_x, 
                                        check_x = True, 
                                        check_y = False
                                        )

            # If int(self.dx) is not 0
            if int(self.dx) != 0:
                
                # If the movement distance is less than 0
                if (self.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] * self.delta_time) < 0:

                    # If knocking the player to the left will place the player out of the tile map / out of the screen
                    if self.rect.left - (self.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] * self.delta_time) <= 0:
                        # Set the player's x position to be at 0
                        self.rect.left = 0

                    # Otherwise
                    elif self.rect.left - (self.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] * self.delta_time) > 0:
                        # Move the player left
                        new_position_center_x += self.dx
                        self.rect.centerx = round(new_position_center_x)

                # If the movement distance is greater than 0
                elif (self.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] * self.delta_time) > 0:

                    # If knocking the player to the right will place the player out of the tile map / out of the screen
                    if self.rect.right + (self.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] * self.delta_time) >= self.last_tile_position[0]:
                        # Set the player's right position to be at the last tile position in the tile map
                        self.rect.right = self.last_tile_position[0]

                    # Otherwise
                    elif self.rect.right + (self.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] * self.delta_time) < self.last_tile_position[0]:
                        # Move the player right
                        new_position_center_x += self.dx
                        self.rect.centerx = round(new_position_center_x)

            # ---------------------------------------------------------------------------------------------------------------------------------
            # Vertical collision checking and movement

            # Handle tile collisions with the y distance to travel
            self.handle_tile_collisions(
                                        distance_to_travel = self.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] * self.delta_time + self.floating_point_correction_y, 
                                        check_x = False, 
                                        check_y = True
                                        )

            # If (self.dy) is not 0
            if int(self.dy) != 0:

                # If the movement distance is greater than 0
                if (self.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] * self.delta_time) > 0:

                    # If moving up will place the player out of the screen
                    if self.rect.top - (self.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] * self.delta_time) < 0:
                        # Set the player's top position to be at the top of the screen 
                        self.rect.top = 0

                    # Otherwise
                    elif self.rect.top - (self.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] * self.delta_time) >= 0:
                        # Move the player up
                        new_position_center_y -= self.dy
                        self.rect.centery = round(new_position_center_y)
                
                # If the movement distance is less than 0
                if (self.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] * self.delta_time) < 0:

                    # If moving down will place the player out of the tile map
                    if self.rect.bottom + (self.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] * self.delta_time) > self.last_tile_position[1]:
                        # Set the player's bottom position to the y position of the last tile position
                        self.rect.bottom = self.last_tile_position[1] 

                    # Otherwise
                    elif self.rect.bottom + (self.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] * self.delta_time) <= self.last_tile_position[1]:
                        # Move the player down
                        new_position_center_y -= self.dy
                        self.rect.centery = round(new_position_center_y)

            # ---------------------------------------------------------------------------------------------------------------------------------
            # Updating the knockback timer

            # If the knockback timer has not finished counting down
            if self.player_gameplay_info_dict["KnockbackTimer"] > 0:
                # Decrease the timer
                self.player_gameplay_info_dict["KnockbackTimer"] -= 1000 * self.delta_time

            # If the knockback timer has finished counting down
            if self.player_gameplay_info_dict["KnockbackTimer"] <= 0:
                # Reset the knockback timer back to None
                self.player_gameplay_info_dict["KnockbackTimer"] = None

    def update_invincibility_timer_and_colour(self):
        
        # Updates the invincibility timer after the player is knocked back by the current boss

        # If a frenzy mode timer has been set to start counting down 
        if self.player_gameplay_info_dict["InvincibilityTimer"] != None:
            
            # --------------------------------------
            # Updating timers and colour

            # If the timer is greater than 0 
            if self.player_gameplay_info_dict["InvincibilityTimer"] > 0:
                # Decrease the invincibility timer
                self.player_gameplay_info_dict["InvincibilityTimer"] -= 1000 * self.delta_time

                # Calculate the new angle time gradient
                self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectAngleTimeGradient"] = (self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectAngleChange"] - 0) / (self.player_gameplay_info_dict["InvincibilityTimer"] / 1000)

                # Increase the current sin angle
                self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectCurrentSinAngle"] += self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectAngleTimeGradient"] * self.delta_time
                
                # For each RGB Value
                for i in range(0, len(self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectColourAdjusterIndex"])):
                    # If the value isn't "0"
                    if self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectColourAdjusterIndex"][i] != 0:
                        # Limit the values to be between 0 and 255
                        self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectColour"][i] = max(0, 
                                                                            min(
                                                                            self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectOriginalColour"][i] + (125 * sin(self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectCurrentSinAngle"])), 
                                                                            255
                                                                                )
                                                                                                            )

            # If the timer is less than or equal to 0
            if self.player_gameplay_info_dict["InvincibilityTimer"] <= 0:
                # Set the blinking invincibility timer back to None
                self.player_gameplay_info_dict["InvincibilityTimer"] = None

                # Reset the blinking invincibility visual effect colour
                self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectColour"] = [
                                                                                            self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectOriginalColour"][0], 
                                                                                            self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectOriginalColour"][1], 
                                                                                            self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectOriginalColour"][2]
                                                                                            ]

                # Reset the invincibility visual effect current sin angle
                self.player_gameplay_info_dict["BlinkingInvincibilityVisualEffectCurrentSinAngle"] = 0 

                # Note: The gradient will be "reset" the next time the player becomes invincible

    # ---------------------------------------
    # Building 

    def update_removal_cooldown_timer(self):

        # Updates the removal cooldown timer

        # If there is a timer that has been set to start counting
        if self.tools["BuildingTool"]["RemovalCooldownTimer"] != None:
            
            # If the timer is less than the removal cooldown of building tiles
            if self.tools["BuildingTool"]["RemovalCooldownTimer"] < self.tools["BuildingTool"]["RemovalCooldown"]:
                # Increase the timer
                self.tools["BuildingTool"]["RemovalCooldownTimer"] += 1000 * self.delta_time
        
            # If the timer is greater than or equal to the removal cooldown of building tiles
            if self.tools["BuildingTool"]["RemovalCooldownTimer"] >= self.tools["BuildingTool"]["RemovalCooldown"]:
                # Set the last tile removed timer back to None
                self.tools["BuildingTool"]["RemovalCooldownTimer"] = None
        
    def handle_building(self):
        
        # If the player currently has the building tool equipped
        if self.player_gameplay_info_dict["CurrentToolEquipped"] == "BuildingTool":
            
            # --------------------------------------
            # Update the removal cooldown timer
            self.update_removal_cooldown_timer()

            # --------------------------------------
            # Highlighting any tiles that are hovered over

            # Look for collisions between the player's mouse and any placed building tile
            # Note: Used for removing building tiles and highlighting tiles
            collision_result_index = self.mouse_rect.collidelist(self.tools["BuildingTool"]["ExistingBuildingTilesList"])

            # If the player is hovering over an existing building tile
            if collision_result_index != -1:
                
                # Find any building tiles that are being hovered over
                building_tile_to_highlight = self.tools["BuildingTool"]["ExistingBuildingTilesList"][collision_result_index]

                # If the distance between this tile and the player is within the maximum removing distance
                if dist(self.rect.center, building_tile_to_highlight.rect.center) <= self.tools["BuildingTool"]["MaximumPlacingAndRemovingDistance"]:
                    # Set the highlight colour as orange
                    highlight_colour = "orange"
                
                # If the distance between this tile and the player is not within the maximum removing distance
                elif dist(self.rect.center, building_tile_to_highlight.rect.center) > self.tools["BuildingTool"]["MaximumPlacingAndRemovingDistance"]:
                    # Set the highlight colour as red
                    highlight_colour = "red"

                # Highlight the building tile
                pygame_draw_rect(
                                surface = self.surface,
                                color = highlight_colour,
                                rect = pygame_Rect(
                                                    building_tile_to_highlight.rect.x - self.camera_position[0],
                                                    building_tile_to_highlight.rect.y  - self.camera_position[1],
                                                    building_tile_to_highlight.rect.width,
                                                    building_tile_to_highlight.rect.height
                                                  ),
                                width = 2
                                )

            # --------------------------------------
            # Checking for input to remove building tiles

            # If there are existing building tiles
            if len(self.tools["BuildingTool"]["ExistingBuildingTilesList"]) > 0:

                # If the player pressed the right mouse button and there is an existing building tile
                if pygame_mouse_get_pressed()[2]:
                    
                    # If enough time has passed since the player last removed a building tile
                    if self.tools["BuildingTool"]["RemovalCooldownTimer"] == None:

                        # Return the building tile at this collision index 
                        """ Note: If there is no collision, index -1 will be returned, which is perfect because then we should remove the last building tile placed down """
                        building_tile_to_remove = self.tools["BuildingTool"]["ExistingBuildingTilesList"][collision_result_index]

                        # If the distance between this tile and the player is within the maximum removing distance
                        if dist(self.rect.center, building_tile_to_remove.rect.center) <= self.tools["BuildingTool"]["MaximumPlacingAndRemovingDistance"]:

                            # Remove the building tile from the world tiles group
                            self.sprite_groups["WorldTiles"].remove(building_tile_to_remove)

                            # "Create" an empty tile where the building tile was
                            self.empty_tiles_dict[self.sprite_groups["ReplacedEmptyTiles"][building_tile_to_remove]] = 0
                            
                            # Remove the building tile from the replaced empty tiles dict
                            self.sprite_groups["ReplacedEmptyTiles"].pop(building_tile_to_remove)

                            # Remove the building tile from the world tiles list
                            self.world_tiles_dict.pop(building_tile_to_remove)

                            # Remove the building tile at the collision result index from the existing building tiles list
                            self.tools["BuildingTool"]["ExistingBuildingTilesList"].pop(collision_result_index)

                            # Start the last tile removed timer, so that the player has to wait "self.tools["BuildingTool"]["RemovalCooldown"]" before removing another tile
                            self.tools["BuildingTool"]["RemovalCooldownTimer"] = 0

                            # If the building tile to remove is in the neighbouring tiles dictionary (keys)
                            if building_tile_to_remove in self.neighbouring_tiles_dict.keys():
                                # Remove the building tile
                                self.neighbouring_tiles_dict.pop(building_tile_to_remove)
            
                # If the player pressed the "r" key and there are existing building tiles placed down
                if pygame_key_get_pressed()[pygame_K_r]:
                
                    # For each building tile inside the existing building tiles list
                    for list_index, building_tile_to_remove in enumerate(self.tools["BuildingTool"]["ExistingBuildingTilesList"]):

                        # If the distance between this tile and the player is within the maximum removing distance
                        if dist(self.rect.center, building_tile_to_remove.rect.center) <= self.tools["BuildingTool"]["MaximumPlacingAndRemovingDistance"]:

                            # Remove the building tile from the world tiles group
                            self.sprite_groups["WorldTiles"].remove(building_tile_to_remove)

                            # Remove the building tile from the world tiles list
                            self.world_tiles_dict.pop(building_tile_to_remove)

                            # "Create" an empty tile where the building tile was
                            self.empty_tiles_dict[self.sprite_groups["ReplacedEmptyTiles"][building_tile_to_remove]] = 0

                            # Remove the building tile from the replaced empty tiles dict
                            self.sprite_groups["ReplacedEmptyTiles"].pop(building_tile_to_remove)

                            # Remove the building tile at the list index
                            self.tools["BuildingTool"]["ExistingBuildingTilesList"].pop(list_index)

                            # Start the last tile removed timer, so that the player has to wait "self.tools["BuildingTool"]["RemovalCooldown"]" before removing tiles again
                            self.tools["BuildingTool"]["RemovalCooldownTimer"] = 0

                            # If the building tile to remove is in the neighbouring tiles dictionary (keys)
                            if building_tile_to_remove in self.neighbouring_tiles_dict.keys():
                                # Remove the building tile
                                self.neighbouring_tiles_dict.pop(building_tile_to_remove)


            # --------------------------------------
            # Checking for placement of building tiles

            # Draw a guide circles to show the minimum and maximum distances the player can place building tiles (MAY REMOVE)
            pygame_draw_circle(self.surface, "red", (self.rect.centerx - self.camera_position[0], self.rect.centery - self.camera_position[1]), self.tools["BuildingTool"]["MinimumPlacingDistance"], 1)
            pygame_draw_circle(self.surface, "red", (self.rect.centerx - self.camera_position[0], self.rect.centery - self.camera_position[1]), self.tools["BuildingTool"]["MaximumPlacingAndRemovingDistance"], 2)

            # Find collisions between the mouse rect and empty tiles inside the tile map
            empty_tile_collision = pygame_Rect(self.mouse_position[0], self.mouse_position[1] , 1, 1).collidedict(self.empty_tiles_dict)

            # If there is a collision between the mouse rect and an empty tile 
            if empty_tile_collision != None:

                # The tile rect will be the key of the returned value from the collide dict
                empty_tile = empty_tile_collision[0]
                
                # The center of the empty tile
                empty_tile_center = (
                                    empty_tile.rect.x + (empty_tile.rect.width / 2),
                                    empty_tile.rect.y + (empty_tile.rect.height / 2)
                                    )   

                # If the distance between the center of the player and the center of the empty tile at the mouse position less than the maximum distance
                if self.tools["BuildingTool"]["MinimumPlacingDistance"] < dist(self.rect.center, empty_tile_center) < self.tools["BuildingTool"]["MaximumPlacingAndRemovingDistance"]:
                    # Highlight the empty tile as green
                    pygame_draw_rect(
                                    surface = self.surface,
                                    color = "green", 
                                    rect = pygame_Rect(
                                                        empty_tile.rect.x - self.camera_position[0], 
                                                        empty_tile.rect.y - self.camera_position[1],
                                                        empty_tile.rect.width,
                                                        empty_tile.rect.height),
                                    width = 2                
                                    )   

                    # If the left mouse button is pressed and there are less than 3 existing building tiles
                    if pygame_mouse_get_pressed()[0] == True and len(self.tools["BuildingTool"]["ExistingBuildingTilesList"]) < self.tools["BuildingTool"]["MaximumNumberOfTilesAtOneTime"]:
                        
                        # If the player has enough bamboo resource to place down another building tile
                        if self.player_gameplay_info_dict["AmountOfBambooResource"] - self.tools["BuildingTool"]["BambooResourceDepletionAmount"] > 0:

                            """Conditions:
                            - If there is no current boss
                            - There is no boss but the player restarted the session
                            - There is a current boss and the player's mouse is not colliding with the rect of the boss
                            """
                            # If there is no current boss or there is a current boss and the player's mouse is not colliding with the rect of the boss or
                            # Note: This is so that the player can't build tiles right on top of the boss (Drains resource very quickly)
                            if hasattr(self, "boss_rect") == False or \
                                self.boss_rect == None or \
                                    (hasattr(self, "boss_rect") == True and self.mouse_rect.colliderect(self.boss_rect) == False):

                                # Create a building tile
                                building_tile = BuildingTile(x = empty_tile.rect.x, y = empty_tile.rect.y, image = self.tools["BuildingTool"]["Images"]["TileImage"])

                                # Add the building tile to the building tiles sprite group
                                self.sprite_groups["WorldTiles"].add(building_tile)

                                # Add the building tile to the world tiles dictionary with the key as the building tile and the value as the type of world tile
                                self.world_tiles_dict[building_tile] = "BuildingTile"

                                # Save the empty tile in the replaced empty tiles dict so that we do not need to create a new empty tile every time a building tile is placed / removed
                                self.sprite_groups["ReplacedEmptyTiles"][building_tile] = empty_tile

                                # Remove the empty tile from the empty tiles dictionary
                                self.empty_tiles_dict.pop(empty_tile)
                                
                                # Add the building tile to the existing building tiles list
                                self.tools["BuildingTool"]["ExistingBuildingTilesList"].append(building_tile)

                                # If a boss has been spawned and the boss rect is not set to None
                                # Note: Second check is so that when the current boss dies, the boss rect can be set to None, until the next boss is spawned
                                if hasattr(self, "boss_rect") == True and self.boss_rect != None:
                                    # Remove bamboo resource by the depletion amount set
                                    self.player_gameplay_info_dict["AmountOfBambooResource"] -= self.tools["BuildingTool"]["BambooResourceDepletionAmount"]

                # If the distance between the center of the player and the center of the empty tile at the mouse position:
                # - Less than or equal to the minimum distance
                # - Greater than or equal to the maximum distance
                elif dist(self.rect.center, empty_tile_center) <= self.tools["BuildingTool"]["MinimumPlacingDistance"] or \
                     dist(self.rect.center, empty_tile_center) >= self.tools["BuildingTool"]["MaximumPlacingAndRemovingDistance"]:

                    # Highlight the empty tile as red
                    pygame_draw_rect(
                                    surface = self.surface,
                                    color = "red", 
                                    rect = pygame_Rect(
                                                        empty_tile.rect.x - self.camera_position[0], 
                                                        empty_tile.rect.y - self.camera_position[1],
                                                        empty_tile.rect.width,
                                                        empty_tile.rect.height),
                                    width = 2                
                                    )   
    
    # ---------------------------------------
    # Shooting

    def handle_shooting(self):

        # Handles the functionality behind shooting for the player

        # --------------------------------------------------------------------------------------
        # Handling shooting input

        # pygame_draw_circle(self.scaled_surface, "white", (self.rect.centerx - self.camera_position[0], self.rect.centery - self.camera_position[1]), 50, 1)

        # If the current tool equipped by the player is not the building tool
        if self.player_gameplay_info_dict["CurrentToolEquipped"] != "BuildingTool":       

            # The dict of the current weapon selected (as a temp variable)
            current_weapon_dict = self.tools[self.player_gameplay_info_dict["CurrentToolEquipped"]]

            # --------------------------------------
            # Updating shooting cooldown timers
            self.update_shooting_cooldown_timer(current_weapon_dict = current_weapon_dict)

            # If the left mouse button has been pressed and the player has enough resources to shoot
            if pygame_mouse_get_pressed()[0] == True and \
                ((self.player_gameplay_info_dict["AmountOfBambooResource"] - current_weapon_dict["BambooResourceDepletionAmount"]) >= 0 or self.player_gameplay_info_dict["FrenzyModeTimer"] != None):

                    # If enough time has passed since the last time the player shot
                    if current_weapon_dict["ShootingCooldownTimer"] == None:

                        # --------------------------------------------------------------------------------------------------------------------
                        # Spawning the projectile 
                        
                        # Distance to place the projectile at the tip of the gun 
                        hypot_distance = 45
                        distance_x = hypot_distance * cos(self.look_angle)
                        distance_y = -(hypot_distance * sin(self.look_angle))

                        # -----------------------------------------------------
                        # Checking that there are no tiles in between the center of the player and where the bamboo projectile will be spawned
                        # Note: The following checks is so that the player cannot shoot projectiles through walls

                        # Assume that there is no tile in between the center of the player and where the bamboo projectile will be spawned
                        no_tile_in_between = True
                        
                        # For every neighbouring tile
                        for neighbouring_tile in self.neighbouring_tiles_dict.keys():
                            # Check if the tile is in between the center of the player and the spawning positions of the bamboo projectile
                            if len(neighbouring_tile.rect.clipline(self.rect.center, (self.rect.centerx + distance_x, self.rect.centery + distance_y))) != 0:
                                # If there is a collision then set "no_tile_in_between" to False and exit the loop
                                no_tile_in_between = False
                                break
                        
                        # If there is nothing in between the center of the player and where the bamboo projectile will be spawned
                        if no_tile_in_between == True:

                            # ----------------------------------------
                            # Angled polygons effect

                            # Distance away from the player for the shooting angled polygons
                            angled_polygon_effect_hypot_distance = 32
                            angled_polygon_effect_distance_x = angled_polygon_effect_hypot_distance * cos(self.look_angle)
                            angled_polygon_effect_distance_y = -(angled_polygon_effect_hypot_distance * sin(self.look_angle))


                            # Save the spawning point so that angled polygons can be greated at the tip of the gun
                            # Note: A copy is made of this tuple
                            self.player_gameplay_info_dict["AngledPolygonsShootingSpawningPosition"] = (self.rect.centerx + angled_polygon_effect_distance_x, self.rect.centery + angled_polygon_effect_distance_y)
                            # Save the angle so that the polygons travel towards the correct direction
                            self.player_gameplay_info_dict["AngledPolygonsShootingAngle"] = self.look_angle

                            # ----------------------------------------
                            # Create a bamboo projectile, spawning it at the tip of the gun (Starts at the center of the player but has an added distance which displaces it to right in front of the gun)
                            # Note: The center of the bamboo projectile is placed at the co-ordinates

                            is_bamboo_launcher_projectile = True if self.player_gameplay_info_dict["CurrentToolEquipped"] == "BambooLauncher" else False

                            # If frenzy mode is not activated when shooting:
                            if self.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                                
                                # Set the "is_frenzy_mode_projectile" attribute to False
                                bamboo_projectile = BambooProjectile(
                                                                    x = self.rect.centerx + distance_x,
                                                                    y = self.rect.centery + distance_y,
                                                                    angle = self.look_angle,
                                                                    damage_amount = current_weapon_dict["WeaponDamage"],
                                                                    is_frenzy_mode_projectile = False,
                                                                    is_bamboo_launcher_projectile = is_bamboo_launcher_projectile
                                                                    )
                            
                            # If frenzy mode is activated when shooting:
                            elif self.player_gameplay_info_dict["FrenzyModeTimer"] != None:
                                # Set the "is_frenzy_mode_projectile" attribute to True
                                bamboo_projectile = BambooProjectile(
                                                                    x = self.rect.centerx + distance_x,
                                                                    y = self.rect.centery + distance_y,
                                                                    angle = self.look_angle,
                                                                    damage_amount = current_weapon_dict["WeaponDamage"],
                                                                    is_frenzy_mode_projectile = True,
                                                                    is_bamboo_launcher_projectile = is_bamboo_launcher_projectile
                                                                    )
                                
                        
                            # Add the bamboo projectile to the bamboo projectiles group
                            self.sprite_groups["BambooProjectiles"].add(bamboo_projectile)

                            # Set the shooting cooldown timer to the shooting cooldown set
                            current_weapon_dict["ShootingCooldownTimer"] = current_weapon_dict["ShootingCooldown"]

                            # If the player isn't in frenzy mode
                            if self.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                                # If a boss has been spawned and the boss rect is not set to None
                                # Note: Second check is so that when the current boss dies, the boss rect can be set to None, until the next boss is spawned
                                if hasattr(self, "boss_rect") == True and self.boss_rect != None:
                                    # Remove the amount of bamboo resource set for the weapon 
                                    self.player_gameplay_info_dict["AmountOfBambooResource"] -= current_weapon_dict["BambooResourceDepletionAmount"]

    def create_bamboo_projectiles_explosion(self, projectile):

        # Additional functionality for the bamboo launcher when the launcher's projectile collides with a boss

        # Create x mini projectiles
        for i in range(0, self.tools["BambooLauncher"]["NumberOfMiniProjectiles"]):
            
            # Offset so that when spawned in an awkward position (e.g. inside a world tile, some projectiles will still not be removed)
            offset_distance_x = 15 * cos(radians(i * (360 / self.tools["BambooLauncher"]["NumberOfMiniProjectiles"])))
            offset_distance_y = -(15 * sin(radians(i * (360 / self.tools["BambooLauncher"]["NumberOfMiniProjectiles"])))) # "-" because pygame's y-axis is flipped
            
            # Create a new projectile with the damage of the mini projectiles damage under the bamboo launcher's dictionary
            bamboo_projectile = BambooProjectile(
                                                x = projectile.rect.centerx + offset_distance_x,
                                                y = projectile.rect.centery + offset_distance_y,
                                                angle = radians(i * (360 / self.tools["BambooLauncher"]["NumberOfMiniProjectiles"])),
                                                damage_amount = self.tools["BambooLauncher"]["MiniProjectilesDamage"],
                                                is_frenzy_mode_projectile = projectile.is_frenzy_mode_projectile,
                                                is_bamboo_launcher_projectile = False # Make this a normal bamboo projectile
                                                )
            # Add the bamboo projectile to the bamboo projectiles group
            self.sprite_groups["BambooProjectiles"].add(bamboo_projectile)

    def update_bamboo_projectiles(self):

        # Updates bamboo projectiles (moves them, changes colour, etc.)

        if len(self.sprite_groups["BambooProjectiles"]) > 0:
            # For all bamboo projectiles
            for bamboo_projectile in self.sprite_groups["BambooProjectiles"]:
                
                # If the bamboo projectile was created whilst frenzy mode was activated
                if bamboo_projectile.is_frenzy_mode_projectile == True:

                    # If the player has activated frenzy mode
                    if self.player_gameplay_info_dict["FrenzyModeTimer"] != None:

                        # Note: The copy of the original image is so that we don't continuously add onto the current RGB values of the projectile's image (otherwise it will become completely white)

                        # Set the bamboo projectile image to be the same colour as the player when in frenzy mode
                        bamboo_projectile.image = change_image_colour(current_animation_image = bamboo_projectile.original_image.copy(), desired_colour = self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"])

                    # If the player has not activated frenzy mode
                    elif self.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                        
                        # Note: This check is so that once the frenzy mode is over, all images need to be reset back to the original image

                        # If the bamboo projectile's image is not the original image
                        if bamboo_projectile.image != bamboo_projectile.original_image:
                            # Set the image back to the original image
                            bamboo_projectile.image = bamboo_projectile.original_image


                # Update the bamboo projectile's delta time
                bamboo_projectile.delta_time = self.delta_time

                # Move the projectile
                bamboo_projectile.move_projectile()
    
    def update_shooting_cooldown_timer(self, current_weapon_dict):

        # Updates the shooting cooldown timer of the current weapon

        # If there is a timer that has been set to start counting
        if current_weapon_dict["ShootingCooldownTimer"] != None:
            # If the timer is greater than 0 (counts down from the shooting cooldown)
            if current_weapon_dict["ShootingCooldownTimer"] > 0:
                # Increase the timer
                current_weapon_dict["ShootingCooldownTimer"] -= 1000 * self.delta_time * self.player_gameplay_info_dict["FrenzyModeFireRateBoost"]

            # If the timer is less than or equal to 0 (counts down from the shooting cooldown)
            if current_weapon_dict["ShootingCooldownTimer"] <= 0:
                # Set the shooting cooldown timer back to None
                current_weapon_dict["ShootingCooldownTimer"] = None

    def run(self, delta_time):

        # Update the delta time
        self.delta_time = delta_time

        # Find the mouse position and angle
        self.find_mouse_position_and_angle()

        # Play animations
        self.play_animations()

        # If the player is not alive
        if self.player_gameplay_info_dict["CurrentHealth"] <= 0:

            # If the animation state has not been set to "Death" yet
            if self.current_animation_state != "Death":
                # Set the current animation state to "Death"
                self.current_animation_state = "Death"

                # Reset the animation index
                self.animation_index = 0
            
                # If the death animations have not been loaded before
                if "Death" not in self.animations_dict.keys():
                    # Load the death animation images
                    self.animations_dict["Death"] = tuple(pygame_image_load(f'graphics/Misc/DeathAnimation/{i}.png').convert_alpha() for i in range(0, len(os_list_dir('graphics/Misc/DeathAnimation'))))

                    # Set the frame cooldown (time between each frame)
                    self.animation_frame_cooldowns_dict["Death"] = FULL_DEATH_ANIMATION_DURATION / len(self.animations_dict["Death"])

        # If the player is alive
        if self.player_gameplay_info_dict["CurrentHealth"] > 0:

            # If the player is allowed to start performing actions (i.e. not during the camera panning when a boss is spawned)
            if self.player_gameplay_info_dict["CanStartOperating"] == False:
                # If the current animation is not set to "Idle", set it to "Idle"
                if self.current_animation_state != "Idle":
                    self.current_animation_state = "Idle"

                # If there are any bamboo projectiles, keep updating them
                self.update_bamboo_projectiles()

            # If the player is allowed to start performing actions (i.e. not during the camera panning when a boss is spawned)
            elif self.player_gameplay_info_dict["CanStartOperating"] == True:

                # # TEMPORARY
                # for tile in self.neighbouring_tiles_dict.keys():
                #     pygame_draw_rect(self.surface, "green", (tile.rect.x - self.camera_position[0], tile.rect.y - self.camera_position[1], tile.rect.width, tile.rect.height))

                # Track player movement
                self.handle_player_movement()
                
                # Create / update a mask for pixel - perfect collisions
                self.mask = pygame_mask_from_surface(self.image)

                # ----------------------------------
                # Gameplay

                # Activate frenzy mode if the conditions are met
                self.activate_frenzy_mode()

                # Update the frenzy mode timer
                self.update_frenzy_mode_timer()

                # Update the frenzy mode colour's RGB values
                self.update_frenzy_mode_colour()

                # Draw the player tool
                self.draw_player_tool()

                # Handle player building
                self.handle_building() 

                # Handle player shooting
                self.handle_shooting()

                # Update any bamboo projectiles that have been created
                self.update_bamboo_projectiles()
                
                # Perform knockback if the player gets knocked back
                self.perform_knockback()

                # Update the invincibility timer and colour
                self.update_invincibility_timer_and_colour()