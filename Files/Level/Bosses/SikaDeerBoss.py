from Global.generic import Generic
from Global.functions import change_image_colour, simple_loop_animation, simple_play_animation_once
from Global.settings import TILE_SIZE, FULL_DEATH_ANIMATION_DURATION
from Level.Bosses.BossAttacks.stomp import StompController
from pygame import Rect as pygame_Rect
from pygame.draw import circle as pygame_draw_circle
from pygame.mask import from_surface as pygame_mask_from_surface
from random import choice as random_choice
from Level.Bosses.AI import AI
from pygame.image import load as load_image
from pygame.transform import scale as scale_image
from os import listdir as os_listdir
from pygame.draw import ellipse as pygame_draw_ellipse
from math import degrees, cos, sin

class SikaDeerBoss(Generic, AI):

    # ImagesDict = ?? (This is set when the boss is instantiated)
    # Example: Stomp : [Image list]
    
    # Characteristics
    knockback_damage = 30
    maximum_health = 25000
    

    # SUVAT variables
    suvat_dict = { 
                # The default distance travelled
                "DefaultDistanceTravelled": 4 * TILE_SIZE,

                # Time to travel the horizontal/vertical distance at the final veloctiy
                "DefaultHorizontalTimeToTravelDistanceAtFinalVelocity": 0.435,
                "DefaultVerticalTimeToTravelDistanceAtFinalVelocity": 0.435,

                # Time to reach / accelerate to the final horizontal/vertical velocity
                "DefaultHorizontalTimeToReachFinalVelocity": 0.3,
                "DefaultVerticalTimeToReachFinalVelocity": 0.3,

                # The distance the AI has to be away from the player to stop chasing them
                "DistanceThreshold": 0

                }

    def __init__(self, x, y, surface, scale_multiplier):

        # Surface that the boss is drawn onto
        self.surface = surface 
        
        # The starting image when spawned (Used as the ending image of the deer boss if the player dies)
        self.starting_image = SikaDeerBoss.ImagesDict["Stomp"][0]

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x , y = y, image = self.starting_image)

        # Spawn the boss at the middle of the tile, with the bottom of the boss being at the bottom of the tile
        # Note: Do this before inheriting the AI class so that the rect positions are the same
        self.rect.midbottom = (x, y)

        # Inherit from the AI class
        AI.__init__(self, max_health = SikaDeerBoss.maximum_health, knockback_damage = SikaDeerBoss.knockback_damage, suvat_dict = SikaDeerBoss.suvat_dict)

        """ List of "hidden" added attributes
        self.delta_time
        self.camera_position
        self.players_position
        self.neighbouring_tiles_dict
        self.camera_shake_events_list # A list of the camera shake events used to add the "Stomp" camera shake effect
        """

        # Stomp controller used to create stomp nodes and update each individual stomp node
        self.stomp_controller = StompController(scale_multiplier = scale_multiplier)

        # The current action that the boss is performing
        self.current_action = "Chase"

        # To delay actions right after spawning, set the cooldown timer to a desired amount of time and add it to this list, so that the cooldown timers can be updated
        self.previous_actions_dict = {
                                    "Stomp": None, 
                                    "Target": None
                                    }
        
        # A dictionary containing information relating to the behaviour of the Sika deer boss
        self.behaviour_patterns_dict = {

                                    # Additional actions that the boss can perform, other than chase

                                    "Stomp": {
                                            # Note: Changing the number of stomps and the duration will affect how fast each wave of stomps is spawned
                                            "NumberOfStomps": 12,
                                            "Duration": 3000, 
                                            "DurationTimer": None, # Timer used to check if the attack is over

                                            "Cooldown": 3000, #9000, 
                                            "CooldownTimer": 3000, #9000, # Delayed cooldown to when the boss can first use the stomp attack

                                            # The variation of the stomp for one entire stomp attack
                                            "StompAttackVariation": 0,

                                             },

                                    "Chase": { 
                                            "FullAnimationDuration": 700
                                              
                                    
                                              },

                                    # Target and charge
                                    "Target": { 
                                            "Duration": 2200,
                                            "DurationTimer": None,
                                            "CooldownTimer": 7500,  # This will be set to be the charge cooldown after the attack has completed (Change this number if you want to delay when the boss can first charge attack)
                                            "Cooldown": 50000, # Set to random number, this will be changed once the charge attack has finished

                                            # Animations
                                            "FullAnimationDuration": 400,
                                            "OriginalAnimationDuration": 400, # Used to reset the full animation duration back to the original amount (this is for the effect of increasing the frame speed the closer the sika deer boss is to charging at the player)
                                            "AnimationListLength": len(SikaDeerBoss.ImagesDict["Target"]["Up"]) # Used to calculate the new time between animation frames 
                                            },

                                    "Charge": {

                                            "Duration": 2000, # The maximum duration that the boss will charge for
                                            "DurationTimer": None,
                                            "Cooldown": 9000,
                                            "CooldownTimer": None,
                                            "FullAnimationDuration": 150,
                                            
                                            "ChargeDirection": None,
                                            "ChargeAngle": None,
                                            "PlayerPosAtChargeTime": None,
                                            "EnterStunnedStateBoolean": False, # A boolean value that represents whether the boss has collided with the player during the charge attack"

                                            # Movement (Keep the time values to be less than the full charge duration)
                                            "ChargeDistanceTravelled": 8 * TILE_SIZE, # 10 * TILE_SIZE
                                            "HorizontalTimeToTravelDistanceAtFinalVelocity": 0.15, 
                                            "VerticalTimeToTravelDistanceAtFinalVelocity": 0.15, 
                                            "HorizontalTimeToReachFinalVelocity": 0.1, #0.25,
                                            "VerticalTimeToReachFinalVelocity": 0.1, #0.25,

                                                },
                                    # Stunned
                                    "Stunned": {
                                            "Duration": 4000,
                                            "DurationTimer": None,
                                            "FullAnimationDuration": 1000,
                                            "StunnedDamageAmount": 350,
                                            "PlayerDamageMultiplierWhenStunned": 2
                                            },

                                    "Death": {
                                            "Images": None

                                            }
                                    }
        # ----------------------------------------------------------------------------------
        # Blinking effect variables

        # The angle change over time (Keep this value low in comparison to the duration time)
        self.behaviour_patterns_dict["Target"]["BlinkingVisualEffectAngleChange"] = (self.behaviour_patterns_dict["Target"]["Duration"] / 100)

        # The starting angle time gradient (this will continue changing inside the Game class as the time decreases)
        self.behaviour_patterns_dict["Target"]["BlinkingVisualEffectAngleTimeGradient"] = (self.behaviour_patterns_dict["Target"]["BlinkingVisualEffectAngleChange"] - 0) / (self.behaviour_patterns_dict["Target"]["Duration"] / 1000)
        
        # The initial sin angle should be 0
        self.behaviour_patterns_dict["Target"]["BlinkingVisualEffectCurrentSinAngle"] = 0

        # ----------------------------------------------------------------------------------
        # Declare the animation attributes
        self.declare_animation_attributes()

    # ----------------------------------------------------------------------------------
    # Animations

    def declare_animation_attributes(self):

        # Declares the animation attributes

        # Set the animation index as 0
        self.animation_index = 0         

        # --------------------------
        # Stomping 

        # Each full cycle of the stomp animation has 2 stomps 
        # Note: (number_of_stomps + 1) because the first animation frame does not count as a stomp, so add another one
        number_of_animation_cycles = (self.behaviour_patterns_dict["Stomp"]["NumberOfStomps"] + 1) / 2

        # The time between each frame should be how long the stomp attack lasts, divided by the total number of animation frames, depending on how many cycles there are 
        self.behaviour_patterns_dict["Stomp"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Stomp"]["Duration"] / (len(SikaDeerBoss.ImagesDict["Stomp"]) * number_of_animation_cycles)

        # Set the animation frame timer to start at 0, this is so that the first animation frame does not count as a stomp
        self.behaviour_patterns_dict["Stomp"]["AnimationFrameTimer"] = 0

        # --------------------------
        # Chasing

        # The time between each frame should be how long each chase animation cycle should last, divided by the total number of animation frames
        self.behaviour_patterns_dict["Chase"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Chase"]["FullAnimationDuration"] / (len(SikaDeerBoss.ImagesDict["Chase"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Chase"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Chase"]["TimeBetweenAnimFrames"]

        # --------------------------
        # Targeting

        # Note: All directions have the same number of animation frames

        # The time between each frame should be how long each target animation cycle should last, divided by the total number of animation frames
        self.behaviour_patterns_dict["Target"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Target"]["FullAnimationDuration"] / (len(SikaDeerBoss.ImagesDict["Target"]["Up"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Target"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Target"]["TimeBetweenAnimFrames"]

        # --------------------------
        # Charging
        # Note: All directions have the same number of animation frames

        # The time between each frame should be how long the charge attack animation lasts, divided by the total number of animation frames
        self.behaviour_patterns_dict["Charge"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Charge"]["FullAnimationDuration"] / (len(SikaDeerBoss.ImagesDict["Charge"]["Up"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Charge"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Charge"]["TimeBetweenAnimFrames"]

        # --------------------------
        # Stunned

        # The time between each frame should be how long the stunned animation lasts, divided by the total number of animation frames
        self.behaviour_patterns_dict["Stunned"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Stunned"]["FullAnimationDuration"] / (len(SikaDeerBoss.ImagesDict["Stunned"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Stunned"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Stunned"]["TimeBetweenAnimFrames"]

    def play_animations(self):

        # -----------------------------------
        # Set image

        # If the boss is alive
        if self.current_action != "Death":

            # If the current action is not "Target" and not "Charge"
            if self.current_action != "Target" and self.current_action != "Charge":
                # The current animation list
                current_animation_list = SikaDeerBoss.ImagesDict[self.current_action]
                # The current animation image
                current_animation_image = current_animation_list[self.animation_index]
            
            # If the current action is "Target" or "Charge"
            elif self.current_action == "Target" or self.current_action == "Charge":
                
                # Only do this if the current action is "Target"
                if self.current_action == "Target":
                    # Find the player (To continuously update the look angle)
                    self.find_player(current_position = self.rect.center, player_position = self.players_position, delta_time = self.delta_time)

                # Find the current look direction
                current_look_direction = self.find_look_direction()

                # The current animation list
                current_animation_list = SikaDeerBoss.ImagesDict[self.current_action][current_look_direction]

                # The current animation image
                current_animation_image = current_animation_list[self.animation_index]
            
            # If the boss has been damaged (red and white version)
            if self.extra_information_dict["DamagedFlashEffectTimer"] != None:
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

        # -----------------------------------
        # Updating animation

        # Find which action is being performed and playing their animation 
        match self.current_action:

            # Chase, Target, Stunned
            case _ if self.current_action == "Chase" or self.current_action == "Target" or self.current_action == "Stunned" or self.current_action == "Stomp":

                # Loop the animation continuously
                self.animation_index, self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] = simple_loop_animation(
                                                                                                                                        animation_index = self.animation_index,
                                                                                                                                        animation_list = current_animation_list,
                                                                                                                                        animation_frame_timer = self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"],
                                                                                                                                        time_between_anim_frames = self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]
                                                                                                                                        )
            # Charge, Death
            case _ if self.current_action == "Charge" or self.current_action == "Death":
                
                # Play the animation once to the end
                self.animation_index, self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] = simple_play_animation_once(
                                                                                                                                            animation_index = self.animation_index,
                                                                                                                                            animation_list = current_animation_list,
                                                                                                                                            animation_frame_timer = self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"],
                                                                                                                                            time_between_anim_frames = self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]
                                                                                                                                            )

        # -----------------------------------
        # Updating timers
        
        # Decrease the animation frame timers
        self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] -= 1000 * self.delta_time

        # Update damage flash effect timer
        self.update_damage_flash_effect_timer()

    # ----------------------------------------------------------------------------------
    # Timer updating

    def update_duration_timers(self):

        # Updates the duration timer of the current action 
        # If the duration timer is over, the action is added to the previous actions list so that their cooldown timer can be updated
        
        # If the current action is not "Chase" (Chase does not have a duration timer)
        if self.current_action != "Chase":
            
            # Decrease the timer
            self.behaviour_patterns_dict[self.current_action]["DurationTimer"] -= 1000 * self.delta_time
            
            # If the current action's duration timer has finished counting down
            if self.behaviour_patterns_dict[self.current_action]["DurationTimer"] <= 0:
                # Reset the duration timer back to None
                self.behaviour_patterns_dict[self.current_action]["DurationTimer"] = None

                # Reset the animation index
                self.animation_index = 0

                # If the current action is not "Stunned" ("Stunned" does not have a cooldown timer)
                if self.current_action != "Stunned":
                    # Set the cooldown timer of the previous action to start counting down
                    self.behaviour_patterns_dict[self.current_action]["CooldownTimer"] = self.behaviour_patterns_dict[self.current_action]["Cooldown"]

                    # Add the current action to the previous actions dict so that its cooldown timer can count down
                    self.previous_actions_dict[self.current_action] = None

                # If the current action is "Target"
                if self.current_action == "Target":

                    # Set the "Charge" duration timer to start counting down
                    self.behaviour_patterns_dict["Charge"]["DurationTimer"] = self.behaviour_patterns_dict["Charge"]["Duration"]

                    # Set the current charge direction (so that the boss cannot change direction whilst charging)
                    self.behaviour_patterns_dict["Charge"]["ChargeDirection"] = self.find_look_direction()

                    # Store the current charge angle (for calculations for movement)
                    self.behaviour_patterns_dict["Charge"]["ChargeAngle"] = self.movement_information_dict["Angle"]

                    # Store the position of the player at this point in time (used to draw red guidelines)
                    self.behaviour_patterns_dict["Charge"]["PlayerPosAtChargeTime"] = self.players_position

                    # Reset the horizontal and vertical velocity (V, A and S are updated during the charge attack)
                    self.movement_information_dict["HorizontalSuvatU"] = 0
                    self.movement_information_dict["VerticalSuvatU"] = 0
                            
                    # Set the current action to Charge
                    self.current_action = "Charge"

                # If the current action is "Charge
                elif self.current_action == "Charge":

                    # Set the no action timer to start counting down
                    self.extra_information_dict["NoActionTimer"] = self.extra_information_dict["NoActionTime"]

                    # Set the "Target" cooldown timer to be the same as the "Charge" cooldown timer (This is because the attack sequence starts with "Target" and then "Charge")
                    self.behaviour_patterns_dict["Target"]["CooldownTimer"] = self.behaviour_patterns_dict["Charge"]["CooldownTimer"]

                    # Reset the current charge direction back to None
                    self.behaviour_patterns_dict["Charge"]["ChargeDirection"] = None

                    # If "EnterStunnedStateBoolean" was set to True, i.e. the boss collided a building tile
                    if self.behaviour_patterns_dict["Charge"]["EnterStunnedStateBoolean"] == True:
                        # Set the current action to "Stunned"
                        self.current_action = "Stunned"
                        # Set "EnterStunnedStateBoolean" back to False
                        self.behaviour_patterns_dict["Charge"]["EnterStunnedStateBoolean"] = False
                    
                    # If "EnterStunnedStateBoolean" is set to False, i.e. the boss did not collide with a building tile
                    elif self.behaviour_patterns_dict["Charge"]["EnterStunnedStateBoolean"] == False:
                        # Set the current action back to Chase
                        self.current_action = "Chase"

                # If the current action is to "Stomp"
                elif self.current_action == "Stomp":

                    # Set the no action timer to start counting down
                    self.extra_information_dict["NoActionTimer"] = self.extra_information_dict["NoActionTime"]

                    # Set the current action back to Chase
                    self.current_action = "Chase"
                
                # If the current action is "Stunned"
                elif self.current_action == "Stunned":
                    # Set the current action back to Chase
                    self.current_action = "Chase"

    # ----------------------------------------------------------------------------------
    # Gameplay

    def update_and_draw_stomp_attacks(self):
        
        # If there are any stomp attack nodes inside the stomp nodes
        if len(StompController.nodes_group) > 0:

            # For each stomp attack in the group
            for stomp_attack_node in StompController.nodes_group:
                
                # ---------------------------------------------------------------------------
                # Drawing the stomp attack node
                
                # ---------------------------------
                # Assigning the colours

                # If the stomp attack node has not been reflected
                if stomp_attack_node.reflected == False:
                    
                    # Set the circle colours to be the default colours
                    circle_colours = ((111, 26, 182), (61, 23, 102), ((255, 0, 50)))

                # If the stomp attack node has not been reflected
                elif stomp_attack_node.reflected == True:
                    
                     # Set the circle colours to be the reflected colours
                    circle_colours = (
                        (min(111 + stomp_attack_node.reflected_additive_colour[1], 255), 26, 182), 
                        (min(61 + stomp_attack_node.reflected_additive_colour[1], 255), 23, 102), 
                        (min(255 + stomp_attack_node.reflected_additive_colour[1], 255), 0, 50)
                        ) 

                    # Change the value of the reflected colour
                    stomp_attack_node.change_reflected_colour_value(delta_time = self.delta_time)

                # ---------------------------------
                # Drawing the circles

                # First circle (Lightest colour)
                pygame_draw_circle(surface = self.surface, color = circle_colours[0], center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius, width = 0)

                # Outline (Darkest colour)
                pygame_draw_circle(surface = self.surface, color = 	circle_colours[1], center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius, width = int(stomp_attack_node.radius / 3))

                # Second circle (Middle colour)
                pygame_draw_circle(surface = self.surface, color = circle_colours[2], center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius * (0.45), width = 0)
                

                # # The center of the rectangle is at the position calculated when the node was created
                # pygame_draw_rect(surface = self.surface, color = "red", rect = (stomp_attack_node.rect.x - self.camera_position[0], stomp_attack_node.rect.y - self.camera_position[1], stomp_attack_node.rect.width, stomp_attack_node.rect.height), width = 1)

                # ---------------------------------------------------------------------------
                # Other

                # Move the stomp attack node
                stomp_attack_node.move(delta_time = self.delta_time)

                # If the current radius of the stomp attack node is less than the maximum node radius set
                if stomp_attack_node.radius < self.stomp_controller.maximum_node_radius:
                    # Increase the radius of the current rect
                    stomp_attack_node.increase_size(delta_time = self.delta_time)

    def stomp_attack(self):

        # Performs the stomp attack

        # If there are no stomp attack nodes (i.e. the start of the stomp attack)
        if len(StompController.nodes_group) == 0:
            # Choose a random variation of the stomp attack
            self.extra_information_dict["StompAttackVariation"] = random_choice((0, 1, 1, 2))
        

        # Create stomp attack nodes
        self.stomp_controller.create_stomp_nodes(
                                                center_of_boss_position = (self.rect.centerx, self.rect.centery), 
                                                desired_number_of_nodes = 12, 
                                                attack_variation = self.extra_information_dict["StompAttackVariation"]
                                                )
        # Set the new last animation index
        self.stomp_controller.last_animation_index = self.animation_index

        # Add a stomp camera shake event to the camera shake events list
        self.camera_shake_events_list.append("Stomp")

    def chase_player(self):

        # Finds and chases the player

        # Find the player (for angles and movement)
        self.find_player(current_position = self.rect.center, player_position = self.players_position, delta_time = self.delta_time)

        # Move the boss
        self.move()

    def decide_action(self):

        # The main "brain" of the deer boss, which will decide on what action to perform

        # "Chase"
        if self.current_action == "Chase":

            # Create a list of all the actions that the AI can currently perform, if the action's cooldown timer is None
            action_list = [action for action in self.behaviour_patterns_dict.keys() if (action == "Stomp" or action == "Target") and self.behaviour_patterns_dict[action]["CooldownTimer"] == None]

            # If there are any possible actions that the boss can perform (other than "Chase") and the boss has not performed an action recently
            if len(action_list) > 0 and self.extra_information_dict["NoActionTimer"] == None:

                # Reset the animation index whenever we change the action
                self.animation_index = 0

                # Choose a random action from the possible actions the boss can perform and set it as the current action
                self.current_action = random_choice(action_list)

                # If the current action that was chosen was "Target", and target duration timer has not been set to start counting down yet
                if self.current_action == "Target" and self.behaviour_patterns_dict["Target"]["DurationTimer"] == None:
                    # Set the duration timer to start counting down
                    self.behaviour_patterns_dict["Target"]["DurationTimer"] = self.behaviour_patterns_dict["Target"]["Duration"] 

                # If the current action is to "Stomp"
                elif self.current_action == "Stomp":
                    # Set the duration timer to start counting down
                    self.behaviour_patterns_dict[self.current_action]["DurationTimer"] = self.behaviour_patterns_dict["Stomp"]["Duration"]

                    # Reset the movement acceleration
                    self.reset_movement_acceleration(horizontal_reset = True, vertical_reset = True)

            # If there are no possible actions that the boss can perform or the boss has performed an action recently
            elif len(action_list) == 0 or self.extra_information_dict["NoActionTimer"] != None: 
                # Continue chasing the player
                self.chase_player()
        
        # "Stomp"
        elif self.current_action == "Stomp":

            # If the stomp attack has not been completed and the stomp has already been completed for this animation index
            if self.behaviour_patterns_dict[self.current_action]["DurationTimer"] > 0 and self.stomp_controller.last_animation_index != self.animation_index:

                """ If this is one of the stomp keyframes inside the boss stomp animation (except from when the stomp attack just started)"""
                if (self.animation_index == 0 and self.behaviour_patterns_dict[self.current_action]["DurationTimer"] != self.behaviour_patterns_dict[self.current_action]["Duration"]) \
                    or self.animation_index == 5:
                    # Start the stomp attack
                    self.stomp_attack()

        # "Charge"
        elif self.current_action == "Charge":
            # Perform the charge attack 
            self.charge_attack()

    def charge_attack(self):

        # Responsible for changing the movement speed of the boss so that the charge attack is faster than the default movement speed
        # Note: These will be reset back to the default values when the current action is set back to "Chase"


        # ------------------------------------------------------------------------------
        # Movement  

        # ----------------------------------------
        # Horizontal

        # Set the horizontal distance travelled based on the current angle that the player is to the AI
        # print(self.behaviour_patterns_dict["Charge"]["ChargeDirection"], self.movement_information_dict["HorizontalSuvatU"])
        horizontal_distance_travelled_at_final_velocity = (self.behaviour_patterns_dict["Charge"]["ChargeDistanceTravelled"] * cos(self.behaviour_patterns_dict["Charge"]["ChargeAngle"]))

        # Equation = (2s - at^2) / 2t
        self.movement_information_dict["HorizontalSuvatV"] = (2 * horizontal_distance_travelled_at_final_velocity) / (2 * self.behaviour_patterns_dict["Charge"]["HorizontalTimeToTravelDistanceAtFinalVelocity"])
        # Set the current acceleration of the AI depending on the current velocity of the player
        self.movement_information_dict["HorizontalSuvatA"] = (self.movement_information_dict["HorizontalSuvatV"] - self.movement_information_dict["HorizontalSuvatU"]) / self.behaviour_patterns_dict["Charge"]["HorizontalTimeToReachFinalVelocity"]
        

        # ----------------------------------------
        # Vertical

        # Set the vertical distance travelled based on the current angle that the player is to the AI
        vertical_distance_travelled_at_final_velocity = (self.behaviour_patterns_dict["Charge"]["ChargeDistanceTravelled"] * sin(self.behaviour_patterns_dict["Charge"]["ChargeAngle"]))

        # Equation = (2s - at^2) / 2t
        self.movement_information_dict["VerticalSuvatV"] = (2 * vertical_distance_travelled_at_final_velocity) / (2 * self.behaviour_patterns_dict["Charge"]["VerticalTimeToTravelDistanceAtFinalVelocity"])

        # Set the current acceleration of the AI depending on the current velocity of the player
        self.movement_information_dict["VerticalSuvatA"] = (self.movement_information_dict["VerticalSuvatV"] - self.movement_information_dict["VerticalSuvatU"]) / self.behaviour_patterns_dict["Charge"]["VerticalTimeToReachFinalVelocity"]

        # Move the boss
        self.move()

    def run(self):
        
        # Update and draw the stomp attacks (always do this so that even when the boss is dead, these are still updated)
        self.update_and_draw_stomp_attacks()

        # If the boss is not alive
        if self.current_action == "Death":
            # Draw a shadow ellipse underneath the boss
            pygame_draw_ellipse(
                surface = self.surface, 
                color = (20, 20, 20), 
                rect = ((self.rect.centerx - self.camera_position[0]) - 20, 
                ((self.rect.centery + 20) - self.camera_position[1]) - 20, 40, 40), 
                width = 0)

        # Draw the boss 
        # Note: Additional positions to center the image (this is because the animation images can vary in size)
        self.draw(
            surface = self.surface, 
            x = (self.rect.x - ((self.image.get_width() / 2)  - (self.rect.width / 2))) - self.camera_position[0], 
            y = (self.rect.y - ((self.image.get_height() / 2) - (self.rect.height / 2))) - self.camera_position[1]
                )

        # pygame_draw_rect(self.surface, "green", pygame_Rect(self.rect.x - self.camera_position[0], self.rect.y - self.camera_position[1], self.rect.width, self.rect.height), 1)
        # pygame_draw_line(self.surface, "white", (0 - self.camera_position[0], self.rect.centery - self.camera_position[1]), (self.surface.get_width() - self.camera_position[0], self.rect.centery - self.camera_position[1]))
        # pygame_draw_line(self.surface, "white", (self.rect.centerx - self.camera_position[0], 0 - self.camera_position[1]), (self.rect.centerx - self.camera_position[0], self.surface.get_height() - self.camera_position[1]))

        # If the boss has spawned and the camera panning has been completed
        if self.extra_information_dict["CanStartOperating"] == True:
            
            # Decide the action that the boss should perform
            self.decide_action()
            
            # Check if the boss' health is less than 0
            if self.extra_information_dict["CurrentHealth"] <= 0:
                
                # If current action has not been set to "Death" the boss does not have a death animation images list yet
                if self.current_action != "Death" or self.behaviour_patterns_dict["Death"]["Images"]  == None:

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

            # Only if the boss is alive, should the timers be updated
            if self.extra_information_dict["CurrentHealth"] > 0:
                # Update the duration timers
                self.update_duration_timers()

                # Update the cooldown timers
                self.update_cooldown_timers()

                # Update the knockback collision idle timer
                self.update_knockback_collision_idle_timer()

                # If the current action is not "Stunned"
                if self.current_action != "Stunned":
                    # Update the no action timer (meaning the boss cannot perform any other actions other than chasing)
                    self.update_no_action_timer()

                # # TEMPORARY
                # for tile in self.neighbouring_tiles_dict.keys():
                #     pygame_draw_rect(self.surface, "white", (tile.rect.x - self.camera_position[0], tile.rect.y - self.camera_position[1], tile.rect.width, tile.rect.height))