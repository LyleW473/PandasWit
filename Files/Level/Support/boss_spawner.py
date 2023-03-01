from Global.settings import TILE_SIZE

from math import dist
from random import choice as random_choice
from os import listdir as os_listdir

from pygame.key import get_pressed as pygame_key_get_pressed
from pygame import K_f as pygame_K_f
from pygame.draw import rect as pygame_draw_rect
from pygame.draw import circle as pygame_draw_circle
from pygame.image import load as pygame_image_load
from pygame.transform import flip as pygame_transform_flip
from pygame.sprite import Group as pygame_sprite_Group

class BossSpawner:

    def __init__(self, game, game_ui, camera):

        # Attribute that references the Game object
        self.game = game

        # Attribute that references the GameUI object
        self.game_ui = game_ui

        # Attribute that references the Camera object
        self.camera = camera

    def look_for_input_to_spawn_boss(self):

        # Spawns the boss given the conditions are met

        """Conditions:
        - If the player is pressing the "f" key and the player has not tried to spawn a boss yet (i.e. this is the player's first session)
        - If the boss is currently spawning
        - If a boss dict has been created and the player has not tried to spawn a boss yet (i.e. the player has restarted the game)

        The final condition is that there shouldn't already be a boss
        """

        if (pygame_key_get_pressed()[pygame_K_f] and hasattr(self, "bosses_dict") == False) or \
            (pygame_key_get_pressed()[pygame_K_f] and hasattr(self, "bosses_dict") == True and self.bosses_dict["ValidSpawningPosition"] == None) or \
            hasattr(self, "bosses_dict") == True and self.bosses_dict["ValidSpawningPosition"] != None:

            # If a boss has not been spawned yet
            if len(self.game.boss_group) == 0:
                
                # If the first guide text in the list is the spawn boss text
                if len(self.game_ui.guide_text_list) > 0 and self.game_ui.guide_text_list[0] == self.game_ui.guide_text_dict["AllGuideTextMessages"]["SpawnBoss"][0]:
                    # Set the display time for the guide text (as it should be the spawn boss text) to 0, so that it stops showing
                    self.game_ui.guide_text_dict["DisplayTime"] = 0
            
                # Find a valid boss spawning position, and continue spawning them
                self.find_valid_boss_spawning_position()

            # If a boss has been spawned but was defeated by the player
            elif len(self.game.boss_group) == 1 and self.game.boss_group.sprite.extra_information_dict["CurrentHealth"] <= 0:
                # If there are still remaining bosses left
                if len(self.bosses_dict["RemainingBossesList"]) > 0:

                    # Empty the boss group
                    self.game.boss_group.empty()

                    # Choose the next boss in the list (The current one would have already been removed, when they were first spawned)
                    self.bosses_dict["CurrentBoss"] = self.bosses_dict["RemainingBossesList"][0]

                    # If the first guide text in the list is the spawn boss text
                    if len(self.game_ui.guide_text_list) > 0 and self.game_ui.guide_text_list[0] == self.game_ui.guide_text_dict["AllGuideTextMessages"]["SpawnBoss"][0]:
                        # Set the display time for the guide text (as it should be the spawn boss text) to 0, so that it stops showing
                        self.game_ui.guide_text_dict["DisplayTime"] = 0

    def find_valid_boss_spawning_position(self):
        
        # Method used to spawn the boss (Spawn the boss once the player presses the button at the top of the screen (add a button at the top of the screen that goes to the next boss))

        # If there isn't a dictionary holding information regarding bosses yet
        if hasattr(self, "bosses_dict") == False:
            
            # Temporary variables for the spawning effect
            number_of_tiles_for_checking = 4
            spawning_effect_counter = 1 # The starting spawning effect counter (e.g. if it was 1, then the spawning effect will start with 1 tile circling the valid spawning position)
            number_of_cycles = 8 # If the NumOfTilesForChecking was 3 and SpawningEffectCounter started at 0, then each cycle would consist of 4 changes
            time_to_spawn = self.camera.camera_pan_information_dict["PanTime"] * 2.25 # Set the time to spawn to be dependent on the time it takes for the camera to pan to the boss' spawning location (To keep everything synced)
            time_between_each_change = (time_to_spawn / number_of_cycles) / ((number_of_tiles_for_checking + 1) - spawning_effect_counter) # The time between each change
            
            # Create a dictionary to hold information regarding bosses
            self.bosses_dict = { 
                        "CurrentBoss": "SikaDeer",
                        "RemainingBossesList": ["SikaDeer", "GoldenMonkey"],

                        "NumOfTilesForChecking": number_of_tiles_for_checking, # The number of tiles to the left / right / up, down of the randomly chosen empty tile for the spawning position to be valid
                        "RandomSpawningPosition" : random_choice(list(self.game.empty_tiles_dict.keys())), # Choose a random spawning position
                        "ValidSpawningPosition": None, 
                        "SpawningPositionTilesList": [],
                        "TimeToSpawn": time_to_spawn, # The time for the boss to spawn
                        "TimeToSpawnTimer": None,

                        # Spawning effect keys and values
                        "SpawningEffectTimeBetweenEachChange": time_between_each_change,
                        "SpawningEffectOriginalTimeBetweenEachChange": time_between_each_change,
                        "SpawningEffectTimer": None,
                        "OriginalSpawningEffectCounter": spawning_effect_counter,
                        "SpawningEffectCounter": spawning_effect_counter, # If the NumOfTilesForChecking is 3, and SpawningEffectCounter is 0, then each cycle would consist of 4 changes

                                }

        # pygame_draw_circle(surface = self.game.scaled_surface, color = "green", center = (self.game.player.rect.centerx - self.camera.position[0], self.game.player.rect.centery - self.camera.position[1]), radius = 13 * TILE_SIZE, width = 2)
        # pygame_draw_circle(surface = self.game.scaled_surface, color = "blue", center = (self.game.player.rect.centerx - self.camera.position[0], self.game.player.rect.centery - self.camera.position[1]), radius = 25 * TILE_SIZE, width = 2)

        # If the distance between the player and the boss is not within a minimum and maximum range
        if ((13 * TILE_SIZE) <= dist(self.game.player.rect.center, self.bosses_dict["RandomSpawningPosition"].rect.center) <= (25 * TILE_SIZE)) == False:

            # Until we find a valid spawning position:
            for i in range(0, 200, 1):
                # Generate a new spawning position
                self.bosses_dict["RandomSpawningPosition"] = random_choice(list(self.game.empty_tiles_dict.keys()))

                # Check if the distance between the player and the boss is within a minimum and maximum range
                if ((13 * TILE_SIZE) <= dist(self.game.player.rect.center, self.bosses_dict["RandomSpawningPosition"].rect.center) <= (25 * TILE_SIZE)) == True:
                    # If it is, exit the loop
                    # Set the spawning boss variable to True
                    self.bosses_dict["SpawningBoss"] = True
                    break

        # If a valid spawning position has not been found
        if self.bosses_dict["ValidSpawningPosition"] == None:

            # For each empty tile inside the empty tiles dictionary
            for empty_tile in self.game.empty_tiles_dict.keys():
                
                # If the length of the tiles list is already has enough empty tiles to prove that it is a valid spawning location
                if len(self.bosses_dict["SpawningPositionTilesList"]) == (((self.bosses_dict["NumOfTilesForChecking"] * 2) + 1) ** 2) - 1:
                    # Exit the loop
                    break
                
                # Otherwise
                else:
                    # If the empty tile is not the same as the random empty tile and the tile is a certain distance from the selected random empty tile
                    if empty_tile != self.bosses_dict["RandomSpawningPosition"] and \
                        self.bosses_dict["RandomSpawningPosition"].rect.x  - (self.bosses_dict["NumOfTilesForChecking"] * TILE_SIZE) <= empty_tile.rect.x <= self.bosses_dict["RandomSpawningPosition"].rect.x + (self.bosses_dict["NumOfTilesForChecking"] * TILE_SIZE) and \
                                self.bosses_dict["RandomSpawningPosition"].rect.y - (self.bosses_dict["NumOfTilesForChecking"] * TILE_SIZE) <= empty_tile.rect.y <= self.bosses_dict["RandomSpawningPosition"].rect.y + (self.bosses_dict["NumOfTilesForChecking"] * TILE_SIZE):

                                # Add the empty tile to the spawning position tiles list
                                self.bosses_dict["SpawningPositionTilesList"].append(empty_tile)
            
            # If there is "enough space" for the boss to spawn 
            if len(self.bosses_dict["SpawningPositionTilesList"]) == (((self.bosses_dict["NumOfTilesForChecking"] * 2) + 1) ** 2) - 1:
                # Set the valid spawning position to be the random spawning position
                self.bosses_dict["ValidSpawningPosition"] = self.bosses_dict["RandomSpawningPosition"]
                # Set the boss spawn timer to start
                self.bosses_dict["TimeToSpawnTimer"] = self.bosses_dict["TimeToSpawn"]
                # Set the boss spawn effect timer to start
                self.bosses_dict["SpawningEffectTimer"] = self.bosses_dict["SpawningEffectTimeBetweenEachChange"]

            # If there is not "enough space" for the boss to spawn 
            elif len(self.bosses_dict["SpawningPositionTilesList"]) < (((self.bosses_dict["NumOfTilesForChecking"] * 2) + 1) ** 2) - 1:
                # Generate another random spawning position
                self.bosses_dict["RandomSpawningPosition"] =  random_choice(list(self.game.empty_tiles_dict.keys()))
                # Empty the spawning position tiles list
                self.bosses_dict["SpawningPositionTilesList"] = []

    def draw_spawning_effect_and_call_spawn_boss(self, delta_time):

        # Draws the spawning effect and spawns the boss once the time to spawn timer is complete

        # If a timer has been set to spawn the boss
        if self.bosses_dict["TimeToSpawnTimer"] != None:

            # For each empty tile in the spawning position tiles list
            for empty_tile in self.bosses_dict["SpawningPositionTilesList"]:

                    # If the empty tile is the required distance away from the selected spawning tile
                    if self.bosses_dict["ValidSpawningPosition"].rect.x - (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE) <= empty_tile.rect.x <= self.bosses_dict["ValidSpawningPosition"].rect.x + (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE) and \
                        self.bosses_dict["ValidSpawningPosition"].rect.y - (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE) <= empty_tile.rect.y <= self.bosses_dict["ValidSpawningPosition"].rect.y + (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE):
                        
                        # Highlight the empty tile
                        pygame_draw_rect(
                            surface = self.game.scaled_surface, 
                            color = (255, 0, 50), 
                            rect = (empty_tile.rect.x - self.camera.position[0], empty_tile.rect.y - self.camera.position[1], empty_tile.rect.width, empty_tile.rect.height), 
                            width = 1,
                            border_radius = 5
                            )
                        # Draw a circle which grows with the spawning effect counter (inner circle)
                        pygame_draw_circle(
                                        surface = self.game.scaled_surface, 
                                        color = (160, 160, 160),
                                        center = (self.bosses_dict["ValidSpawningPosition"].rect.centerx - self.camera.position[0], self.bosses_dict["ValidSpawningPosition"].rect.centery - self.camera.position[1]), 
                                        radius = ((self.bosses_dict["SpawningEffectCounter"] - 1) * TILE_SIZE),
                                        width = 1
                                        )

                        # Draw a circle which grows with the spawning effect counter (outer circle)
                        pygame_draw_circle(
                                        surface = self.game.scaled_surface, 
                                        color = (180, 180, 180), 
                                        center = (self.bosses_dict["ValidSpawningPosition"].rect.centerx - self.camera.position[0], self.bosses_dict["ValidSpawningPosition"].rect.centery - self.camera.position[1]), 
                                        radius = (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE),
                                        width = 1
                                        )

            # Draw the spawning tile
            pygame_draw_rect(
                            surface = self.game.scaled_surface, 
                            color = "firebrick1", 
                            rect = (
                                
                                    self.bosses_dict["ValidSpawningPosition"].rect.x - self.camera.position[0],
                                    self.bosses_dict["ValidSpawningPosition"].rect.y - self.camera.position[1], 
                                    self.bosses_dict["ValidSpawningPosition"].rect.width, 
                                    self.bosses_dict["ValidSpawningPosition"].rect.height
                                    ),
                            width = 0, 
                            border_radius = 5
                            )

            # Draw the spawning tile outline    
            pygame_draw_rect(
                            surface = self.game.scaled_surface, 
                            color = "black", 
                            rect = (
                                
                                    self.bosses_dict["ValidSpawningPosition"].rect.x - self.camera.position[0],
                                    self.bosses_dict["ValidSpawningPosition"].rect.y - self.camera.position[1], 
                                    self.bosses_dict["ValidSpawningPosition"].rect.width,
                                    self.bosses_dict["ValidSpawningPosition"].rect.height
                                    ),
                            width = 2, 
                            border_radius = 5
                            )
            
            # --------------------------------------------
            # Spawning effect timer 

            # If the timer has not finished counting down
            if self.bosses_dict["SpawningEffectTimer"] > 0:
                # Decrease the timer
                self.bosses_dict["SpawningEffectTimer"] -= 1000 * delta_time

            # If the timer has finished counting down
            if self.bosses_dict["SpawningEffectTimer"] <= 0:

                # If incrementing the spawning effect counter is less than the number of tiles for checking
                if self.bosses_dict["SpawningEffectCounter"] + 1 <= self.bosses_dict["NumOfTilesForChecking"]:
                    # Increment the spawning effect counter
                    self.bosses_dict["SpawningEffectCounter"] += 1

                # If incrementing the spawning effect counter is greater than the number of tiles for checking
                elif self.bosses_dict["SpawningEffectCounter"] + 1 > self.bosses_dict["NumOfTilesForChecking"]:
                    # Reset the spawning effect counter
                    self.bosses_dict["SpawningEffectCounter"] = self.bosses_dict["OriginalSpawningEffectCounter"]

                # Reset the timer (Adding it will help improve accuracy)
                self.bosses_dict["SpawningEffectTimer"] += self.bosses_dict["SpawningEffectTimeBetweenEachChange"]

            # Change the time between each change depending on how close the boss is to spawning
            self.bosses_dict["SpawningEffectTimeBetweenEachChange"] = self.bosses_dict["SpawningEffectOriginalTimeBetweenEachChange"] * self.bosses_dict["TimeToSpawnTimer"] / self.bosses_dict["TimeToSpawn"]
                                                                        
            # --------------------------------------------
            # Spawning timer 

            # If the timer has not finished counting down
            if self.bosses_dict["TimeToSpawnTimer"] > 0:
                # Decrease the timer
                self.bosses_dict["TimeToSpawnTimer"] -= 1000 * delta_time

            # If the timer has finished counting down
            if self.bosses_dict["TimeToSpawnTimer"] <= 0:
                # Set the boss spawn timer back to None, which will allow for the boss to be spawned
                self.bosses_dict["TimeToSpawnTimer"] = None

        # If the timer has finished counting down
        if self.bosses_dict["TimeToSpawnTimer"] == None:

            # If there is no current boss
            if len(self.game.boss_group) == 0:
                # Spawn the boss
                self.spawn_boss(boss_to_spawn = self.bosses_dict["CurrentBoss"])

                # -------------------------------------------------------------------------
                # Resetting for the next boss

                # Reset the spawning effect variables, so that when the next boss spawns, the effect will work as intended
                self.bosses_dict["SpawningEffectTimer"] = None
                self.bosses_dict["SpawningEffectTimeBetweenEachChange"] = self.bosses_dict["SpawningEffectOriginalTimeBetweenEachChange"]
                self.bosses_dict["SpawningEffectCounter"] = self.bosses_dict["OriginalSpawningEffectCounter"] 
                self.bosses_dict["SpawningPositionTilesList"] = []

                # Set the valid spawning position back to None (that way when the game restarts or the player goes to the next boss, the boss can be spawned)
                self.bosses_dict["ValidSpawningPosition"] = None
                self.bosses_dict["RandomSpawningPosition"] = random_choice(list(self.game.empty_tiles_dict.keys()))

    def spawn_boss(self, boss_to_spawn):

        # Spawns the boss
        
        # Check which boss should be spawned
        match boss_to_spawn:
            
            case "SikaDeer":
                # Import the SikaDeer boss
                from Level.Bosses.SikaDeerBoss import SikaDeerBoss
                
                # If the images for the deer boss have not been loaded already
                if hasattr(SikaDeerBoss, "ImagesDict") == False:
                    # Create a class attribute for the SikaDeerBoss, which is an image dictionary holding all the images for each action that the boss has
                    SikaDeerBoss.ImagesDict = {

                        "Chase": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Chase/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Chase")))),
                        "Stomp": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Stomp/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Stomp")))),

                        "Target": { 
                                "Up": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Target/Up/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Up")))),
                                "Up Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Target/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/UpRight")))),
                                "Up Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Target/UpRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/UpRight")))),

                                "Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Target/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Right")))),
                                "Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Target/Right/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Right")))),

                                "Down": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Target/Down/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Down")))),
                                "Down Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Target/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/DownRight")))),
                                "Down Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Target/DownRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/DownRight")))),
                                },
                        "Charge": {
                                "Up": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/Up/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Up")))),
                                "Up Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/UpRight")))),
                                "Up Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/UpRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/UpRight")))),

                                "Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Right")))),
                                "Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/Right/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Right")))),

                                "Down": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/Down/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Down")))),
                                "Down Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/DownRight")))),
                                "Down Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/DownRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/DownRight")))),
                                    
                                    },
                        "Stunned": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Stunned/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Stunned")))),


                                            }
                
                # Spawn the boss at the middle of the tile, with the bottom of the boss being at the bottom of the tile
                sika_deer_boss = SikaDeerBoss(
                                            x = self.bosses_dict["ValidSpawningPosition"].rect.centerx, 
                                            y = self.bosses_dict["ValidSpawningPosition"].rect.centery,
                                            surface = self.game.scaled_surface,
                                            scale_multiplier = self.game.scale_multiplier
                                            )
                
                # ----------------------------------------
                # Preparing groups 

                # Create a sprite group for the stomp attacks nodes created by the Sika Deer boss
                from Level.Objects.projectiles import StompController
                self.game.stomp_attack_nodes_group = pygame_sprite_Group()
                StompController.nodes_group = self.game.stomp_attack_nodes_group

                # Add the boss into the boss group
                self.game.boss_group.add(sika_deer_boss)

                # Update the game UI with this information
                self.game_ui.current_boss = self.game.boss_group.sprite

                # Set the current boss' last tile position to be the last tile position found (for collisions)
                self.game.boss_group.sprite.last_tile_position = self.game.last_tile_position

            case "GoldenMonkey":
                # Import the GoldenMonkey boss
                from Level.Bosses.GoldenMonkeyBoss import GoldenMonkeyBoss

                # If the images for the deer boss have not been loaded already
                if hasattr(GoldenMonkeyBoss, "ImagesDict") == False:

                    # Create a class attribute for the GoldenMonkeyBoss, which is an image dictionary holding all the images for each action that the boss has
                    GoldenMonkeyBoss.ImagesDict = {

                        "Chase": {
                                "Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/GoldenMonkey/Chase/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/Chase/Right")))),
                                "Right": tuple(pygame_image_load(f"graphics/Bosses/GoldenMonkey/Chase/Right/{i}.png").convert_alpha() for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/Chase/Right")))),
                                "Up": tuple(pygame_image_load(f"graphics/Bosses/GoldenMonkey/Chase/Up/{i}.png").convert_alpha() for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/Chase/Up")))),
                                "Up Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/GoldenMonkey/Chase/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/Chase/UpRight")))),
                                "Up Right": tuple(pygame_image_load(f"graphics/Bosses/GoldenMonkey/Chase/UpRight/{i}.png").convert_alpha() for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/Chase/UpRight")))),
                                "Down": tuple(pygame_image_load(f"graphics/Bosses/GoldenMonkey/Chase/Down/{i}.png").convert_alpha() for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/Chase/Down")))),
                                "Down Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/GoldenMonkey/Chase/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/Chase/DownRight")))),
                                "Down Right": tuple(pygame_image_load(f"graphics/Bosses/GoldenMonkey/Chase/DownRight/{i}.png").convert_alpha() for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/Chase/Downright")))),
                                },

                        "SpiralAttack": tuple(pygame_image_load(f"graphics/Bosses/GoldenMonkey/SpiralAttack/{i}.png").convert_alpha() for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/SpiralAttack")))),
                        "Sleep": tuple(pygame_image_load(f"graphics/Bosses/GoldenMonkey/Sleep/{i}.png").convert_alpha() for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/Sleep")))),

                        "DiveBomb": {
                                    "Launch": tuple(pygame_image_load(f"graphics/Bosses/GoldenMonkey/DiveBomb/Launch/{i}.png").convert_alpha() for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/DiveBomb/Launch")))),
                                    "Land": tuple(pygame_image_load(f"graphics/Bosses/GoldenMonkey/DiveBomb/Land/{i}.png").convert_alpha() for i in range(len(os_listdir("graphics/Bosses/GoldenMonkey/DiveBomb/Land"))))
                                    }
                                                }
                # Find the boss map boundaries, so that for the divebomb mechanic, they aren't spawned inside of a tile
                GoldenMonkeyBoss.boss_map_boundaries = {
                    "Top": 3 * TILE_SIZE, 
                    "Left": TILE_SIZE, 
                    "Right": (len(self.game.tile_map[0]) - 1) * TILE_SIZE, 
                    "Bottom": (len(self.game.tile_map) - 1) * TILE_SIZE,

                    # Used for the second phase circles
                    "EntireTileMapSize": (len(self.game.tile_map[0]) * TILE_SIZE, len(self.game.tile_map) * TILE_SIZE)
                    
                    }

                # Spawn the boss at the middle of the tile, with the bottom of the boss being at the bottom of the tile
                golden_monkey_boss = GoldenMonkeyBoss(
                                                    x = self.bosses_dict["ValidSpawningPosition"].rect.centerx, 
                                                    y = self.bosses_dict["ValidSpawningPosition"].rect.centery,
                                                    surface = self.game.scaled_surface,
                                                    scale_multiplier = self.game.scale_multiplier
                                                    )
                # ----------------------------------------
                # Preparing groups 

                # Create a dict for the chilli projectiles created by the Golden Monkey boss
                from Level.Objects.projectiles import ChilliProjectileController
                self.game.chilli_projectiles_dict = {}
                ChilliProjectileController.projectiles_dict = self.game.chilli_projectiles_dict

                # Add the boss into the boss group
                self.game.boss_group.add(golden_monkey_boss)

                # Update the game UI with this information
                self.game_ui.current_boss = self.game.boss_group.sprite

                # Set the current boss' last tile position to be the last tile position found (for collisions)
                self.game.boss_group.sprite.last_tile_position = self.game.last_tile_position

        # Remove the boss from the remaining bosses list 
        self.bosses_dict["RemainingBossesList"].remove(self.bosses_dict["CurrentBoss"])

        # If there are still remaining bosses after this current boss
        if len(self.bosses_dict["RemainingBossesList"]) > 0:
            # Set the display time back to default
            self.game_ui.guide_text_dict["DisplayTime"] = self.game_ui.guide_text_dict["OriginalDisplayTime"]

        # Update the Game UI with the current boss
        # Note: Required so that when the player goes to the next boss, we can draw the correct game UI
        self.game_ui.current_boss = self.game.boss_group.sprite
        self.game_ui.current_boss_name = self.bosses_dict["CurrentBoss"]