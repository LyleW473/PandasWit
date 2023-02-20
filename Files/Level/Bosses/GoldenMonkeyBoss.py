from Global.generic import Generic
from Global.settings import TILE_SIZE, FULL_DEATH_ANIMATION_DURATION
from Global.functions import change_image_colour, change_image_colour_v2, sin_change_object_colour, update_generic_timer, simple_loop_animation, simple_play_animation_once
from random import choice as random_choice
from pygame.mask import from_surface as pygame_mask_from_surface
from pygame.image import load as load_image
from pygame.transform import scale as scale_image
from os import listdir as os_listdir
from Level.Bosses.AI import AI
from Level.Bosses.BossAttacks.chilli_attacks import ChilliProjectileController
from Level.Bosses.BossAttacks.dive_bomb_attack import DiveBombAttackController
from math import sin, cos, radians
from pygame.font import Font as pygame_font_Font
from Level.effect_text import EffectText
from pygame import Surface as pygame_Surface
from pygame.draw import circle as pygame_draw_circle
from pygame.draw import ellipse as pygame_draw_ellipse


class GoldenMonkeyBoss(Generic, AI):

    # ImagesDict = ?? (This is set when the boss is instantiated)
    # Example: Chase : [Direction][Image list]

    # Find the boss map boundaries, so that for the divebomb mechanic, they aren't spawned inside of a tile
    # boss_map_boundaries = {"Top": (0, 32), "Left": (32, 0), "Right": len(self.tile_map[0]) * TILE_SIZE, "Bottom": len(self.tile_map) * TILE_SIZE}
    
    # Characteristics
    knockback_damage = 20
    maximum_health = 20000
    maximum_energy_amount = 100
    

    # SUVAT variables
    suvat_dict = { 
                # The default distance travelled
                "DefaultDistanceTravelled": 3 * TILE_SIZE,

                # Time to travel the horizontal/vertical distance at the final veloctiy
                "DefaultHorizontalTimeToTravelDistanceAtFinalVelocity": 0.52,
                "DefaultVerticalTimeToTravelDistanceAtFinalVelocity": 0.52,

                # Time to reach / accelerate to the final horizontal/vertical velocity
                "DefaultHorizontalTimeToReachFinalVelocity": 0.15,
                "DefaultVerticalTimeToReachFinalVelocity": 0.15,

                # The distance the AI has to be away from the player to stop chasing them
                "DistanceThreshold": 5 

                }

    def __init__(self, x, y, surface, scale_multiplier):

        # Surface that the boss is drawn onto
        self.surface = surface 
        
        # The starting image when spawned (Used as the starting image and ending image for the boss at the start of the game and when the player dies)
        self.starting_image = GoldenMonkeyBoss.ImagesDict["Sleep"][0]

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x , y = y, image = self.starting_image)

        # Spawn the boss at the middle of the tile, with the bottom of the boss being at the bottom of the tile
        # Note: Do this before inheriting the AI class so that the rect positions are the same
        self.rect.midbottom = (x, y)

        # Inherit from the AI class
        AI.__init__(self, max_health = GoldenMonkeyBoss.maximum_health, knockback_damage = GoldenMonkeyBoss.knockback_damage, suvat_dict = GoldenMonkeyBoss.suvat_dict)

        """ List of "hidden" added attributes
        self.delta_time
        self.camera_position
        self.players_position
        self.neighbouring_tiles_dict
        self.camera_shake_events_list # A list of the camera shake events used to add the "Stomp" camera shake effect
        """

        # The current action that the boss is performing
        self.current_action = "Chase"
        
        # The amount of energy that the boss starts with
        self.energy_amount = GoldenMonkeyBoss.maximum_energy_amount

        # The current phase the golden monkey is in
        self.current_phase = 1

        # To delay actions right after spawning, set the cooldown timer to a desired amount of time and add it to this list, so that the cooldown timers can be updated
        self.previous_actions_dict = {
                                    "SpiralAttack": None,
                                    "DiveBomb": None
                                    }

        # A dictionary containing information relating to the behaviour of the Sika deer boss
        self.behaviour_patterns_dict = {

                                    "Chase": { 
                                            "FullAnimationDuration": 600,

                                            "ChilliThrowingCooldown": 260,
                                            "ChilliThrowingCooldownTimer": None
                                              },
                                    
                                    "SpiralAttack": {
                                                    "EnergyDepletionAmount": 35,
                                                    "Duration": 6000,
                                                    "DurationTimer": None,
                                                    "SpiralChilliSpawningCooldown": 60, # Cooldown between each chilli spawned in the spiral attack (50 chillis)
                                                    "SpiralChilliSpawningCooldownTimer": None, 

                                                    "Cooldown": 10000,
                                                    "CooldownTimer": 10000, # Start the cooldown timer at 10 seconds after being spawned

                                                    # Animation
                                                    "FullAnimationDuration": 150,
                                                    
                                                    # Moving the boss around a point in a circle
                                                    "SpiralAttackSpinPivotPoint": None,
                                                    "SpiralAttackSpinPivotDistance": 15,
                                                    "SpiralAttackSpinAngle": 0, # The angle the boss will be compared to its pivot point
                                                    "SpiralAttackSpinAngleTimeGradient": 360 / 1.2,
                                                    "SpiralAttackSpinNewAngle": 0,
                                                    "SpiralAttackSpinNewCenterPositions": None
                                                    },

                                    "Sleep": {
                                        "Duration": 5500,
                                        "DurationTimer": None,
                                        "FullAnimationDuration": 1200,
                                        "PlayerDamageMultiplierWhenBossIsSleeping": 1.75
                                            },

                                    "DiveBomb":{
                                                "SecondPhaseDiveBombCounter": 0,
                                                "CurrentDiveBombStage": None,
                                                "Cooldown": 7500,
                                                "CooldownTimer": 6000, # This will be set after the attack has completed (Change this number if you want to delay when the boss can first divebomb attack)
                                                "EnergyDepletionAmount": 25,
                                                "CameraShakePerformed": False, # This is used so that 

                                                "Launch": {
                                                            "Duration": 450, 
                                                            "DurationTimer": None,
                                                            "LaunchDistance": 40
                                                            # JumpTimeGradient (this is set when the boss is launching up)

                                                            # "FullAnimationDuration"

                                                            },
                                                "Target": {
                                                        "Duration": 2100, #3000,
                                                        "DurationTimer": None
                                                        },

                                                "Land": {
                                                        "Duration": 600, # 700
                                                        "DurationTimer": None,


                                                        "ShockwaveCircleAlphaLevel": 0,
                                                        "ShockwaveCircleAlphaLevelTimeGradient": 255 - 0 / (600 / 1000)

                                                        },
                                            },

                                    "Death": {
                                            "Images": None

                                            }
                                    
                                        }
        
        # -------------------------------------------------
        # Chilli projectiles and spiral attack 

        # Controller to create chilli projectiles and chilli projectile attacks
        self.chilli_projectile_controller = ChilliProjectileController()

        # If the chilli projectile controller does not have this attribute
        if hasattr(ChilliProjectileController, "spiral_attack_angle_time_gradient") == False:
            # Set the time it takes for the attack to do one full rotation to be the half the duration of the attack
            ChilliProjectileController.spiral_attack_angle_time_gradient = 360 /( (self.behaviour_patterns_dict["SpiralAttack"]["Duration"] / 1000) / 3)

        # -------------------------------------------------
        # Divebomb attack
           
        self.dive_bomb_attack_controller = DiveBombAttackController(
            x = self.rect.x, 
            y = self.rect.y, 
            damage_amount = self.extra_information_dict["KnockbackDamage"] * 1.5,
            knockback_multiplier = 1.5
            )


        # ----------------------------------------------------------------------------------
        # Declare the animation attributes
        self.declare_animation_attributes()

        # ----------------------------------------------------------------------------------
        # Sleep text

        """ Notes: 
        - The game UI is responsible for drawing the text and updating it 
        - The rest of the info e.g. gradients are inside the GameUI's effect text info dict
        """
        self.sleep_effect_text_info_dict = {
                                    "Font": pygame_font_Font("graphics/Fonts/frenzy_mode_value_font.ttf", 30),
                                    "Text": "Z",
                                    "DisplayTime": 850,
                                    "DefaultAlphaLevel": 185,
                                    "Colour": "white",
                                    "CreationCooldownTime": 300,
                                    "CreationCooldownTimer": None
                                    }
        
        # Font size for creating alpha surfaces
        self.sleep_effect_text_info_dict["FontSize"] =  pygame_font_Font("graphics/Fonts/frenzy_mode_value_font.ttf", 30).size("Z") 

        # If EffectText does not have an effect text list yet
        # Note: This is because effect text is also created in the game UI
        if hasattr(EffectText, "effect_text_list") == False:
            EffectText.effect_text_list = []

        # ----------------------------------------------------------------------------------
        # Phase 2 colour

        self.second_phase_colour_min_max_colours = ((0, 60, 0), (0, 0, 0))
        self.second_phase_colour_current_colour = self.second_phase_colour_min_max_colours[1]
        self.second_phase_colour_current_sin_angle = 0
        self.second_phase_colour_angle_time_gradient = (360 - 0) / 0.6
        self.second_phase_colour_plus_or_minus = (0, 1, 0)

    # ----------------------------------------------------------------------------------
    # Animations

    def update_second_phase_colour(self):

        # Change the colour of the player and update the current sin angle
        self.second_phase_colour_current_colour, self.second_phase_colour_current_sin_angle = sin_change_object_colour(      
                                                                                                                        # The current sin angle
                                                                                                                        current_sin_angle = self.second_phase_colour_current_sin_angle,

                                                                                                                        # The rate of change in the sin angle over time
                                                                                                                        angle_time_gradient = self.second_phase_colour_angle_time_gradient, 

                                                                                                                        # Set the colour that will be changed (the return value)
                                                                                                                        colour_to_change = self.second_phase_colour_current_colour,

                                                                                                                        # Set the original colour as either the min or max colour 
                                                                                                                        # Note:  The order does not matter because the colour will always start at the midpoint RGB value
                                                                                                                        original_colour = self.second_phase_colour_min_max_colours[0],

                                                                                                                        # The minimum and maximum colours
                                                                                                                        min_max_colours = self.second_phase_colour_min_max_colours,

                                                                                                                        # A list containing values indicating whether we should subtract or add for each RGB value at a given angle, e.g. (-1, 0, 1)
                                                                                                                        plus_or_minus_list = self.second_phase_colour_plus_or_minus,

                                                                                                                        # Delta time to increase the angle over time
                                                                                                                        delta_time = self.delta_time
                                                                                                                        )

    def declare_animation_attributes(self):

        # Declares the animation attributes

        # Set the animation index as 0
        self.animation_index = 0         

        # --------------------------
        # Chasing

        # The time between each frame should be how long each chase animation cycle should last, divided by the total number of animation frames
        # Note: All chase animations have the same number of frames regardless of the direction
        self.behaviour_patterns_dict["Chase"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Chase"]["FullAnimationDuration"] / (len(GoldenMonkeyBoss.ImagesDict["Chase"]["Down"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Chase"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Chase"]["TimeBetweenAnimFrames"]

        # --------------------------
        # Spiral attack

        # Note: All directions have the same number of animation frames

        # The time between each frame should be how long each target animation cycle should last, divided by the total number of animation frames
        self.behaviour_patterns_dict["SpiralAttack"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["SpiralAttack"]["FullAnimationDuration"] / (len(GoldenMonkeyBoss.ImagesDict))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["SpiralAttack"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["SpiralAttack"]["TimeBetweenAnimFrames"]

        # --------------------------
        # Sleep

        # The time between each frame should be how long the "Sleep" animation lasts, divided by the total number of animation frames
        self.behaviour_patterns_dict["Sleep"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Sleep"]["FullAnimationDuration"] / (len(GoldenMonkeyBoss.ImagesDict["Sleep"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Sleep"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Sleep"]["TimeBetweenAnimFrames"]

        # --------------------------
        # DiveBomb

        # The time between each frame should be how long "Launch" state is active for, divided by the total number of animation frames
        # Note: Launch duration multiplied by 0.25 so that the end of the animation is reached faster than the full launch duration
        self.behaviour_patterns_dict["DiveBomb"]["Launch"]["TimeBetweenAnimFrames"] = (self.behaviour_patterns_dict["DiveBomb"]["Launch"]["Duration"] * 0.25) / (len(GoldenMonkeyBoss.ImagesDict["DiveBomb"]["Launch"]))
        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["DiveBomb"]["Launch"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Launch"]["TimeBetweenAnimFrames"]

        # The time between each frame should be how long "Land" state is active for, divided by the total number of animation frames
        self.behaviour_patterns_dict["DiveBomb"]["Land"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["DiveBomb"]["Land"]["Duration"] / (len(GoldenMonkeyBoss.ImagesDict["DiveBomb"]["Land"]))
        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["DiveBomb"]["Land"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Land"]["TimeBetweenAnimFrames"]

    def play_animations(self):

        # --------------------------------------------------------
        # Set the current animation image and change the colour if there are any effects

        # If the boss is alive
        if self.current_action != "Death":

            # If the current action is "Chase"
            if self.current_action == "Chase":
                
                # The current direction the monkey is facing
                current_direction = self.find_look_direction()

                # The current animation list
                current_animation_list = GoldenMonkeyBoss.ImagesDict[self.current_action][current_direction]

                # The current animation image
                current_animation_image = current_animation_list[self.animation_index]

            # If the current action is "SpiralAttack" or "Sleep"
            elif self.current_action == "SpiralAttack" or self.current_action == "Sleep":
                
                # The current animation list
                current_animation_list = GoldenMonkeyBoss.ImagesDict[self.current_action]

                # The current animation image
                current_animation_image = current_animation_list[self.animation_index]

            # If the current action is "DiveBomb"
            elif self.current_action == "DiveBomb":
                
                # If the current divebomb stage is not "Target"
                if self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] != "Target":
                    # The current animation list (e.g. ["DiveBomb"]["Land"])
                    current_animation_list = GoldenMonkeyBoss.ImagesDict[self.current_action][self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"]]
                    # The current animation image
                    current_animation_image = current_animation_list[self.animation_index]

                # If the current divebomb stage is "Target"
                elif self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] == "Target":
                    # Set the image and image list to be anything (This is because the boss will not be in frame, so it does not matter)
                    current_animation_list = GoldenMonkeyBoss.ImagesDict[self.current_action]["Land"]
                    current_animation_image = GoldenMonkeyBoss.ImagesDict[self.current_action]["Land"][0]

            # If the boss is in its second phase
            if self.current_phase == 2:

                # Change the colour of the boss to be its second phase colour
                current_animation_image = change_image_colour(current_animation_image = current_animation_image, desired_colour = self.second_phase_colour_current_colour)
                
            # If the boss has been damaged (red and white version)
            if self.extra_information_dict["DamagedFlashEffectTimer"] != None:
                
                # Reduce the colour of the image all the way down to black
                """Note: This is because yellow is made up of red and green, so the colours must be reduced all the way down first to actually see the red (otherwise the only colour visible would be white
                and the default colours)
                """
                current_animation_image = change_image_colour_v2(current_animation_image = current_animation_image, desired_colour = (0, 0, 0))

                # Set the current animation image to be a flashed version of the current animation image (a white flash effect)
                current_animation_image = change_image_colour(current_animation_image = current_animation_image, desired_colour = random_choice(((255, 255, 255), (255, 0, 0))))

        # If the boss is not alive
        elif self.current_action == "Death":
            # Set the current animation list
            current_animation_list = self.behaviour_patterns_dict["Death"]["Images"]

            # Set the current animation image
            current_animation_image = self.behaviour_patterns_dict["Death"]["Images"][self.animation_index]

            # If the boss has been damaged (white version)
            if self.extra_information_dict["DamagedFlashEffectTimer"] != None:
                # Set the current animation image to be a flashed version of the current animation image (a white flash effect)
                current_animation_image = change_image_colour(current_animation_image = current_animation_image, desired_colour = random_choice(((255, 255, 255), (40, 40, 40))))
                
        # Set the image to be the current animation image
        self.image = current_animation_image

        # --------------------------------------------------------
        # Updating animation

        # Find which action is being performed and update the animation index based on that
        match self.current_action:

            # Chase, SpiralAttack, Sleep
            case _ if self.current_action == "Chase" or self.current_action == "SpiralAttack" or self.current_action == "Sleep":

                # Loop the animation continuously
                self.animation_index, self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] = simple_loop_animation(
                                                                                                                                        animation_index = self.animation_index,
                                                                                                                                        animation_list = current_animation_list,
                                                                                                                                        animation_frame_timer = self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"],
                                                                                                                                        time_between_anim_frames = self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]
                                                                                                                                        )

            # Death
            case _ if self.current_action == "Death":
                
                # Play the animation once to the end
                self.animation_index, self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] = simple_play_animation_once(
                                                                                                                                            animation_index = self.animation_index,
                                                                                                                                            animation_list = current_animation_list,
                                                                                                                                            animation_frame_timer = self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"],
                                                                                                                                            time_between_anim_frames = self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]
                                                                                                                                            )

            # Divebomb
            case _ if self.current_action == "DiveBomb":

                # Current divebomb stage
                current_stage = self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"]
                
                # If the current stage is not "Target"
                if current_stage != "Target":

                    # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
                    if self.animation_index < (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action][current_stage]["AnimationFrameTimer"]) <= 0:
                        # Go the next animation frame
                        self.animation_index += 1

                        # Reset the timer 
                        self.behaviour_patterns_dict[self.current_action][current_stage]["AnimationFrameTimer"] = self.behaviour_patterns_dict[self.current_action][current_stage]["TimeBetweenAnimFrames"]
            
        # --------------------------------------------------------
        # Additional for sleeping
        
        # Creates sleep effect text
        self.create_sleep_text()

        # -----------------------------------
        # Updating timers
        
        # If the current action isn't "DiveBomb"
        if self.current_action != "DiveBomb":
            # Decrease the animation frame timers
            self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] -= 1000 * self.delta_time

        # If the current action is "DiveBomb"
        elif self.current_action == "DiveBomb":
            # If the current divebomb stage is not "Target" ("Target" does not have an animation")
            if current_stage != "Target":
                # Decrease the animation frame timers
                self.behaviour_patterns_dict[self.current_action][current_stage]["AnimationFrameTimer"] -= 1000 * self.delta_time

        # Update damage flash effect timer
        self.update_damage_flash_effect_timer()

    def create_sleep_text(self):
        
        # Creates sleep effect text when the boss is in the sleep state (effect text is always updated by the game UI)

        # If enough time has passed since the last sleep effect text was created and the current action is "Sleep"
        if self.sleep_effect_text_info_dict["CreationCooldownTimer"] == None and self.current_action == "Sleep":
            
            # Position of the text
            text_position_x = (self.rect.midtop[0] + 3) - self.camera_position[0]
            text_position_y = ((self.rect.midtop[1] - (self.sleep_effect_text_info_dict["FontSize"][1] / 2)) + 12) - self.camera_position[1]

            # Alpha surface
            new_alpha_surface = pygame_Surface(self.sleep_effect_text_info_dict["FontSize"])
            new_alpha_surface.set_colorkey("black")
            new_alpha_surface.set_alpha(self.sleep_effect_text_info_dict["DefaultAlphaLevel"])

            # Create the effect text (Automatically added to the effect text group)
            EffectText(
                        x = text_position_x,
                        y = text_position_y,
                        colour = self.sleep_effect_text_info_dict["Colour"],
                        display_time = self.sleep_effect_text_info_dict["DisplayTime"], 
                        text = self.sleep_effect_text_info_dict["Text"],
                        font = self.sleep_effect_text_info_dict["Font"],
                        alpha_surface = new_alpha_surface,
                        alpha_level = self.sleep_effect_text_info_dict["DefaultAlphaLevel"],
                        type_of_effect_text = "Sleep"
                        )

            # Set the creation timer cooldown to start
            self.sleep_effect_text_info_dict["CreationCooldownTimer"] = self.sleep_effect_text_info_dict["CreationCooldownTime"]

    # ----------------------------------------------------------------------------------
    # Gameplay

    def decide_action(self):

        # The main "brain" of the deer boss, which will decide on what action to perform

        # Find the player (To continuously update the look angle)
        """Note: This is done because even if the boss other attacks will also need the current look angle """
        self.find_player(current_position = self.rect.center, player_position = self.players_position, delta_time = self.delta_time)
        
        # If the energy amount is greater than 0
        if self.energy_amount > 0:

            # If the current action is "Chase"
            if self.current_action == "Chase":

                # If the boss did not just enter phase 2 (so that it doesn't interrupt the effect)
                if hasattr(self, "second_phase_circles_dict") == False:
                    # Create a list of all the actions that the AI can currently perform, if the action's cooldown timer is None
                    action_list = [action for action in self.behaviour_patterns_dict.keys() if (action == "SpiralAttack" or action == "DiveBomb") and self.behaviour_patterns_dict[action]["CooldownTimer"] == None]

                # If the boss just entered phase 2
                elif hasattr(self, "second_phase_circles_dict") == True:
                    # Set the action list as empty, meaning that the boss can only chase the player
                    action_list = []

                # If there are any possible actions that the boss can perform (other than "Chase") and the boss has not performed an action recently 
                if len(action_list) > 0 and self.extra_information_dict["NoActionTimer"] == None:

                    # Reset the animation index whenever we change the action
                    self.animation_index = 0

                    # Choose a random action from the possible actions the boss can perform and set it as the current action
                    self.current_action = random_choice(action_list)

                    # If the current action that was chosen was "SpiralAttack", and "SpiralAttack" duration timer has not been set to start counting down yet
                    if self.current_action == "SpiralAttack" and self.behaviour_patterns_dict["SpiralAttack"]["DurationTimer"] == None:

                        # --------------------------------------------
                        # Chillis

                        # Set the duration timer to start counting down
                        self.behaviour_patterns_dict["SpiralAttack"]["DurationTimer"] = self.behaviour_patterns_dict["SpiralAttack"]["Duration"] 

                        # Set the chilli projectile controllers center position so that chilli projectiles can spawn from the center of the boss
                        self.chilli_projectile_controller.boss_center_position = self.rect.center

                        # Set the rotation direction for this spiral attack (1 = clockwise, -1 = anti-clockwise)
                        self.chilli_projectile_controller.spiral_attack_angle_time_gradient *= random_choice([-1, 1])

                        # --------------------------------------------
                        # Spin
                        
                        # Set the pivot point to be the current center of the boss 
                        self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotPoint"] = self.rect.center

                        # Alter the angle time gradient of the spin, so that the boss can rotate around the pivot point clockwise or anti clockwise
                        self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngleTimeGradient"] *= random_choice([-1, 1])


                    # If the current action that was chosen was "DiveBomb" and the current divebomb stage is set to None (meaning the attack has not started yet)
                    elif self.current_action == "DiveBomb" and self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] == None:
                        
                        # Set the divebomb stage to be Launch
                        self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] = "Launch"
                        
                        # Set the "Launch" duration timer to start counting down
                        self.behaviour_patterns_dict["DiveBomb"]["Launch"]["DurationTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Launch"]["Duration"]
                
                # If there are no possible actions that the boss can perform or the boss has performed an action recently
                elif len(action_list) == 0 or self.extra_information_dict["NoActionTimer"] != None:
                    # Move the boss (i.e. Chase the player)
                    self.move()

                    # If the boss has not thrown a chilli recently
                    if self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"] == None:
                        
                        # The angle the projectile will travel at
                        projectile_angle = self.movement_information_dict["Angle"]
                        
                        # Create a chilli projectile and throw it at the player
                        self.chilli_projectile_controller.create_chilli_projectile(
                                        x_pos = self.rect.centerx,
                                        y_pos = self.rect.centery,
                                        angle = projectile_angle,
                                        damage_amount = ChilliProjectileController.base_damage
                                                                                    )

                        # Set the cooldown timer to start counting down
                        self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"] = self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldown"] 

                    # Update the cooldown for throwing chillis whilst chasing the player
                    self.update_chilli_throwing_cooldown_timer()

            # If the current action is "SpiralAttack"
            if self.current_action == "SpiralAttack":

                # -------------------------------------------------------------------------------------------------
                # Chilli spiral attack
                
                # If enough time has passed since the last set of chilli projectiles were sent out
                if self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"] == None:
                    # Perform the spiral attack
                    self.chilli_projectile_controller.create_spiral_attack()
                    # Start the cooldown for the chilli spawning
                    self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"] = self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldown"]

                # Always increase the spiral attack angle
                self.chilli_projectile_controller.increase_spiral_attack_angle(delta_time = self.delta_time)

                # Update the spiral chilli spawning cooldown timer
                self.update_spiral_chilli_spawning_cooldown_timer()

                # --------------------------------------------
                # Pivoting around the original center point

                # Increase the angle
                self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewAngle"] += self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngleTimeGradient"] * self.delta_time
                self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngle"] = round(self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewAngle"])

                # Calculate the horizontal and vertical distnaces the player should be away from the pivot point
                displacement_x = (self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotDistance"] * cos(radians(self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngle"])))
                displacement_y = (self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotDistance"] * sin(radians(self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngle"])))
                
                # Calculate the new center position of the boss
                self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewCenterPositions"] = (
                                                                            self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotPoint"][0] + displacement_x ,
                                                                            self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotPoint"][1] + displacement_y 
                                                                                                    )
                
                # Set the center of the boss to be the same as the new center positions
                self.rect.centerx = self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewCenterPositions"][0]
                self.rect.centery = self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewCenterPositions"][1]

            # If the current action is "DiveBomb"
            elif self.current_action == "DiveBomb":
                # If the boss is in the "Launch" stage of the "DiveBomb" action
                if self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] == "Launch":
                    
                    # Modify the gradient depending on how much time is left before the boss enters the "Target" stage
                    self.behaviour_patterns_dict["DiveBomb"]["Launch"]["JumpUpGradient"] = (
                        self.behaviour_patterns_dict["DiveBomb"]["Launch"]["LaunchDistance"] / ((self.behaviour_patterns_dict["DiveBomb"]["Launch"]["DurationTimer"] / self.behaviour_patterns_dict["DiveBomb"]["Launch"]["Duration"]) / 10)
                                                                                            )                                                   
                    # Decrease the position of the boss (to move up)
                    self.rect.y -= self.behaviour_patterns_dict["DiveBomb"]["Launch"]["JumpUpGradient"] * self.delta_time
                
        # If the boss has 0 or less than 0 energy
        elif self.energy_amount <= 0:
            
            # If the current action is not already "Sleep" (meaning this is the first time this if check was entered)
            if self.current_action != "Sleep":
                # Set the current action to "Sleep"
                self.current_action = "Sleep"
                # Set the animation index back to 0
                self.animation_index = 0
                # Set the sleep duration timer to start counting down
                self.behaviour_patterns_dict["Sleep"]["DurationTimer"] = self.behaviour_patterns_dict["Sleep"]["Duration"]

    def update_and_draw_divebomb_circles(self, delta_time):

        # If the current dive bomb stage is "Target"
        if self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] == "Target":
            
            # Fill the dive bomb attack controller's alpha surface with black
            self.dive_bomb_attack_controller.alpha_surface.fill("black")

            # Draw the circles onto the alpha surface
            # Note: The center 
            pygame_draw_circle(
                            surface = self.dive_bomb_attack_controller.alpha_surface, 
                            color = (180, 0, 0), 
                            center = (self.dive_bomb_attack_controller.maximum_circle_radius, self.dive_bomb_attack_controller.maximum_circle_radius), 
                            radius = self.dive_bomb_attack_controller.maximum_circle_radius, 
                            width = 0
                            )

            pygame_draw_circle(
                            surface = self.dive_bomb_attack_controller.alpha_surface, 
                            color = (225, 0, 0), 
                            center = (self.dive_bomb_attack_controller.maximum_circle_radius, self.dive_bomb_attack_controller.maximum_circle_radius), 
                            radius = self.dive_bomb_attack_controller.growing_circle_radius, 
                            width = 0
                            )
                            
            pygame_draw_circle(
                            surface = self.dive_bomb_attack_controller.alpha_surface, 
                            color = (255, 0, 0), 
                            center = (self.dive_bomb_attack_controller.maximum_circle_radius, self.dive_bomb_attack_controller.maximum_circle_radius), 
                            radius = min(0, self.dive_bomb_attack_controller.growing_circle_radius - 20),
                            width = 0
                            )

            # Blit the center of the alpha surface at the landing position (Which would be the center of the player)
            self.surface.blit(
                            self.dive_bomb_attack_controller.alpha_surface, 
                            (
                            (self.dive_bomb_attack_controller.landing_position[0] - self.dive_bomb_attack_controller.maximum_circle_radius) - self.camera_position[0],
                            (self.dive_bomb_attack_controller.landing_position[1] - self.dive_bomb_attack_controller.maximum_circle_radius)  - self.camera_position[1]
                            )
                            )

            # Increase the radius of the smaller, growing circle and change the alpha level of the alpha surface
            self.dive_bomb_attack_controller.change_visual_effects(
                                proportional_time_remaining = self.behaviour_patterns_dict["DiveBomb"]["Target"]["DurationTimer"] / self.behaviour_patterns_dict["DiveBomb"]["Target"]["Duration"],
                                delta_time = delta_time
                                                                            )

            # Outline
            pygame_draw_circle(
                            surface = self.surface, 
                            color = (0, 0, 0), 
                            center = (self.dive_bomb_attack_controller.landing_position[0] - self.camera_position[0], self.dive_bomb_attack_controller.landing_position[1] - self.camera_position[1]), 
                            radius = self.dive_bomb_attack_controller.maximum_circle_radius, 
                            width = 3
                            )

            # self.dive_bomb_attack_controller.draw(surface= self.surface, x = self.dive_bomb_attack_controller.rect.x - self.camera_position[0], y = self.dive_bomb_attack_controller.rect.y - self.camera_position[1])
    
    def draw_shockwave_circles(self, delta_time):
        
        # Draws the shockwave circles
    
        # Fill the shockwave circle alpha surface with black
        self.dive_bomb_attack_controller.shockwave_circle_alpha_surface.fill("black")


        # Drawing the shockwave circles
        pygame_draw_circle(
                        surface = self.dive_bomb_attack_controller.shockwave_circle_alpha_surface, 
                        color = (100, 0, 0),
                        center = (self.dive_bomb_attack_controller.shockwave_circle_alpha_surface_size[0] / 2, self.dive_bomb_attack_controller.shockwave_circle_alpha_surface_size[1] / 2), 
                        radius = self.dive_bomb_attack_controller.shockwave_circle_current_radius, 
                        width = 0
                        )
        pygame_draw_circle(
                        surface = self.dive_bomb_attack_controller.shockwave_circle_alpha_surface, 
                        color = (120, 0, 0),
                        center = (self.dive_bomb_attack_controller.shockwave_circle_alpha_surface_size[0] / 2, self.dive_bomb_attack_controller.shockwave_circle_alpha_surface_size[1] / 2), 
                        radius = self.dive_bomb_attack_controller.shockwave_circle_current_radius * 0.4, 
                        width = 0
                        )
        pygame_draw_circle(
                        surface = self.dive_bomb_attack_controller.shockwave_circle_alpha_surface, 
                        color = (140, 0, 0),
                        center = (self.dive_bomb_attack_controller.shockwave_circle_alpha_surface_size[0] / 2, self.dive_bomb_attack_controller.shockwave_circle_alpha_surface_size[1] / 2), 
                        radius = self.dive_bomb_attack_controller.shockwave_circle_current_radius * 0.15, 
                        width = 0
                        )

        # Blit the center of the alpha surface at the landing position (Which would be the center of the player)
        # Note: The rect positions should be the 
        self.surface.blit(
                        self.dive_bomb_attack_controller.shockwave_circle_alpha_surface, 
                        (
                        (self.dive_bomb_attack_controller.rect.centerx - (self.dive_bomb_attack_controller.shockwave_circle_alpha_surface_size[0] / 2)) - self.camera_position[0],
                        (self.dive_bomb_attack_controller.rect.centery - (self.dive_bomb_attack_controller.shockwave_circle_alpha_surface_size[1] / 2))  - self.camera_position[1]
                        ),
                        )
    
        # Change the alpha level and size of the shockwave circles
        self.dive_bomb_attack_controller.change_shockwave_circles_visual_effect(delta_time = delta_time)

    def update_and_draw_second_phase_circles(self, delta_time):

        # Fill the alpha surface with black
        self.second_phase_circles_dict["AlphaSurface"].fill("black")
        
        # The current colour
        current_colour = self.second_phase_circles_dict["Colours"][self.second_phase_circles_dict["CircleCounterIndex"]]
            
        # Outer circle
        pygame_draw_circle(
                        surface = self.second_phase_circles_dict["AlphaSurface"],
                        color = (max(current_colour[0] - 60, 0), max(current_colour[1] - 60, 0), max(current_colour[2] - 60, 0)),
                        center = (self.second_phase_circles_dict["AlphaSurfaceSize"][0] / 2, self.second_phase_circles_dict["AlphaSurfaceSize"][1] / 2),
                        radius = self.second_phase_circles_dict["CurrentRadiusList"][self.second_phase_circles_dict["CircleCounterIndex"]], 
                        width = 0
                        )

        # Mid-circle
        pygame_draw_circle(
                        surface = self.second_phase_circles_dict["AlphaSurface"],
                        color = (max(current_colour[0] - 20, 0), max(current_colour[1] - 20, 0), max(current_colour[2] - 20, 0)),
                        center = (self.second_phase_circles_dict["AlphaSurfaceSize"][0] / 2, self.second_phase_circles_dict["AlphaSurfaceSize"][1] / 2),
                        radius = self.second_phase_circles_dict["CurrentRadiusList"][self.second_phase_circles_dict["CircleCounterIndex"]] * 0.5, 
                        width = 0
                        )

        # Inner circle
        pygame_draw_circle(
                        surface = self.second_phase_circles_dict["AlphaSurface"],
                        color = current_colour,
                        center = (self.second_phase_circles_dict["AlphaSurfaceSize"][0] / 2, self.second_phase_circles_dict["AlphaSurfaceSize"][1] / 2),
                        radius = self.second_phase_circles_dict["CurrentRadiusList"][self.second_phase_circles_dict["CircleCounterIndex"]] * 0.2, 
                        width = 0
                        )
        
        # If all three circles have not been drawn yet, and the inner circle of the last circle is less than the maximum radius
        if self.second_phase_circles_dict["CircleCounterIndex"] < 3 and (self.second_phase_circles_dict["CurrentRadiusList"][self.second_phase_circles_dict["CircleCounterIndex"] ]) < self.second_phase_circles_dict["MaximumRadius"]:
            # Increase the radius of the shockwave circle
            self.second_phase_circles_dict["CurrentRadiusList"][self.second_phase_circles_dict["CircleCounterIndex"]] += self.second_phase_circles_dict["RadiusTimeGradient"] * delta_time


        # ---------------------------------------------------------------------------------------------
        # Alpha surfaces    

        # Update the blit position along with the center of the boss
        self.second_phase_circles_dict["BlitPosition"] = ( 
                                (self.rect.centerx - self.camera_position[0]) - (self.second_phase_circles_dict["AlphaSurfaceSize"][0] / 2),
                                (self.rect.centery - self.camera_position[1]) - (self.second_phase_circles_dict["AlphaSurfaceSize"][1] / 2)
                                )

        # Blit alpha surface onto the main surface
        # Note: The blending alpha surface and alpha surface are both the tile map size
        self.surface.blit(
                        self.second_phase_circles_dict["AlphaSurface"], 
                        self.second_phase_circles_dict["BlitPosition"]
                        )

        # If the current alpha level of the main alpha surface is greater than 0
        if self.second_phase_circles_dict["CurrentAlphaLevel"] > 0:
            # Decrease the alpha level of the shockwave circle alpha surface
            self.second_phase_circles_dict["CurrentAlphaLevel"] = max(0, self.second_phase_circles_dict["CurrentAlphaLevel"] + (self.second_phase_circles_dict["AlphaLevelTimeGradient"] * delta_time))
            self.second_phase_circles_dict["AlphaSurface"].set_alpha(self.second_phase_circles_dict["CurrentAlphaLevel"])

        # If e.g. the first circle has finished growing to the maximum radius and all 3 circles have not been drawn yet
        if self.second_phase_circles_dict["CurrentRadiusList"][self.second_phase_circles_dict["CircleCounterIndex"]] > self.second_phase_circles_dict["MaximumRadius"] \
            and self.second_phase_circles_dict["CircleCounterIndex"] < 2:

            # Reset the alpha level of the surface back to its default values for the next circles
            self.second_phase_circles_dict["CurrentAlphaLevel"] = self.second_phase_circles_dict["StartingAlphaLevel"]
            self.second_phase_circles_dict["AlphaSurface"].set_alpha(self.second_phase_circles_dict["CurrentAlphaLevel"])

            # Increment the number of circles already drawn
            self.second_phase_circles_dict["CircleCounterIndex"] += 1

        # If 3 circles have been drawn and the alpha level of tbe alpha surface is less than or equal to 0
        if self.second_phase_circles_dict["CircleCounterIndex"] == 2 and self.second_phase_circles_dict["CurrentAlphaLevel"] <= 0:
            # Delete the second phase circles dictionary
            del self.second_phase_circles_dict

    # ----------------------------------------------------------------------------------
    # Timer updating

    def update_duration_timers(self):

        # Updates the duration timer of the current action 
        # If the duration timer is over, the action is added to the previous actions list so that their cooldown timer can be updated
        
        # If the current action is not "Chase" (Chase does not have a duration timer) or "DiveBomb" (DiveBomb has multiple stages)
        if self.current_action != "Chase" and self.current_action != "DiveBomb":
            
            # Decrease the timer
            self.behaviour_patterns_dict[self.current_action]["DurationTimer"] -= 1000 * self.delta_time
            
            # If the current action's duration timer has finished counting down
            if self.behaviour_patterns_dict[self.current_action]["DurationTimer"] <= 0:
                # Reset the duration timer back to None
                self.behaviour_patterns_dict[self.current_action]["DurationTimer"] = None

                # Reset the animation index
                self.animation_index = 0

                # If the current action is not "Sleep"
                # Note: "Sleep" does not have a cooldown
                if self.current_action != "Sleep":
                    # Add the current action to the previous actions dict so that its cooldown timer can count down
                    self.previous_actions_dict[self.current_action] = None

                # -----------------------------------------------------------------------------------
                # Additional resets depending on the action

                # If the current action is "SpiralAttack"
                if self.current_action == "SpiralAttack":

                    # Set the current action back to Chase
                    self.current_action = "Chase"

                    # Set the no action timer to start counting down
                    self.extra_information_dict["NoActionTimer"] = self.extra_information_dict["NoActionTime"]

                    # Set the cooldown timer to start counting down
                    self.behaviour_patterns_dict["SpiralAttack"]["CooldownTimer"] = self.behaviour_patterns_dict["SpiralAttack"]["Cooldown"]

                    # Reduce the amount of energy that the boss has
                    self.energy_amount -= self.behaviour_patterns_dict["SpiralAttack"]["EnergyDepletionAmount"]

                    # --------------------------------------
                    # Spin

                    # Reset the angles for the spin pivoting
                    self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngle"] = 0
                    self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewAngle"] = 0

                    # Set the position of the boss to be the original position again
                    self.rect.center = self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotPoint"]
                    # Reset the pivot point back to None
                    self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotPoint"] = None

                # If the current action is "Sleep"
                elif self.current_action == "Sleep":
                    # Set the current action back to Chase
                    self.current_action = "Chase"

                    # Set the energy amount back to the maximum amount
                    self.energy_amount = GoldenMonkeyBoss.maximum_energy_amount

        # If the current action is "DiveBomb"
        elif self.current_action == "DiveBomb":
            
            # Current DiveBomb stage
            current_stage = self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] 

            # If the current action's duration timer has not finished counting down
            if self.behaviour_patterns_dict["DiveBomb"][current_stage]["DurationTimer"] > 0:
                # Decrease the timer
                self.behaviour_patterns_dict["DiveBomb"][current_stage]["DurationTimer"] -= 1000 * self.delta_time
            
            # If the current action's duration timer has finished counting down
            if self.behaviour_patterns_dict["DiveBomb"][current_stage]["DurationTimer"] <= 0:
                # Reset the duration timer back to None
                self.behaviour_patterns_dict["DiveBomb"][current_stage]["DurationTimer"] = None

                # Reset the animation index
                self.animation_index = 0

                # Identify the current divebomb stage
                match current_stage:

                    case "Launch":

                        # Set the next stage to be "Target"wdddaw
                        self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] = "Target"

                        # Set the divebomb "Target" duration timer to start counting down
                        self.behaviour_patterns_dict["DiveBomb"]["Target"]["DurationTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Target"]["Duration"]

                        # -----------------------------------------------------------------------
                        # Finding a valid divebomb end position 

                        """Note:
                        - The landing position is the center of the player, therefore if the plasayer was at the edge of the map, the boss would be spawned inside the tile.
                        The following code will correct the positions so that e.g. if the player was on the far right of the map, the landing position would need to be at a position where
                        the right side of the boss' rect would be touching the far right tile, but not  inside
                        """
                        # Save the new position in a temporary variable
                        new_position = [self.players_position[0], self.players_position[1]]

                        # Right side correction:
                        if (new_position[0] + (self.rect.width / 2)) >= GoldenMonkeyBoss.boss_map_boundaries["Right"]:
                            new_position[0] = GoldenMonkeyBoss.boss_map_boundaries["Right"] - (self.rect.width / 2)
                        
                        # Left side correction:
                        if (new_position[0] - (self.rect.width / 2)) <= GoldenMonkeyBoss.boss_map_boundaries["Left"]:
                            new_position[0] = GoldenMonkeyBoss.boss_map_boundaries["Left"] + (self.rect.width / 2)
                        
                        # Top side correction 
                        if (new_position[1] - (self.rect.height / 2)) <= GoldenMonkeyBoss.boss_map_boundaries["Top"]:
                            new_position[1] = GoldenMonkeyBoss.boss_map_boundaries["Top"] + (self.rect.height / 2)

                        # Bottom side correction 
                        if (new_position[1] + (self.rect.height / 2)) >= GoldenMonkeyBoss.boss_map_boundaries["Bottom"]:
                            new_position[1] = GoldenMonkeyBoss.boss_map_boundaries["Bottom"]  - (self.rect.height / 2)

                        # Set the divebomb's end position (where to land) to be the calculated position
                        self.dive_bomb_attack_controller.landing_position = new_position
                        
                        # Set the divebomb attack controller's center to be the same as the player (for the image to also be centered for mask collisions)
                        self.dive_bomb_attack_controller.rect.center = new_position

                        # Modify the movement infomration dict's new center positions so that when the boss lands, it won't teleport back to its old position
                        # Note: -(self.rect.height) / 2, so that the bottom of the boss will be spawned at the landing position
                        self.movement_information_dict["NewPositionCenterX"] = self.dive_bomb_attack_controller.landing_position[0]
                        self.movement_information_dict["NewPositionCenterY"] = self.dive_bomb_attack_controller.landing_position[1]

                        # Take the boss off the map
                        self.rect.center = (10000, 10000)

                    case "Target":

                        # Set the next stage to be "Land"
                        self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] = "Land"

                        # Set the divebomb "Land" duration timer to start counting down
                        self.behaviour_patterns_dict["DiveBomb"]["Land"]["DurationTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Land"]["Duration"]

                        # Set the boss to be at the landing position
                        self.rect.center = self.dive_bomb_attack_controller.landing_position

                        # Update the angle between the boss and the player, so that the player gets knocked back properly
                        self.find_player(player_position = self.players_position, current_position = self.dive_bomb_attack_controller.landing_position, delta_time = self.delta_time) 

                        # Reset the divebomb attributes of the divebobm attack controller
                        self.dive_bomb_attack_controller.reset_divebomb_attributes()

                        # Set the shockwave circle timer to start as the boss just landed (visual effect)
                        self.dive_bomb_attack_controller.shockwave_circle_alive_timer = self.dive_bomb_attack_controller.shockwave_circle_alive_time * 1000

                    case "Land":
                        
                        # If current phase is the first phase or the boss is in the second phase and the boss has dive bombed the player 3 times already
                        if self.current_phase == 1 or (self.current_phase == 2 and self.behaviour_patterns_dict["DiveBomb"]["SecondPhaseDiveBombCounter"] == 2):
                            # Set the current action back to "Chase"
                            self.current_action = "Chase"

                            # Set the next stage to be None
                            self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] = None

                            # Set the cooldown timer to start counting down
                            self.behaviour_patterns_dict["DiveBomb"]["CooldownTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Cooldown"]

                            # Set the no action timer to start counting down
                            self.extra_information_dict["NoActionTimer"] = self.extra_information_dict["NoActionTime"]
                            
                            # Add the divebomb action to the previous actions dict so that its cooldown timer can count down
                            self.previous_actions_dict["DiveBomb"] = None

                            # Reduce the amount of energy that the boss has
                            self.energy_amount -= self.behaviour_patterns_dict["DiveBomb"]["EnergyDepletionAmount"]

                            # If the boss has divebombed the player 3 times already
                            if self.behaviour_patterns_dict["DiveBomb"]["SecondPhaseDiveBombCounter"] == 2:
                                # Reset the seocnd phased dive bomb counter
                                self.behaviour_patterns_dict["DiveBomb"]["SecondPhaseDiveBombCounter"] = 0

                        # If the boss is in the second phase, and the boss has not divebombed the player 3 times yet
                        elif self.current_phase == 2 and self.behaviour_patterns_dict["DiveBomb"]["SecondPhaseDiveBombCounter"] < 2:
                            # Set the current action back to DiveBomb
                            self.current_action = "DiveBomb"

                            # Set the next stage to be None
                            self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] = "Launch"

                            # Set the "Launch" duration timer to start counting down
                            self.behaviour_patterns_dict["DiveBomb"]["Launch"]["DurationTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Launch"]["Duration"]

                            # Increment the second phase dive bomb counter
                            self.behaviour_patterns_dict["DiveBomb"]["SecondPhaseDiveBombCounter"] += 1

    def update_spiral_chilli_spawning_cooldown_timer(self):

        # Timer for the spawning of chillis during the spiral attack

        self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"] = update_generic_timer(
                                                                                                                current_timer = self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"],
                                                                                                                delta_time = self.delta_time
                                                                                                                )

    def update_chilli_throwing_cooldown_timer(self):

        # Timer for the spawning of chillis whilst chasing the plyaer

        self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"] = update_generic_timer(
                                                                                                    current_timer = self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"],
                                                                                                    delta_time = self.delta_time
                                                                                                    )

    def update_sleep_effect_text_timer(self):

        # Timer for the creation of sleep effect text

        self.sleep_effect_text_info_dict["CreationCooldownTimer"] = update_generic_timer(
                                                                                        current_timer = self.sleep_effect_text_info_dict["CreationCooldownTimer"],
                                                                                        delta_time = self.delta_time
                                                                                        )
    
    def run(self):
         
        # Always update / move / draw the chilli projectiles
        self.chilli_projectile_controller.update_chilli_projectiles(
                                                                    delta_time = self.delta_time,
                                                                    camera_position = self.camera_position,
                                                                    surface = self.surface
                                                                    )

        # If the boss is not alive
        if self.current_action == "Death":
            # Draw a shadow ellipse underneath the boss
            pygame_draw_ellipse(
                surface = self.surface, 
                color = (20, 20, 20), 
                rect = ((self.rect.centerx - self.camera_position[0]) - 20, 
                ((self.rect.centery + 20) - self.camera_position[1]) - 20, 40, 40), 
                width = 0)

        # If the boss has spawned and the camera panning has been completed
        if self.extra_information_dict["CanStartOperating"] == True:
            
            # If the boss is alive:
            if self.extra_information_dict["CurrentHealth"] > 0:
                # Decide the action that the boss should perform
                self.decide_action()

            # Check if the boss' health is less than 0
            elif self.extra_information_dict["CurrentHealth"] <= 0:
                
                # If current action has not been set to "Death" and the boss does not have a death animation images list yet
                if self.current_action != "Death" and self.behaviour_patterns_dict["Death"]["Images"]  == None:
                    

                    """Note: Do not set self.extra_information_dict["CanStartOperating"] to False, otherwise the death animation will not play"""
                    
                    # Reset the animation index
                    self.animation_index = 0

                    # Set the current action to death
                    self.current_action = "Death"

                    # Load and scale the death animation images 
                    self.behaviour_patterns_dict["Death"]["Images"] = [scale_image(
                        load_image(f"graphics/Misc/DeathAnimation/{i}.png").convert_alpha(), ((load_image(f"graphics/Misc/DeathAnimation/{i}.png").convert_alpha().get_width() * 2, load_image(f"graphics/Misc/DeathAnimation/{i}.png").convert_alpha().get_height() * 2)))  
                        for i in range(0, len(os_listdir("graphics/Misc/DeathAnimation")))]

                    # Set up the animation speed and timer
                    self.behaviour_patterns_dict["Death"]["FullAnimationDuration"] = FULL_DEATH_ANIMATION_DURATION
                    self.behaviour_patterns_dict["Death"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Death"]["FullAnimationDuration"] / len(self.behaviour_patterns_dict["Death"]["Images"])
                    self.behaviour_patterns_dict["Death"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Death"]["TimeBetweenAnimFrames"]

            # Play animations
            self.play_animations()

            # Create / update a mask for pixel - perfect collisions
            self.mask = pygame_mask_from_surface(self.image)

            # If the boss is alive
            if self.extra_information_dict["CurrentHealth"] > 0:

                # If the boss has less than 40% of its maximum health and is currently chasing the player
                if self.extra_information_dict["CurrentHealth"] <=  (0.4 * self.extra_information_dict["MaximumHealth"]) and self.current_action == "Chase":
                    # If the boss is not already in phase 2
                    if self.current_phase != 2:

                        # Go into phase 2
                        self.current_phase = 2
                        
                        # Reduce the spawning cooldowns of the spiral attack
                        self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldown"] *= 0.75

                        # -------------------------------------------------------
                        # Second phase circles

                        # Create a circles dict for the second phase circles effect
                        self.second_phase_circles_dict = {
                                                    "AliveTime": 1.5,
                                                    "CircleCounterIndex": 0,
                                                    "MinimumRadius": 30,
                                                    "MaximumRadius": 500,
                                                    "StartingAlphaLevel": 80,
                                                    "Colours": ((238, 44, 44), (191, 62, 255), (255, 215, 0))
                                                
                                                    }

                        # Current radius / alpha level
                        self.second_phase_circles_dict["CurrentRadiusList"] = [self.second_phase_circles_dict["MinimumRadius"] for i in range(0, 3)]
                        self.second_phase_circles_dict["CurrentAlphaLevel"] = self.second_phase_circles_dict["StartingAlphaLevel"] 

                        # Alpha level / radius time gradients
                        self.second_phase_circles_dict["AlphaLevelTimeGradient"] = (0 - self.second_phase_circles_dict["StartingAlphaLevel"]) / (self.second_phase_circles_dict["AliveTime"] * 1) # * 3 because there are 3 circles to be drawn
                        self.second_phase_circles_dict["RadiusTimeGradient"] = (self.second_phase_circles_dict["MaximumRadius"] - self.second_phase_circles_dict["MinimumRadius"]) / self.second_phase_circles_dict["AliveTime"]

                        # Alpha surface
                        # self.second_phase_circles_dict["AlphaSurface"] = pygame_Surface(GoldenMonkeyBoss.boss_map_boundaries["EntireTileMapSize"])

                        self.second_phase_circles_dict["AlphaSurface"] = pygame_Surface((self.second_phase_circles_dict["MaximumRadius"] * 2, self.second_phase_circles_dict["MaximumRadius"] * 2))
                        self.second_phase_circles_dict["AlphaSurfaceSize"] = self.second_phase_circles_dict["AlphaSurface"].get_size()
                        self.second_phase_circles_dict["AlphaSurface"].set_alpha(self.second_phase_circles_dict["StartingAlphaLevel"])
                        self.second_phase_circles_dict["AlphaSurface"].set_colorkey("black")
                    
                    # Update the second phase colour
                    self.update_second_phase_colour()

                    # If there is a dictionary called "second_phase_circles_dict"
                    # Note: This is because once the effect is complete, the dictionary is deleted
                    if hasattr(self, "second_phase_circles_dict") == True:
                        # Update and draw the second phase circles
                        self.update_and_draw_second_phase_circles(delta_time = self.delta_time)


                # Update the duration timers
                self.update_duration_timers()

                # Update the cooldown timers
                self.update_cooldown_timers()

                # Update the knockback collision idle timer
                self.update_knockback_collision_idle_timer()

                # If the current action is not "Sleep"
                if self.current_action != "Sleep":
                    # Update the no action timer (meaning the boss cannot perform any other actions other than chasing)
                    self.update_no_action_timer()

                # If the current action is "Sleep"
                elif self.current_action == "Sleep":
                    # Update the sleep effect text timer
                    self.update_sleep_effect_text_timer()

        # Draw the boss 
        """ Notes: 
        - Additional positions to center the image (this is because the animation images can vary in size)
        - This is down here because the chilli projectiles should be drawn under the boss 
        """
        self.draw(
            surface = self.surface, 
            x = (self.rect.x - ((self.image.get_width() / 2)  - (self.rect.width / 2))) - self.camera_position[0], 
            y = (self.rect.y - ((self.image.get_height() / 2) - (self.rect.height / 2))) - self.camera_position[1]
                )

        # # TEMPORARY
        # pygame_draw_rect(self.surface, "green", (self.rect.x - self.camera_position[0], self.rect.y - self.camera_position[1], self.rect.width, self.rect.height), 1)

        # for tile in self.neighbouring_tiles_dict.keys():
        #     pygame_draw_rect(self.surface, "white", (tile.rect.x - self.camera_position[0], tile.rect.y - self.camera_position[1], tile.rect.width, tile.rect.height))