from random import uniform as random_uniform

class Camera:
    
    def __init__(self, game):

        # Attribute that references the Game object
        self.game = game

        # Camera position
        self.position = 0
        # Camera modes
        self.mode = None # Can either be: Static, Follow, Pan
        
        # A dictionary containing information about camera panning
        """ The panning is as follows:
        - Pans from the player to the boss
        - Locks on the boss for a short period of time
        - Pans from the boss back to the player
        - Locks on the player for a short period of time
        - Resets the camera mode back to "Follow", allowing the player to play
        
        """
        self.camera_pan_information_dict = {
                                            # The rate of change in the distance of the camera over time
                                            "PanHorizontalDistanceTimeGradient": None,
                                            "PanVerticalDistanceTimeGradient": None,                              

                                            # Time it takes to pan the camera from the current camera position to the new position
                                            "PanTime": 1500, # This must be less than the spawning timer of the boss"
                                            "PanTimer": None,
                                            
                                            # The time the camera locks onto the boss for after panning from the player to the boss
                                            "BossPanLockTime": 2500,
                                            "BossPanLockTimer": None,
                                            
                                            # The time the camera locks onto the player for after panning from the boss back to the player
                                            "PlayerPanLockTime": 1000, 
                                            "PlayerPanLockTimer": None,

                                            # Boolean variable used to track whether the camera has finished panning to the boss, locking in for a short period of time and started panning back to the player
                                            "BossPanComplete": False, 

                                            # Used to store the changing camera position for floating point accuracy
                                            "NewCameraPositionX": None,
                                            "NewCameraPositionY": None,
                                            }

        # A dictionary containing information to do with the camera / screen shake
        self.camera_shake_info_dict = {
                                        "EventsList": [],

                                        # Timers
                                        "BossTileCollideTimer": None,
                                        "BossTileCollideTime": 800,

                                        "StompTimer": None,
                                        "StompTime": 100,
                                        
                                        "DiveBombTimer": None,
                                        "DiveBombTime": 500 

                                    }


    def set_mode(self, manual_camera_mode_setting = None):

        # Used to change the camera mode depending on the size of the tile map or changing the camera mode if a manual camera mode setting was passed in
        
        # If a manual camera mode setting has not been passed to this method
        if manual_camera_mode_setting == None:
            # If the width of the tile map is one room
            if self.game.last_tile_position[0] <= (self.game.scaled_surface.get_width() / 2):
                # Set the camera mode to "Static"
                self.mode = "Static"
            
            # If the width of the tile map is more than one room
            else:
                # Set the camera mode to "Follow"
                self.mode = "Follow"

        # If a manual camera mode setting has been passed to this method
        elif manual_camera_mode_setting != None:
            # Set the camera mode as the manual camera mode setting passed
            self.mode = manual_camera_mode_setting

    def update_position(self, delta_time, focus_subject_center_pos):   
        
        # Moves the camera's position depending on what mode the camera has been set as and according to who the focus subject is (i.e. the boss, the player, etc.)
        
        # If the camera mode is set to "Follow"
        if self.mode == "Follow":
            
            # --------------------------------------------------------------------------------------
            # Adjusting camera x position

            # If the player is in half the width of the scaled screen from the first tile in the tile map
            if 0 <= focus_subject_center_pos[0] <= (self.game.scaled_surface.get_width() / 2):
                # Don't move the camera
                camera_position_x = 0

            # If the player is in between half of the size of the scaled screen width from the first tile in the tile map and half the width of the scaled screen from the last tile in the tile map
            elif 0 + (self.game.scaled_surface.get_width() / 2) < focus_subject_center_pos[0] < self.game.last_tile_position[0] - (self.game.scaled_surface.get_width() / 2):
                # Set the camera to always follow the player
                camera_position_x = focus_subject_center_pos[0] - (self.game.scaled_surface.get_width() / 2)

            # If the player is half the scaled screen width away from the last tile in the tile maps
            elif focus_subject_center_pos[0] >= self.game.last_tile_position[0] - (self.game.scaled_surface.get_width() / 2):
                # Set the camera to stop moving and be locked at half the size of the scaled screen width from the last tile in the tile map
                camera_position_x = self.game.last_tile_position[0] - self.game.scaled_surface.get_width() 

            # --------------------------------------------------------------------------------------
            # Adjusting camera y position

            # If the player is in half the height of the scaled screen from the first tile in the tile map
            if 0 <= focus_subject_center_pos[1] <= (self.game.scaled_surface.get_height() / 2):
                # Don't move the camera
                camera_position_y = 0

            # If the player is in between half of the size of the scaled screen height from the first tile in the tile map and half the width of the scaled screen from the last tile in the tile map
            elif 0 + (self.game.scaled_surface.get_height() / 2) <= focus_subject_center_pos[1] <= self.game.last_tile_position[1] - (self.game.scaled_surface.get_height() / 2):
                # Set the camera to always follow the player
                camera_position_y = focus_subject_center_pos[1] - (self.game.scaled_surface.get_height() / 2)

            # If the player is half the scaled screen width away from the last tile in the tile maps
            elif focus_subject_center_pos[1] >= self.game.last_tile_position[1] - (self.game.scaled_surface.get_height() / 2):
                # Set the camera to stop moving and be locked at half the size of the scaled screen width from the last tile in the tile map
                camera_position_y = self.game.last_tile_position[1] - self.game.scaled_surface.get_height()     

        # If the camera mode is set to "Static"
        elif self.mode == "Static":
            # The camera's x position will always be at 0
            camera_position_x = 0

        # If the camera mode is set to "Pan" (will pan towards a specific location)
        elif self.mode == "Pan":

            # If there has been a timer set for pan timer
            if self.camera_pan_information_dict["PanTimer"] != None:

                # ------------------------------------------------------------------------------
                # Moving the camera
                
                # Increase the new camera position x and y (Floating point accuracy)
                self.camera_pan_information_dict["NewCameraPositionX"] += self.camera_pan_information_dict["PanHorizontalDistanceTimeGradient"] * delta_time
                self.camera_pan_information_dict["NewCameraPositionY"] += self.camera_pan_information_dict["PanVerticalDistanceTimeGradient"] * delta_time

                # Set the camera position as the rounded values
                camera_position_x = round(self.camera_pan_information_dict["NewCameraPositionX"])
                camera_position_y = round(self.camera_pan_information_dict["NewCameraPositionY"])

                # ------------------------------------------------------------------------------
                # Updating the pan timer

                # If the timer has not finished counting
                if self.camera_pan_information_dict["PanTimer"] > 0:
                    # Decrease the timer
                    self.camera_pan_information_dict["PanTimer"] -= 1000 * delta_time
                
                # If the timer has finished counting
                if self.camera_pan_information_dict["PanTimer"] <= 0:
                    # Set the pan timer back to None
                    self.camera_pan_information_dict["PanTimer"] = None

                    # If the camera has finished going from the boss to the player but the camera has not locked onto the player for a short period of time yet
                    if self.camera_pan_information_dict["BossPanComplete"] == True and self.camera_pan_information_dict["PlayerPanLockTimer"] == None:
                        # Set the camera to lock onto the player for a short period of time
                        self.camera_pan_information_dict["PlayerPanLockTimer"] = self.camera_pan_information_dict["PlayerPanLockTime"] 

            # If there has not been a timer set for pan timer
            elif self.camera_pan_information_dict["PanTimer"] == None:

                # Keep the camera the same
                camera_position_x = round(self.camera_pan_information_dict["NewCameraPositionX"])
                camera_position_y = round(self.camera_pan_information_dict["NewCameraPositionY"])

                # -------------------------------------
                # If the boss has finished spawning and and the camera has finished panning to the boss but still needs to lock in for a short period of time

                if self.game.bosses_dict["TimeToSpawnTimer"] == None and self.camera_pan_information_dict["BossPanLockTimer"] == None and self.camera_pan_information_dict["PlayerPanLockTimer"] == None:
                    # Set the boss pan lock timer to start
                    self.camera_pan_information_dict["BossPanLockTimer"] = self.camera_pan_information_dict["BossPanLockTime"]

                # ------------------------------------------------------------------------------
                # Updating the boss pan lock timer

                # If a boss pan lock timer has been set (Locks on the boss for short period of time)
                if self.camera_pan_information_dict["BossPanLockTimer"] != None:

                    # If the timer has not finished counting
                    if self.camera_pan_information_dict["BossPanLockTimer"] > 0:
                        # Decrease the timer
                        self.camera_pan_information_dict["BossPanLockTimer"]-= 1000 * delta_time
                    
                    # If the timer has finished counting
                    if self.camera_pan_information_dict["BossPanLockTimer"] <= 0:
                        # Set the timer back to None
                        self.camera_pan_information_dict["BossPanLockTimer"] = None

                        # If the player is alive
                        if self.game.player.player_gameplay_info_dict["CurrentHealth"] > 0:

                            # -----------------------------------------
                            # Set the camera to pan back to the player

                            # Invert the horizontal and vertical distance time gradients so that it pans back to the player
                            self.camera_pan_information_dict["PanHorizontalDistanceTimeGradient"] *= -1
                            self.camera_pan_information_dict["PanVerticalDistanceTimeGradient"] *= -1

                            # Set the camera to pan back to the player (start the pan timer to count down)
                            self.camera_pan_information_dict["PanTimer"] = self.camera_pan_information_dict["PanTime"] 

                            # Set the boss pan to be complete so that once the pan timer has finished panning back to the player.
                            self.camera_pan_information_dict["BossPanComplete"] = True
                        
                        # If the player is not alive
                        elif self.game.player.player_gameplay_info_dict["CurrentHealth"] <= 0:
                            # Instead of panning back to the player, end the game (This will start the transition to the restart menu)
                            self.game.game_over = True

                            # Exit the method
                            return None

                # -------------------------------------
                # Updating the player pan lock timer

                # If the camera has finished panning back to the player but still needs to lock in for a short period of time (THE FINAL STEP)

                # If a timer has been set to lock on the player for a short period of time
                if self.camera_pan_information_dict["PlayerPanLockTimer"] != None:

                    # If the timer has not finished counting
                    if self.camera_pan_information_dict["PlayerPanLockTimer"] > 0:
                        # Decrease the timer
                        self.camera_pan_information_dict["PlayerPanLockTimer"] -= 1000 * delta_time
                    
                    # If the timer has finished counting
                    if self.camera_pan_information_dict["PlayerPanLockTimer"] <= 0:

                        # Set the timer back to None
                        self.camera_pan_information_dict["PlayerPanLockTimer"] = None

                        # Set the camera mode back to Follow
                        self.set_mode("Follow")

                        # Allow the boss to start operating (i.e, moving and performing actions)
                        self.game.boss_group.sprite.extra_information_dict["CanStartOperating"] = True

                        # Allow the player to start operating (i.e, moving and performing actions)
                        self.game.player.player_gameplay_info_dict["CanStartOperating"] = True

                        # Reset the boss pan complete variable
                        self.camera_pan_information_dict["BossPanComplete"] = False

        # --------------------------------------------------------------------------------------------------------------
        # Update the camera position
        """
        - The camera's x position:
            - Starts at 0 until the focus subject reaches half the size of the scaled screen width
            - Once the focus subject reaches the center of the screen, then the camera will always follow the focus subject
            - Until the focus subject reaches half the size of the scaled screen width from the last tile in the tile map

        - The camera's y position:
            - Starts at 0 until the focus subject reaches half the size of the scaled screen height
            - Once the focus subject reaches the center of the screen, then the camera will always follow the focus subject
            - Until the focus subject reaches half the size of the scaled screen height from the last tile in the tile map
        """

        try:
            # Assign the camera position
            self.position = [camera_position_x, camera_position_y]

        except:
            self.position = [0, camera_position_y]


        # Perform screen / camera shake if the conditions are met
        self.position = self.shake_camera(camera_position_to_change = self.position, delta_time = delta_time)

        # Update the player's camera position attribute so that tile rects are correctly aligned
        self.game.player.camera_position = self.position

    def update_focus_subject(self):
        
        # If a boss has not been created or if a boss has been created and has been spawned and the player is currently alive
        if (hasattr(self.game, "bosses_dict") == False or (hasattr(self.game, "bosses_dict") == True and self.game.bosses_dict["TimeToSpawnTimer"] == None)) and self.game.player.player_gameplay_info_dict["CurrentHealth"] > 0:
            # Return the center of the player (so that the camera follows the player)
            return (self.game.player.rect.centerx,  self.game.player.rect.centery)

        # If a boss has been created and is currently being spawned and the player is alive
        elif (hasattr(self.game, "bosses_dict") == True and self.game.bosses_dict["TimeToSpawnTimer"] != None) and self.mode != "Pan" and self.game.player.player_gameplay_info_dict["CurrentHealth"] > 0:

            # Set the camera mode as "Pan"
            self.set_mode(manual_camera_mode_setting = "Pan")
            
            # The position of the center of the screen, that the camera is following (i.e. the center of the camera)
            middle_camera_position = (self.position[0] + (self.game.scaled_surface.get_width() / 2), self.position[1] + (self.game.scaled_surface.get_height() / 2))
            
            # Calculate the horizontal and vertical distance time gradients for the panning movement
            # Note: TILE_SIZE / 2 so that the center of the camera is aligned with the center of the spawning tile
            self.camera_pan_information_dict["PanHorizontalDistanceTimeGradient"] = (self.game.bosses_dict["ValidSpawningPosition"].rect.centerx - middle_camera_position[0]) / (self.camera_pan_information_dict["PanTime"] / 1000)
            self.camera_pan_information_dict["PanVerticalDistanceTimeGradient"] = (self.game.bosses_dict["ValidSpawningPosition"].rect.centery - middle_camera_position[1]) / (self.camera_pan_information_dict["PanTime"] / 1000)

            # Set the new camera position X and Y to be the current camera position
            self.camera_pan_information_dict["NewCameraPositionX"] = self.position[0]
            self.camera_pan_information_dict["NewCameraPositionY"] = self.position[1]

            # Set the pan timer to start counting down
            self.camera_pan_information_dict["PanTimer"] = self.camera_pan_information_dict["PanTime"]

            # Don't allow the player to perform actions
            self.game.player.player_gameplay_info_dict["CanStartOperating"] = False

            # Return None (as nothing is required)
            return None
        
    def shake_camera(self, camera_position_to_change, delta_time):
        
        # Sets the timers for each camera shake event and performs the camera shake

        # If there are no camera shake events
        if len(self.camera_shake_info_dict["EventsList"]) == 0:
            # Return the original camera position
            return camera_position_to_change
    
        # If there are any camera shake events
        elif len(self.camera_shake_info_dict["EventsList"]) > 0:

            # ---------------------------------------------------------------------------------------
            # Setting the timers if there are any camera shake events and no timers have been activated
            
            # If all the camera shake events' timers are None (i.e. there is no camera shake to be performed currently)
            if self.camera_shake_info_dict["BossTileCollideTimer"] == None and self.camera_shake_info_dict["StompTimer"] == None and self.camera_shake_info_dict["DiveBombTimer"] == None:

                # Identify what this camera shake is for and start the timer for the screenshake
                match self.camera_shake_info_dict["EventsList"][0]:

                    # ------------------------------------------------------
                    # Sika Deer boss
                    
                    # The boss collided with a world tile or a building tile
                    case "BossTileCollide":
                        # Set the timer for the boss tile collide screen shake to start
                        self.camera_shake_info_dict["BossTileCollideTimer"] = self.camera_shake_info_dict["BossTileCollideTime"]

                    case "Stomp":
                        # Set the timer for the stomp screen shake to start
                        self.camera_shake_info_dict["StompTimer"] = self.camera_shake_info_dict["StompTime"]

                    case "DiveBomb":
                        # Set the timer for the divebomb screen shake to start
                        self.camera_shake_info_dict["DiveBombTimer"] = self.camera_shake_info_dict["DiveBombTime"]

            # ---------------------------------------------------------------------------------------
            # Performing the screen shake and removing events if their timer has finished counting down
        
            # Boss and tile timer:
            if self.camera_shake_info_dict["BossTileCollideTimer"] != None:
                
                # If the timer has not finished counting down
                if self.camera_shake_info_dict["BossTileCollideTimer"] > 0:

                    # Calculate a dampening factor which is dependent on how much time is left before we stop shaking the camera
                    dampening_factor = self.camera_shake_info_dict["BossTileCollideTimer"] / self.camera_shake_info_dict["BossTileCollideTime"]

                    # How impactful the screen shake should be
                    shake_magnitude = 3.5

                    # Set the camera shake for the x and y axis depending on the movement of the boss during the charge
                    # random_uniform is for a random float number between a given range
                    camera_shake_x = random_uniform(-abs(self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatS"] * shake_magnitude), abs(self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatS"] * shake_magnitude)) * dampening_factor
                    camera_shake_y = random_uniform(-abs(self.game.boss_group.sprite.movement_information_dict["VerticalSuvatS"] * shake_magnitude), abs(self.game.boss_group.sprite.movement_information_dict["VerticalSuvatS"] * shake_magnitude)) * dampening_factor

                    # Adjust the camera position by the camera shake amounts
                    camera_position_to_change[0] += camera_shake_x
                    camera_position_to_change[1] += camera_shake_y

                    # Decrease the timer
                    self.camera_shake_info_dict["BossTileCollideTimer"] -= 1000 * delta_time

                # If the timer has finished counting down 
                if self.camera_shake_info_dict["BossTileCollideTimer"] <= 0:
                    # Remove the event from the camera shake events list
                    self.camera_shake_info_dict["EventsList"].pop()

                    # Set the timer back to None
                    self.camera_shake_info_dict["BossTileCollideTimer"] = None

            # Deer boss stomp timer
            elif self.camera_shake_info_dict["StompTimer"] != None:
                
                # If the timer has not finished counting down
                if self.camera_shake_info_dict["StompTimer"] > 0:
                    # Adjust the camera position by the camera shake amounts
                    camera_position_to_change[0] += random_uniform(-1.75, 1.75)
                    camera_position_to_change[1] += random_uniform(-1.75, 1.75)

                    # Decrease the timer
                    self.camera_shake_info_dict["StompTimer"] -= 1000 * delta_time

                # If the timer has finished counting down 
                if self.camera_shake_info_dict["StompTimer"] <= 0:
                    # Remove the event from the camera shake events list
                    # random_uniform is for a random float number between a given range
                    self.camera_shake_info_dict["EventsList"].pop()

                    # Set the timer back to None
                    self.camera_shake_info_dict["StompTimer"] = None

            # Golden monkey dive bomb timer
            elif self.camera_shake_info_dict["DiveBombTimer"] != None:
                
                # If the timer has not finished counting down
                if self.camera_shake_info_dict["DiveBombTimer"] > 0:
                    # Adjust the camera position by the camera shake amounts
                    camera_position_to_change[0] += random_uniform(-12, 12) * (self.camera_shake_info_dict["DiveBombTimer"] / self.camera_shake_info_dict["DiveBombTime"])
                    camera_position_to_change[1] += random_uniform(-12, 12) * (self.camera_shake_info_dict["DiveBombTimer"] / self.camera_shake_info_dict["DiveBombTime"])

                    # Decrease the timer
                    self.camera_shake_info_dict["DiveBombTimer"] -= 1000 * delta_time

                # If the timer has finished counting down 
                if self.camera_shake_info_dict["DiveBombTimer"] <= 0:
                    # Remove the event from the camera shake events list
                    # random_uniform is for a random float number between a given range
                    self.camera_shake_info_dict["EventsList"].pop()

                    # Set the timer back to None
                    self.camera_shake_info_dict["DiveBombTimer"] = None

            # Return the new camera position after shaking
            return camera_position_to_change