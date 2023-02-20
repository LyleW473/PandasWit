from pygame import Rect as pygame_Rect
from pygame import Surface as pygame_Surface
from pygame.font import Font as pygame_font_Font
from pygame.draw import rect as pygame_draw_rect
from pygame.draw import line as pygame_draw_line
from pygame.image import load as load_image
from Level.display_card import DisplayCard
from Global.settings import TILE_SIZE, BAR_ALPHA_LEVEL
from Global.functions import draw_text, sin_change_object_colour, move_item_vertically_sin
from pygame import Surface as pygame_Surface
from Level.effect_text import EffectText
from random import randrange as random_randrange
from math import degrees
from pygame.image import load as pygame_image_load


class GameUI:

    def __init__(self, surface, scale_multiplier, player_tools, player_gameplay_info_dict, camera_pan_information_dict):

        # Surface the UI will be drawn onto
        self.surface = surface
        
        # The scale multiplier used in the game
        self.scale_multiplier = scale_multiplier
        
        # Delta time attribute
        self.delta_time = None

        # The current boss
        self.current_boss = None

        # The current boss' name
        self.current_boss_name = None

        # The current mouse position
        self.mouse_position = None

        # The tools that the player has
        self.player_tools = player_tools
        
        # A dictionary containing information such as the HP the player has, the current tool equipped, amount of bamboo resource, etc.
        self.player_gameplay_info_dict = player_gameplay_info_dict

        # A dictionary containing information for each element of the game UI
        self.dimensions = {
                            "player_tools": { 
                                            "x": round(25 / scale_multiplier),
                                            "y": round(140 / scale_multiplier),
                                            "width": round(138 / scale_multiplier),
                                            "height": round(138 / scale_multiplier),
                                            "spacing_y": round(20 / scale_multiplier),
                                            },
                            "player_stats": {
                                "x": round(25 / scale_multiplier),
                                "y": 0,
                                "width": round(310 / scale_multiplier),
                                "height": round(200 / scale_multiplier),
                                "starting_position_from_inner_rect": (round(10 / scale_multiplier), round(10 / scale_multiplier)),
                                "spacing_y_between_stats": round(12 / scale_multiplier),
                                "spacing_x_between_image_and_text" : round(15 / scale_multiplier),
                                "scale_multiplier": scale_multiplier,

                                # Health bar
                                "spacing_y_between_stats_and_health_bar": round(20 / scale_multiplier),
                                # The width is calculated inside the display card class, using the inner body rect
                                "health_bar_height": int(52 / scale_multiplier), # Odd values will result in the health bar not being aligned properly
                                "health_bar_border_radius": 0,
                                "health_bar_outline_thickness": 2,
                                "changing_health_bar_edge_thickness" : 3,

                                # Frenzy mode bar
                                "frenzy_mode_bar_x": (self.surface.get_width() - (int(92 / scale_multiplier))) - TILE_SIZE,
                                "frenzy_mode_bar_y": (self.surface.get_height() - round(500 / scale_multiplier)) - TILE_SIZE,
                                "frenzy_mode_bar_width": int(92 / scale_multiplier),
                                "frenzy_mode_bar_height": round( 500 / scale_multiplier),
                                "changing_frenzy_mode_bar_edge_thickness": 3,
                                "frenzy_mode_bar_outline_thickness": 3,
                                "frenzy_mode_value_text_font": pygame_font_Font("graphics/Fonts/frenzy_mode_value_font.ttf", 18),
                                

                                # Frenzy mode glow visual effect (The bar will glow at a slow rate, once activated, the effect is synced with the player's visual effect)
                                "frenzy_mode_visual_effect_colour": self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"].copy(),
                                "frenzy_mode_visual_effect_angle_time_gradient": (360 - 0) / 2, # The rate of change of the angle over time (time in seconds)
                                "frenzy_mode_visual_effect_current_sin_angle": 0,

                                            },
                            "boss_bar": {
                                "x": (self.surface.get_width() - round(800 / scale_multiplier)) / 2,
                                "y": (self.surface.get_height() - round( (52 + 4) / scale_multiplier)) - TILE_SIZE, # Positioned 1 tile from the bottom of the screen (The 4 = the bar outline thickness)
                                "width": round((800) / scale_multiplier),
                                "height": round(52 / scale_multiplier),
                                "bar_outline_thickness": 4,
                                "text_font": pygame_font_Font("graphics/Fonts/player_stats_font.ttf", 32),
                                "changing_health_bar_edge_thickness": 3,
                                },
                            }
                            
        # A dictionary containing the display cards of all the elements of the game UI
        self.display_cards_dict = {
                                    "player_tools": [],
                                    "player_stats": [],
                                  }

        # A dictionary containing the images for the player stats
        self.stats_images_dict = {
                        "BambooResource": load_image("graphics/Misc/BambooResource.png").convert_alpha(),
                        "BuildingTiles": self.player_tools["BuildingTool"]["Images"]["TileImage"]
                                 }

        # A dictionary containing information about the effect text
        self.effect_text_info_dict = { 

                                        "Damage": {
                                                        "Font": pygame_font_Font("graphics/Fonts/effect_text_font.ttf", 16),
                                                        "LargerFont": pygame_font_Font("graphics/Fonts/effect_text_font.ttf", 18),
                                                        "DisplayTime": 2000,
                                                        "Colour": (170, 4, 4),
                                                        "FloatUpTimeGradient": 12 / 0.2, # The vertical distance travelled over time in seconds (Should be the same as the display time)
                                                        "AlphaLevelTimeGradient": (125 - 255) / 0.6,
                                                        "DefaultAlphaLevel": 255,

                                                        },
                                        "Heal": {
                                                        "Font": pygame_font_Font("graphics/Fonts/effect_text_font.ttf", 24),
                                                        "DisplayTime": 3000,
                                                        "Colour": (4, 225, 4),
                                                        "FloatUpTimeGradient": 12 / 0.2, # The vertical distance travelled over time in seconds (Should be the same as the display time)
                                                        "AlphaLevelTimeGradient": (125 - 255) / 0.6,
                                                        "DefaultAlphaLevel": 255,
                                                        },
                                        
                                        "BambooResourceReplenishment": {
                                                        "Font": pygame_font_Font("graphics/Fonts/effect_text_font.ttf", 16),
                                                        "DisplayTime": 2500,
                                                        "Colour": (247, 127, 0),
                                                        "FloatUpTimeGradient": 12 / 0.2, # The vertical distance travelled over time in seconds (Should be the same as the display time)
                                                        "AlphaLevelTimeGradient": (125 - 255) / 0.6,
                                                        "DefaultAlphaLevel": 255,
                                                        },

                                        "FrenzyModeValueIncrement":{
                                                        "Font": pygame_font_Font("graphics/Fonts/effect_text_font.ttf", 12), # 14
                                                        "LargerFont": pygame_font_Font("graphics/Fonts/effect_text_font.ttf", 24),
                                                        "DisplayTime": 500,
                                                        "Colour": (235, 199, 230), #,(191, 172, 226)
                                                        "FloatUpTimeGradient": 12 / 0.2, # The vertical distance travelled over time in seconds (Should be the same as the display time)
                                                        "AlphaLevelTimeGradient": (125 - 255) / 0.6,
                                                        "DefaultAlphaLevel": 255,
                                                        },
                                        "Sleep": {
                                                "Font": pygame_font_Font("graphics/Fonts/frenzy_mode_value_font.ttf", 30),
                                                "DisplayTime": 1000,
                                                "DefaultAlphaLevel": 255,
                                                "AlphaLevelTimeGradient": (0 - 255) / 1,
                                                "FloatUpTimeGradient": 10 / 0.2,
                                                "FloatRightTimeGradient": 5 / 0.2,
                                                "Colour": "white"
                                                }
                        }

     

        # Create a list for all the effect text
        EffectText.effect_text_list = []

        # Create display cards
        self.create_player_tools_display_cards()
        self.create_player_stats_display_cards()

        # ------------------------------------------------------------
        # Alpha surfaces

        # Frenzy mode bar
        self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"] =  pygame_Surface((self.dimensions["player_stats"]["frenzy_mode_bar_width"], self.dimensions["player_stats"]["frenzy_mode_bar_height"]))
        self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"].set_colorkey("black")
        self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"].set_alpha(BAR_ALPHA_LEVEL)

        # Boss' health bar
        self.dimensions["boss_bar"]["alpha_surface"] =  pygame_Surface((self.dimensions["boss_bar"]["width"], self.dimensions["boss_bar"]["height"]))
        self.dimensions["boss_bar"]["alpha_surface"].set_colorkey("black")
        self.dimensions["boss_bar"]["alpha_surface"].set_alpha(BAR_ALPHA_LEVEL)

        # ------------------------------------------------------------
        # Cursor image
        self.default_cursor_image = load_image("graphics/Cursors/Default.png").convert_alpha()
    
        """ 'Hidden' attributes:

        self.camera_position
        self.angled_polygons_controller
    
        """
        # ------------------------------------------------------------
        # VFX

        # Angled polygons
        self.angled_polygons_surface = pygame_Surface((self.surface.get_width(), self.surface.get_height()))
        self.angled_polygons_surface.set_colorkey("black")

        # ------------------------------------------------------------
        # Camera panning 

        # A dictionary containing information relating to the camera panning
        self.camera_pan_information_dict = camera_pan_information_dict

        # -----------------------------
        # Black bars

        # The height of the black bars
        self.black_bar_height = 0

        # The rate of change of the height over time
        self.black_bar_height_time_gradient = ((self.surface.get_height() / 5) - 0) / (self.camera_pan_information_dict["PanTime"] / 1000)
        self.original_black_bar_height_time_gradient = ((self.surface.get_height() / 5) - 0) / (self.camera_pan_information_dict["PanTime"] / 1000)
        
        # A variable to store the new height (floating point accuracy)
        self.black_bar_new_height = 0

        # -----------------------------
        # Boss text

        # The text font (Re-using the same font for the frenzy mode value)
        self.boss_text_font = pygame_font_Font("graphics/Fonts/frenzy_mode_value_font.ttf", 56)

        # The size required to render the text depending on the text
        self.boss_text_font_size = None
        
        # The name of the boss
        self.boss_text = None

        # The rate of change in the alpha level of the over time
        # Note: THe time is in half so that it fades in and out
        self.boss_text_alpha_level_time_gradient = 200 / ((self.camera_pan_information_dict["BossPanLockTime"] / 1000) / 5) # 5 so that at the middle of the timer, the text will be completely opaque
        self.boss_text_new_alpha_level = 0

        # -----------------------------
        # Guide text

        self.guide_text_dict = {
                                "OriginalDisplayTime": 3.5,
                                "DisplayTime": 3.5,
                                "OriginalPosition": None,
                                "CurrentPosition": None,
                                "Displacement": 30,
                                "CurrentSinAngle": 0,
                                "AngleTimeGradient": 360 / 2.5,
                                "Font": pygame_font_Font("graphics/Fonts/player_stats_font.ttf", 48),

                                
                                "AllGuideTextMessages": 
                                                    # Note: Key is the purpose, The value is a list containing the text and a boolean value as to whether its been shown before
                                                    {
                                                    "SpawnBoss": ['Press the "F" key to spawn the boss', False],
                                                    "ActivateFrenzyMode": ['Press the "Spacebar" key to activate Frenzy Mode!', False],
                                                    "SikaDeerReflectProjectiles": ["Build to reflect these projectiles!", False],
                                                    "SikaDeerBuildToStun": ["Blocking the boss with tiles can stun it!", False],
                                                    "BuildToSlowBoss": ["Tiles can slow down the boss! Remember to pick them back up!", False],
                                                    "SikaDeerIsVulnerable": ["The Sika Deer receives more damage when stunned!", False],
                                                    "KnockbackImmunity": ["You are temporarily immune to KNOCKBACK attacks", False],
                                                    "GoldenMonkeyEnergyCounter": ["This boss gets fatigued, keep an eye on its energy counter!", False],
                                                    "GoldenMonkeyIsVulnerable": ["The Golden Monkey receives more damage when sleeping!", False],
                                                    "GoldenMonkeyEnterSecondPhase": ["The Golden Monkey has become enraged and has obtained a new attack!", False],
                                                    "GameCompletion": ["Congratulations for beating the game! Thanks for playing, hope you had fun!", False],
                                                    
                                                    }
                                }

        # List of all the current guide text's being shown
        self.guide_text_list = []

    # ---------------------------------------------------------------------
    # Resetting methods

    def reset_effect_text_list(self):

        # Resets the effect text list when the game is over

        # If there are any effect text in the list
        if len(EffectText.effect_text_list) > 0:
            # Clear the list
            EffectText.effect_text_list = []

    def reset_visual_effects_dict(self):

        # Resets visual effects dictionaries
        
        # If there are any angled polygons effects
        if hasattr(self, "angled_polygons_controller") and len(self.angled_polygons_controller.polygons_dict) > 0:
            # Empty the dictionary and reset the amount of polygons created
            self.angled_polygons_controller.polygons_dict = {}
            self.angled_polygons_controller.polygons_created = 0
    
    # ---------------------------------------------------------------------
    # Display methods

    def create_player_tools_display_cards(self):

        # Creates the players' tools' display cards

        # Set the font for the display card numbers
        DisplayCard.tools_display_card_number_text_font = pygame_font_Font("graphics/Fonts/player_stats_font.ttf", 16)

        # If the length of the inventory display cards dict is not the same as the length of the amount of tools 
        if len(self.display_cards_dict["player_tools"]) != len(self.player_tools):
            
            # For each tool in the player's inventory of tools
            for tool in self.player_tools.keys():
                # The spacing on the y-axis between each card
                spacing_y = self.dimensions["player_tools"]["spacing_y"]

                # Create a display card, passing in: The rect, main surface, an alpha surface for the display card, icon image, the purpose and the display card number
                self.display_cards_dict["player_tools"].append(DisplayCard(
                                            rect = pygame_Rect(
                                                            self.dimensions["player_tools"]["x"], 
                                                            self.dimensions["player_tools"]["y"] + (self.dimensions["player_tools"]["height"] * len(self.display_cards_dict["player_tools"])) + (spacing_y * len(self.display_cards_dict["player_tools"])),
                                                            self.dimensions["player_tools"]["width"],
                                                            self.dimensions["player_tools"]["height"]),
                                            surface = self.surface,
                                            alpha_surface = pygame_Surface((self.dimensions["player_tools"]["width"], self.dimensions["player_tools"]["height"])),
                                            images = self.player_tools[tool]["Images"]["IconImage"],
                                            purpose = "PlayerTools",
                                            display_card_number = len(self.display_cards_dict["player_tools"]) + 1,
                                            which_tool = tool
                                                                )
                                                            )
                
                # If this is the last tool inside the player's inventory of tools
                if len(self.display_cards_dict["player_tools"]) == len(self.player_tools):
                    # Temp variable for the last display card
                    last_display_card = self.display_cards_dict["player_tools"][len(self.display_cards_dict["player_tools"]) - 1]
                    
                    # Set the dimensions of where the player stats to start to be below that
                    self.dimensions["player_stats"]["y"] = last_display_card.rect.y + last_display_card.rect.height + spacing_y
    
    def create_player_stats_display_cards(self):

        # Creates the players' stats' display cards
        
        # Create player stats cards and add it to the list in the player stats of the display cards dictionary
        self.display_cards_dict["player_stats"].append(DisplayCard
                                                                    (
                                                                        rect = pygame_Rect(
                                                                                            self.dimensions["player_stats"]["x"],
                                                                                            self.dimensions["player_stats"]["y"], 
                                                                                            self.dimensions["player_stats"]["width"], 
                                                                                            self.dimensions["player_stats"]["height"]
                                                                                            ),
                                                                        surface = self.surface, 
                                                                        alpha_surface = pygame_Surface((self.dimensions["player_stats"]["width"], self.dimensions["player_stats"]["height"])),
                                                                        images = [self.stats_images_dict["BuildingTiles"], self.stats_images_dict["BambooResource"]],
                                                                        text_font = pygame_font_Font("graphics/Fonts/player_stats_font.ttf", 32),
                                                                        extra_information_dict = {key:value for key, value in self.dimensions["player_stats"].items() if key not in ["x", "y", "width", "height"]}, # Adds extra information into a dictionary
                                                                        purpose = "PlayerStats"
                                                                    )
                                                                )

    def draw_boss_health(self):
        
        # If a boss has been spawned
        if self.current_boss != None:

            # Fill the boss bar's alpha surface with black
            self.dimensions["boss_bar"]["alpha_surface"].fill("black")

            # --------------------------------------
            # Default body

            pygame_draw_rect(
                            surface = self.dimensions["boss_bar"]["alpha_surface"],
                            color = "gray21",
                            rect = pygame_Rect(
                                            0,
                                            0,
                                            self.dimensions["boss_bar"]["width"],
                                            self.dimensions["boss_bar"]["height"]
                                            ),
                            width = 0
                            )
            
            # --------------------------------------
            # Bar that changes depending on the health of the current boss

            health_bar_width = max((self.current_boss.extra_information_dict["CurrentHealth"] / self.current_boss.extra_information_dict["MaximumHealth"] ) * self.dimensions["boss_bar"]["width"], 0)

            # If the boss isn't the "GoldenMonkey"
            if self.current_boss_name != "GoldenMonkey":
                # Set the health bar to be red
                health_bar_colours = ("firebrick3", "firebrick4", (200, 44, 44))

            # If the boss is the "GoldenMonkey"
            elif self.current_boss_name == "GoldenMonkey":
                # If the boss is in phase 1
                if self.current_boss.current_phase == 1:
                    # Set the health bar to be red
                    health_bar_colours = ("firebrick3", "firebrick4", (200, 44, 44))
                # If the boss is in phase 2
                elif self.current_boss.current_phase == 2:
                    # Set the health bar to be orange
                    health_bar_colours = ((255,140,0), (238,118,0), (220,108,0))

            pygame_draw_rect(
                            surface = self.dimensions["boss_bar"]["alpha_surface"],
                            color = health_bar_colours[0],
                            rect = pygame_Rect(
                                            0,
                                            0,
                                            health_bar_width,
                                            self.dimensions["boss_bar"]["height"] / 2
                                            ),
                            width = 0
                            )

            pygame_draw_rect(
                            surface = self.dimensions["boss_bar"]["alpha_surface"],
                            color = health_bar_colours[1],
                            rect = pygame_Rect(
                                            0,
                                            0 + (self.dimensions["boss_bar"]["height"] / 2),
                                            health_bar_width,
                                            self.dimensions["boss_bar"]["height"] / 2
                                            ),
                            width = 0
                            )

            # Only draw the edge when the width of the health bar is greater than 0
            if health_bar_width > 0:

                # Edge at the end of the changing part of the boss' health
                pygame_draw_line(
                                surface = self.dimensions["boss_bar"]["alpha_surface"], 
                                color = health_bar_colours[2],
                                start_pos = ((health_bar_width) - (self.dimensions["boss_bar"]["changing_health_bar_edge_thickness"] / 2), 0),
                                end_pos = ((health_bar_width) - (self.dimensions["boss_bar"]["changing_health_bar_edge_thickness"] / 2), self.dimensions["boss_bar"]["height"]),
                                width = self.dimensions["boss_bar"]["changing_health_bar_edge_thickness"]
                                )

            # --------------------------------------
            # Draw the alpha surface onto the main surface
            self.surface.blit(self.dimensions["boss_bar"]["alpha_surface"], (self.dimensions["boss_bar"]["x"], self.dimensions["boss_bar"]["y"]))

            # --------------------------------------
            # Outline
            pygame_draw_rect(
                            surface = self.surface,
                            color = "black",
                            rect = pygame_Rect(
                                            self.dimensions["boss_bar"]["x"] - (self.dimensions["boss_bar"]["bar_outline_thickness"]),
                                            self.dimensions["boss_bar"]["y"] - (self.dimensions["boss_bar"]["bar_outline_thickness"]),
                                            self.dimensions["boss_bar"]["width"] + (self.dimensions["boss_bar"]["bar_outline_thickness"] * 2),
                                            self.dimensions["boss_bar"]["height"] + (self.dimensions["boss_bar"]["bar_outline_thickness"] * 2)
                                            ),
                            width = self.dimensions["boss_bar"]["bar_outline_thickness"]
                                )

            # --------------------------------------
            # Health bar text:

            # Update the text that will be displayed on the screen depending on the boss' current health
            boss_health_text = f'{max(self.current_boss.extra_information_dict["CurrentHealth"], 0)} / {self.current_boss.extra_information_dict["MaximumHealth"]}'

            # Calculate the font size, used to position the text at the center of the health bar
            boss_health_text_font_size = self.dimensions["boss_bar"]["text_font"].size(boss_health_text)
            
            # Draw the text displaying the amount of bamboo resource
            draw_text(
                    text = boss_health_text, 
                    text_colour = "white",
                    font = self.dimensions["boss_bar"]["text_font"],
                    x = (self.dimensions["boss_bar"]["x"] + (self.dimensions["boss_bar"]["width"] / 2)) - ((boss_health_text_font_size[0] / self.scale_multiplier) / 2),
                    y = (self.dimensions["boss_bar"]["y"] + (self.dimensions["boss_bar"]["height"] / 2)) - ((boss_health_text_font_size[1] / self.scale_multiplier) / 2),
                    surface = self.surface, 
                    scale_multiplier = self.scale_multiplier
                    )

    def draw_golden_monkey_energy_indicator(self):
        
        # If there is a current boss and the boss is the "GoldenMonkey"
        if self.current_boss != None and self.current_boss_name == "GoldenMonkey":

            # If the following does not exist in the dimensions dictionary
            if self.dimensions.get("golden_monkey_energy_indicator") == None:
                # Load the image and text font and calculate the x and y positions that the image will be blitted at
                self.dimensions["golden_monkey_energy_indicator"] = {
                                                                    "Image": pygame_image_load("graphics/Misc/Energy.png").convert_alpha(),
                                                                    "x": self.dimensions["boss_bar"]["x"] + self.dimensions["boss_bar"]["width"],
                                                                    "y": self.dimensions["boss_bar"]["y"] + (self.dimensions["boss_bar"]["height"] / 2),
                                                                    "Font": self.dimensions["boss_bar"]["text_font"],
                                                                    "SpacingXFromBossBar": 20
                                                                    
                                                                        }
                # X pos shift
                self.dimensions["golden_monkey_energy_indicator"]["x"] += self.dimensions["golden_monkey_energy_indicator"]["SpacingXFromBossBar"]
                
                # Alpha surface
                self.dimensions["AlphaSurface"] = pygame_Surface(self.dimensions["golden_monkey_energy_indicator"]["Image"].get_size())
                self.dimensions["AlphaSurface"].set_colorkey("blue")
                self.dimensions["AlphaSurface"].set_alpha(130)

            # Fill the alpha surface with blue
            self.dimensions["AlphaSurface"].fill("blue")

            # Draw the image onto the alpha surface
            self.dimensions["AlphaSurface"].blit(self.dimensions["golden_monkey_energy_indicator"]["Image"], (0, 0))

            # Draw the alpha surface at the location
            self.surface.blit(
                            self.dimensions["AlphaSurface"], 
                            (self.dimensions["golden_monkey_energy_indicator"]["x"] , self.dimensions["golden_monkey_energy_indicator"]["y"] - (self.dimensions["golden_monkey_energy_indicator"]["Image"].get_height() / 2))
                            )

            # Update the text that will be displayed on the screen depending on the boss' current energy
            energy_text = f'{max(self.current_boss.energy_amount, 0)}'
            # Calculate the font size, used to position the text properly
            energy_text_font_size = self.dimensions["golden_monkey_energy_indicator"]["Font"].size(energy_text)

            #pygame_draw_line(self.surface, "green", (0, (self.dimensions["golden_monkey_energy_indicator"]["y"])),(self.surface.get_width(), (self.dimensions["golden_monkey_energy_indicator"]["y"])))

            # Draw the text displaying the amount of energy the golden monkey boss has
            draw_text(
                    text = energy_text, 
                    text_colour = "white",
                    font = self.dimensions["golden_monkey_energy_indicator"]["Font"],
                    x = (self.dimensions["golden_monkey_energy_indicator"]["x"] + (self.dimensions["golden_monkey_energy_indicator"]["Image"].get_width() / 2)) - ((energy_text_font_size[0] / 2) / self.scale_multiplier),
                    y = (self.dimensions["golden_monkey_energy_indicator"]["y"]) - ((energy_text_font_size[1] / 2) / self.scale_multiplier),
                    surface = self.surface, 
                    scale_multiplier = self.scale_multiplier
                    )

    def draw_player_frenzy_mode_bar(self):

        # Fill the frenzy mode bar's alpha surface with black
        self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"].fill("black")

        # --------------------------------------
        # Default body

        pygame_draw_rect(
                        surface = self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"],
                        color = "gray21",
                        rect = pygame_Rect(
                                        0,
                                        0,
                                        self.dimensions["player_stats"]["frenzy_mode_bar_width"],
                                        self.dimensions["player_stats"]["frenzy_mode_bar_height"]
                                        ),
                        width = 0
                        ) 
        # --------------------------------------
        # Bar that changes depending on the frenzy mode value

        # Calculate the height of the bar
        frenzy_mode_bar_height = max(self.player_gameplay_info_dict["CurrentFrenzyModeValue"] / self.player_gameplay_info_dict["MaximumFrenzyModeValue"] * self.dimensions["player_stats"]["frenzy_mode_bar_height"], 0)
        # Calculate the y position based on the height of the bar (int(frenzy_mode_bar_height) so that the bar doesn't get misaligned with decimal increments in the frenzy mode value)
        frenzy_mode_bar_y_pos = (self.dimensions["player_stats"]["frenzy_mode_bar_height"]) - int(frenzy_mode_bar_height)

        # If the player has not activated frenzy mode
        if self.player_gameplay_info_dict["FrenzyModeTimer"] == None:

            # If the frenzy mode bar is not completely full
            if self.player_gameplay_info_dict["CurrentFrenzyModeValue"] != self.player_gameplay_info_dict["MaximumFrenzyModeValue"]:
                # Set the colour of the bar to be the default colours
                frenzy_mode_bar_colour = ("darkorchid2", "darkorchid3")

            # If the frenzy mode bar is completely full
            elif self.player_gameplay_info_dict["CurrentFrenzyModeValue"] == self.player_gameplay_info_dict["MaximumFrenzyModeValue"]:
                
                # Note: This is not synced with the player, but a separate visual effect to indicate that the bar is full
                
                # Lambda function to offset the rgb values of the current frenzy mode colour
                darker_colour = lambda x: x - min(self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"])
                
                # Set the colour of the bar to oscillate slowly with the visual effect settings
                self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"], self.dimensions["player_stats"]["frenzy_mode_visual_effect_current_sin_angle"] = sin_change_object_colour(
                                                                                                                                        
                                                                                                            # The current sin angle
                                                                                                            current_sin_angle = self.dimensions["player_stats"]["frenzy_mode_visual_effect_current_sin_angle"],

                                                                                                            # The rate of change in the sin angle over time
                                                                                                            angle_time_gradient = self.dimensions["player_stats"]["frenzy_mode_visual_effect_angle_time_gradient"], 

                                                                                                            # Set the colour that will be changed (the return value)
                                                                                                            colour_to_change = self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"],

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

                # Set the frenzy mode bar colour (A tuple because the bar is made up of two rectangles)
                frenzy_mode_bar_colour = (
                                        self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"], 
                                        tuple(darker_colour(self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"][i]) for i in range(0, len(self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"])))
                                        )

        # If the player has activated frenzy mode
        if self.player_gameplay_info_dict["FrenzyModeTimer"] != None:

            # Note: This is synced to the visual effect of the player
            
            # Lambda function to offset the rgb values of the current frenzy mode colour
            darker_colour = lambda x: x - 10

            # Set the frenzy mode bar colour (A tuple because the bar is made up of two rectangles)
            frenzy_mode_bar_colour = (
                                    self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"], 
                                    tuple(min(max(darker_colour(self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"][i]), 0), 255) for i in range(0, len(self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"])))
                                    
                                    )
        
        # Drawing the frenzy mode bar
        pygame_draw_rect(
                        surface = self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"],
                        color = frenzy_mode_bar_colour[0],
                        rect = pygame_Rect(
                                        0,
                                        frenzy_mode_bar_y_pos,
                                        self.dimensions["player_stats"]["frenzy_mode_bar_width"] / 2,
                                        frenzy_mode_bar_height
                                        ),
                        width = 0
                        ) 

        pygame_draw_rect(
                        surface = self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"],
                        color = frenzy_mode_bar_colour[1],
                        rect = pygame_Rect(
                                        0 + (self.dimensions["player_stats"]["frenzy_mode_bar_width"] / 2),
                                        frenzy_mode_bar_y_pos,
                                        self.dimensions["player_stats"]["frenzy_mode_bar_width"] / 2,
                                        frenzy_mode_bar_height
                                        ),
                        width = 0
                        ) 

        # Only draw the edge when the height of the frenzy mode bar is greater than 0
        if frenzy_mode_bar_height > 0:
            
            # If the player has not activated frenzy mode
            if self.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                # Set the edge colour as the default colour
                bar_edge_colour = (174, 50, 205)
            
            # If the player has activated frenzy mode
            elif self.player_gameplay_info_dict["FrenzyModeTimer"] != None:
                # Set the bar edge as the current frenzy mode visual effect colour 
                # Note: Call the darker colour lambda function again for a colour that will always be darker than the bar
                bar_edge_colour = tuple(min(max(darker_colour(frenzy_mode_bar_colour[1][i]), 0), 255) for i in range(0, len(self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"])))

            # Edge at the end of the changing part of the boss' health
            pygame_draw_line(
                            surface = self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"], 
                            color = bar_edge_colour,
                            start_pos = (0, frenzy_mode_bar_y_pos - (self.dimensions["player_stats"]["changing_frenzy_mode_bar_edge_thickness"] / 2)),
                            end_pos = (0 + self.dimensions["player_stats"]["frenzy_mode_bar_width"], frenzy_mode_bar_y_pos - (self.dimensions["player_stats"]["changing_frenzy_mode_bar_edge_thickness"] / 2)),
                            width = self.dimensions["player_stats"]["changing_frenzy_mode_bar_edge_thickness"]
                            )
        
        # --------------------------------------
        # Draw the alpha surface onto the main surface
        self.surface.blit(self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"], (self.dimensions["player_stats"]["frenzy_mode_bar_x"], self.dimensions["player_stats"]["frenzy_mode_bar_y"]))
        
        # --------------------------------------
        # Outline
        pygame_draw_rect(
                        surface = self.surface,
                        color = "black",
                        rect = pygame_Rect(
                                        self.dimensions["player_stats"]["frenzy_mode_bar_x"] - (self.dimensions["player_stats"]["frenzy_mode_bar_outline_thickness"]),
                                        self.dimensions["player_stats"]["frenzy_mode_bar_y"] - (self.dimensions["player_stats"]["frenzy_mode_bar_outline_thickness"]),
                                        self.dimensions["player_stats"]["frenzy_mode_bar_width"] + (self.dimensions["player_stats"]["frenzy_mode_bar_outline_thickness"] * 2),
                                        self.dimensions["player_stats"]["frenzy_mode_bar_height"] + (self.dimensions["player_stats"]["frenzy_mode_bar_outline_thickness"] * 2)
                                        ),
                        width = self.dimensions["player_stats"]["frenzy_mode_bar_outline_thickness"]
                            )
        
        # --------------------------------------
        # Frenzy mode bar text:

        # Update the text that will be displayed on the screen depending on the current frenzy mode value
        frenzy_mode_value_text = f'{int((self.player_gameplay_info_dict["CurrentFrenzyModeValue"] / self.player_gameplay_info_dict["MaximumFrenzyModeValue"]) * 100)} %' # A percentage meter

        # Calculate the font size, used to position the text at the center of the health bar
        frenzy_mode_value_text_font_size = self.dimensions["player_stats"]["frenzy_mode_value_text_font"].size(frenzy_mode_value_text)
        
        # Draw the text displaying the amount of bamboo resource
        draw_text(
                text = frenzy_mode_value_text, 
                text_colour = "white",
                font = self.dimensions["player_stats"]["frenzy_mode_value_text_font"],
                x = (self.dimensions["player_stats"]["frenzy_mode_bar_x"] + (self.dimensions["player_stats"]["frenzy_mode_bar_width"] / 2)) - ((frenzy_mode_value_text_font_size[0]) / 2),
                y = (self.dimensions["player_stats"]["frenzy_mode_bar_y"] + (self.dimensions["player_stats"]["frenzy_mode_bar_height"] / 2)) - ((frenzy_mode_value_text_font_size[1]) / 2),
                surface = self.surface, 

                )

    def draw_display_cards(self):

        # For each tool display card
        for tool_display_card in self.display_cards_dict["player_tools"]:

            # If this tool card is for the tool the player currently has equipped
            if tool_display_card.which_tool == self.player_gameplay_info_dict["CurrentToolEquipped"]:
                # Set the alpha level of the display card's surfaces to its maximum alpha level
                if tool_display_card.alpha_surface.get_alpha() != DisplayCard.tools_maximum_alpha_surface_alpha_level:
                    tool_display_card.alpha_surface.set_alpha(DisplayCard.tools_maximum_alpha_surface_alpha_level)
                    tool_display_card.second_alpha_surface.set_alpha(DisplayCard.tools_maximum_second_alpha_surface_alpha_level)
            
            # If this tool card is not for the tool the player currently has equipped
            elif tool_display_card.which_tool != self.player_gameplay_info_dict["CurrentToolEquipped"]:
                # Set the alpha level of the display card's surfaces to its minimum alpha level
                if tool_display_card.alpha_surface.get_alpha() != DisplayCard.tools_minimum_alpha_surface_alpha_level:
                    tool_display_card.alpha_surface.set_alpha(DisplayCard.tools_minimum_alpha_surface_alpha_level)
                    tool_display_card.second_alpha_surface.set_alpha(DisplayCard.tools_minimum_second_alpha_surface_alpha_level)

            # Draw the card
            tool_display_card.draw()

        # For each stats display card
        for stats_display_card in self.display_cards_dict["player_stats"]:
            # Draw the card, passing in the player tools dictionary and the players gameplay info dictionary
            stats_display_card.draw(player_tools = self.player_tools, player_gameplay_info_dict = self.player_gameplay_info_dict)

    def draw_mouse_cursor(self):

        # Draws the new cursor

        # Blit the cursor image at the mouse position, subtracting half of the cursor image's width and height
        self.surface.blit(self.default_cursor_image, (self.mouse_position[0] - (self.default_cursor_image.get_width()/ 2), self.mouse_position[1]- (self.default_cursor_image.get_height() / 2)))

    def draw_camera_pan_bars(self):

        # Draws the black bars when the camera is panning towards the boss

        # If the camera is panning
        if self.camera_pan_information_dict["PanTimer"] != None:
            
            # If the camera is panning back to the player and the if the black bar height time gradient has not already been inverted / flipped
            if self.camera_pan_information_dict["BossPanComplete"] == True and self.black_bar_height_time_gradient == self.original_black_bar_height_time_gradient:
                # Invert the black bar height time gradient so that the black bars shrink
                self.black_bar_height_time_gradient *= -1

            # Shrink / Increase the black bar height depending on the black bar height time gradient
            self.black_bar_new_height += self.black_bar_height_time_gradient * self.delta_time
            self.black_bar_height = round(self.black_bar_new_height)

        # If the camera panning has been completed and the black bar variables have not been reset yet (Camera panning has completely finished)
        elif self.player_gameplay_info_dict["CanStartOperating"] == True and self.black_bar_height_time_gradient != self.original_black_bar_height_time_gradient:
            # Reset the black bar heights and gradient
            self.black_bar_height = 0
            self.black_bar_new_height = 0
            self.black_bar_height_time_gradient = self.original_black_bar_height_time_gradient

            # Reset the boss text font size back to None, so that if the player spawns another boss, the text will be different
            self.boss_text_font_size = None
            self.boss_text = None

        # If the black bar height is greater than 0
        if self.black_bar_height > 0:

            # ----------------------------------------------------------
            # Drawing the black bars

            # The top black bar
            pygame_draw_rect(
                surface = self.surface,
                color = "black", 
                rect = (
                        0, 
                        0, 
                        self.surface.get_width(), 
                        self.black_bar_height
                        ),
                width = 0
                            )

            # The bottom black bar
            pygame_draw_rect(
                surface = self.surface,
                color = "black", 
                rect = (
                        0, 
                        self.surface.get_height() - self.black_bar_height , 
                        self.surface.get_width(), 
                        self.black_bar_height
                        ),
                width = 0
                            )
            
            # ----------------------------------------------------------
            # Drawing the boss text

            # If the camera is currently locking onto the boss
            if self.camera_pan_information_dict["BossPanLockTimer"] != None:
                
                # If the boss text (and all its components) has not been created yet
                if self.boss_text_font_size == None:

                    # Assigning the boss text 
                    if self.current_boss_name == "SikaDeer":
                        self.boss_text = "Sika Deer"

                    elif self.current_boss_name == "GoldenMonkey":
                        self.boss_text = "Golden Monkey"

                    # Calculae the text font size for positioning the text correctly
                    self.boss_text_font_size = self.boss_text_font.size(self.boss_text)

                    # Create an alpha surface for the boss text
                    self.boss_text_alpha_surface = pygame_Surface(self.boss_text_font_size)
                    self.boss_text_alpha_surface.set_colorkey("black")
                    self.boss_text_alpha_surface.set_alpha(0)

                # Fill the boss text alpha surface with black
                self.boss_text_alpha_surface.fill("black")
                
                # Draw the boss text onto the boss text alpha surface
                draw_text(
                        text = self.boss_text,
                        text_colour = "white",
                        font = self.boss_text_font,
                        x = 0,
                        y = 0,
                        surface = self.boss_text_alpha_surface

                        )      

                # Draw the boss text alpha surface onto the main surface, at the midtop of the screen
                self.surface.blit(self.boss_text_alpha_surface, ((self.surface.get_width() / 2) - (self.boss_text_font_size[0] / 2), (self.black_bar_height / 2) - (self.boss_text_font_size[1] / 2)))

                # ---------------------------
                # Adjust alpha of the surface

                # If the boss pan lock timer is not halfway through the countdown (Countdown is near the start)
                if self.camera_pan_information_dict["BossPanLockTimer"] > (self.camera_pan_information_dict["BossPanLockTime"] / 2):
                    # The text should be fading in
                    self.boss_text_new_alpha_level += self.boss_text_alpha_level_time_gradient * self.delta_time

                # If the boss pan lock timer is halfway through the countdown (Countdown is nearly finished)
                if self.camera_pan_information_dict["BossPanLockTimer"] < (self.camera_pan_information_dict["BossPanLockTime"] / 2):
                    # The text should be fading out
                    self.boss_text_new_alpha_level -= self.boss_text_alpha_level_time_gradient * self.delta_time

                # Set the alpha level, not allowing it to go below 0 or above 255
                self.boss_text_alpha_surface.set_alpha(max(0, min(255, self.boss_text_new_alpha_level)))

    # ---------------------------------------------------------------------
    # Tutorial / Guide text

    def display_introduction(self, surface):

        # If this dictionary does not exist
        if hasattr(self, "introduction_box_dict") == False:
            # Create a dictionary containing info for the introduction box
            self.introduction_box_dict = {
                                                    "Images": (
                                                                    pygame_image_load("graphics/Misc/IntroText1.png").convert_alpha(),
                                                                    pygame_image_load("graphics/Misc/IntroText2.png").convert_alpha()
                                                                    ),
                                                    "IntroductionCompleted": False,
                                                    "IntroductionBoxSize": (700, 800),
                                                    "IntroductionStage": 1

                                                    }
        
        # If the introduction has not been completed yet
        if self.introduction_box_dict["IntroductionCompleted"] == False:

            # Calculate the box positions for the introduction box
            introduction_box_positions = (
                                    (surface.get_width() / 2) - (self.introduction_box_dict["IntroductionBoxSize"][0] / 2), 
                                    (surface.get_height() / 2) - (self.introduction_box_dict["IntroductionBoxSize"][1] / 2), 
                                    )
            # Body
            pygame_draw_rect(
                surface = surface,
                color = (97, 104, 58), 
                rect = (
                    introduction_box_positions[0], 
                    introduction_box_positions[1], 
                    self.introduction_box_dict["IntroductionBoxSize"][0],
                    self.introduction_box_dict["IntroductionBoxSize"][1]
                    ),
                width = 0
                )

            # Outline
            pygame_draw_rect(
                surface = surface,
                color = "black", 
                rect = (
                    introduction_box_positions[0], 
                    introduction_box_positions[1], 
                    self.introduction_box_dict["IntroductionBoxSize"][0],
                    self.introduction_box_dict["IntroductionBoxSize"][1]
                    ),
                width = 5)

            # Draw the image text onto the screen
            surface.blit(
                        self.introduction_box_dict["Images"][self.introduction_box_dict["IntroductionStage"] - 1],
                        (
                        introduction_box_positions[0],
                        introduction_box_positions[1]
                        )
                        )

    def draw_guide_text(self, delta_time, surface):
        
        # There can only be one guide text being drawn at a time
    
        # If there are any guide text to be drawn
        if len(self.guide_text_list) > 0:
            
            # If an original position has not been set yet
            if self.guide_text_dict["OriginalPosition"] == None:

                # Calculate the size of the font
                text_font_size = self.guide_text_dict["Font"].size(self.guide_text_list[0])

                # If the current guide text is not the game completion text
                if self.guide_text_list[0] != self.guide_text_dict["AllGuideTextMessages"]["GameCompletion"][0]:
                    # Set the position of the text to be aligned with the mid-top of the screen
                    self.guide_text_dict["OriginalPosition"] = (
                                                                (surface.get_width() / 2) - (text_font_size[0] / 2),
                                                                70
                                                                )

                # If the current guide text is the game completion text
                elif self.guide_text_list[0] == self.guide_text_dict["AllGuideTextMessages"]["GameCompletion"][0]:
                    # Set the game completion text to be in the center of the screen
                    self.guide_text_dict["OriginalPosition"] = (
                                                                (surface.get_width() / 2) - (text_font_size[0] / 2),
                                                                (surface.get_height() / 2) - (text_font_size[1] / 2)
                                                                )


                self.guide_text_dict["CurrentPosition"] = [self.guide_text_dict["OriginalPosition"][0], self.guide_text_dict["OriginalPosition"][1]]

            # If the display time for the current guide text is greater than 0
            if self.guide_text_dict["DisplayTime"] > 0:
                                                    
                # Change the current position and sin angle
                self.guide_text_dict["CurrentPosition"], self.guide_text_dict["CurrentSinAngle"] = move_item_vertically_sin(
                                                                                                                            current_sin_angle = self.guide_text_dict["CurrentSinAngle"],
                                                                                                                            angle_time_gradient = self.guide_text_dict["AngleTimeGradient"],
                                                                                                                            displacement = self.guide_text_dict["Displacement"],
                                                                                                                            original_position = self.guide_text_dict["OriginalPosition"],
                                                                                                                            current_position = self.guide_text_dict["CurrentPosition"],
                                                                                                                            delta_time = delta_time,

                                                                                                                            )

                # If the text isn't the spawn boss text or the congratulations text
                if self.guide_text_list[0] != self.guide_text_dict["AllGuideTextMessages"]["SpawnBoss"][0] and \
                    self.guide_text_list[0] != self.guide_text_dict["AllGuideTextMessages"]["GameCompletion"][0]:

                    # Reduce the display time
                    self.guide_text_dict["DisplayTime"] -= delta_time

                # Draw the text onto the surface
                draw_text(
                        text = self.guide_text_list[0], 
                        text_colour = "white", 
                        font = self.guide_text_dict["Font"],
                        x = self.guide_text_dict["CurrentPosition"][0],
                        y = self.guide_text_dict["CurrentPosition"][1],
                        surface = surface
                        )
            
            # If the display time for the current guide text is less than or equal to 0
            elif self.guide_text_dict["DisplayTime"] <= 0:
                
                # Set the display time back to its original value
                self.guide_text_dict["DisplayTime"] = self.guide_text_dict["OriginalDisplayTime"]

                # Reset the position of the guide text so the next guide text is centered properly
                self.guide_text_dict["OriginalPosition"] = None
                self.guide_text_dict["CurrentPosition"] = None

                # Remove the first guide text in the list (i.e. the current one)
                self.guide_text_list.pop(0)
                        

    # -----------------------------------------------------------------------------
    # Visual effects

    def draw_guidelines_between_a_and_b(self, a, b, guidelines_surface, main_surface, camera_position, guidelines_segments_thickness, colour):

        # Draws guidelines between the two subjects (dashed line)
    
        # The number of segments desired for the guidelines
        number_of_segments = 6

        # Calculate the distance between the a and b
        dx, dy = a[0] - b[0], a[1] - b[1]

        # Calculate the length of each segment 
        segment_length_x = dx / (number_of_segments * 2)
        segment_length_y = dy / (number_of_segments * 2)

        # Fill the guidelines surface with black. (The colour-key has been set to black)
        guidelines_surface.fill("black")

        # Draw lines
        for i in range(1, (number_of_segments * 2) + 1, 2):     
            pygame_draw_line(
                surface = guidelines_surface, 
                color = colour,
                start_pos = ((b[0] - camera_position[0]) + (segment_length_x * i), (b[1] - camera_position[1]) + (segment_length_y * i)),
                end_pos = ((b[0] - camera_position[0]) + (segment_length_x * (i + 1)), (b[1] - camera_position[1]) + (segment_length_y * (i + 1))),
                width = guidelines_segments_thickness)

        # Draw the guidelines surface onto the main surface
        main_surface.blit(guidelines_surface, (0, 0))

    def create_effect_text(self, type_of_effect_text, target, text, larger_font = False):
        
        # Creates effect text

        # --------------------------------------------------------------------------------------------------------
        # Assigning font selected and calculating the font size

        # If this effect text should not be larger
        if larger_font == False:
            # Find the font size for positioning the text properly
            font_size = self.effect_text_info_dict[type_of_effect_text]["Font"].size(text)

            # Set the font selected to be the default font
            font_selected = self.effect_text_info_dict[type_of_effect_text]["Font"]

        # If this effect text should be larger
        elif larger_font == True:
            # Find the font size for positioning the text properly
            font_size = self.effect_text_info_dict[type_of_effect_text]["LargerFont"].size(text)

            # Set the font selected to be the larger font
            font_selected = self.effect_text_info_dict[type_of_effect_text]["LargerFont"]

        # --------------------------------------------------------------------------------------------------------
        # Assigning text position

        # If the target is the boss
        if target == "Boss":
            
            # Random offset
            random_x_offset = random_randrange(-25, 25)

            # Calculate the width of the boss health bar
            boss_health_bar_width = max((self.current_boss.extra_information_dict["CurrentHealth"] / self.current_boss.extra_information_dict["MaximumHealth"] ) * self.dimensions["boss_bar"]["width"], 0)

            # Calculate the text position so that the text is centered, and then add random offsets
            text_position_x = ((self.dimensions["boss_bar"]["x"] + boss_health_bar_width) - (font_size[0] / 2)) + random_x_offset
            text_position_y = (self.dimensions["boss_bar"]["y"] + (self.dimensions["boss_bar"]["height"] / 2)) - (font_size[1] / 2)

        # If the target is the player
        elif target == "Player":

            # Temporary variables for positioning the text
            # Note: self.health_bar_positioning_information = (health_bar_measurements, green_health_bar_width)
            player_stats_display_card = self.display_cards_dict["player_stats"][0]

            # If this is a heal or damage effect text
            if type_of_effect_text == "Heal" or type_of_effect_text == "Damage":

                # Calculate the text position so that the text is centered
                text_position_x = (player_stats_display_card.health_bar_positioning_information[0][0] + player_stats_display_card.health_bar_positioning_information[1]) - (font_size[0] / 2)
                text_position_y = (player_stats_display_card.health_bar_positioning_information[0][1]) - (font_size[1] / 2)

            # If this is a bamboo resource replenishment effect text
            elif type_of_effect_text == "BambooResourceReplenishment":

                # Calculate the bamboo resource text size, so that the effect text can be placed anywhere along that text (y-pos will start at the top of the text)
                bamboo_resource_text_size = player_stats_display_card.text_font.size(player_stats_display_card.extra_information_dict["bamboo_resource_text"])

                # Set the text position
                text_position_x = ((player_stats_display_card.rect.x + (DisplayCard.border_thickness / 2) + player_stats_display_card.extra_information_dict["starting_position_from_inner_rect"][0] + player_stats_display_card.images_size[1][0] + player_stats_display_card.extra_information_dict["spacing_x_between_image_and_text"]) - (font_size[0] / 2)) + (
                    random_randrange(0, (bamboo_resource_text_size[0] / self.scale_multiplier)))
                text_position_y = ((player_stats_display_card.rect.y + (DisplayCard.border_thickness  / 2) + player_stats_display_card.extra_information_dict["starting_position_from_inner_rect"][1] + player_stats_display_card.images_size[1][1] + player_stats_display_card.extra_information_dict["spacing_y_between_stats"]) - (font_size[1] / 2))

            # If this is a frenzy mode value increment 
            elif type_of_effect_text == "FrenzyModeValueIncrement":

                # Offsets
                random_x_offset = random_randrange(0, self.dimensions["player_stats"]["frenzy_mode_bar_width"])
                random_y_offset = random_randrange(0, 35)

                # Anywhere between the starting width and ending width of the bar
                text_position_x = (self.dimensions["player_stats"]["frenzy_mode_bar_x"] - (font_size[0] / 2)) + random_x_offset

                # Positioned from the bottom of the bar with a random y offset
                text_position_y = ((self.dimensions["player_stats"]["frenzy_mode_bar_y"] + self.dimensions["player_stats"]["frenzy_mode_bar_height"]) - (font_size[1])) - random_y_offset

        # Alpha surface
        new_alpha_surface = pygame_Surface(font_size)
        new_alpha_surface.set_colorkey("black")
        new_alpha_surface.set_alpha(self.effect_text_info_dict[type_of_effect_text]["DefaultAlphaLevel"])


        # Create the effect text (Automatically added to the effect text group)
        EffectText(
                    x = text_position_x,
                    y = text_position_y,
                    colour = self.effect_text_info_dict[type_of_effect_text]["Colour"],
                    display_time = self.effect_text_info_dict[type_of_effect_text]["DisplayTime"], 
                    text = text,
                    font = font_selected,
                    alpha_surface = new_alpha_surface,
                    alpha_level = self.effect_text_info_dict[type_of_effect_text]["DefaultAlphaLevel"],
                    type_of_effect_text = type_of_effect_text
                    )

    def draw_and_update_effect_text(self):
        
        # Draws and updates the effect text
        
        # If there is any effect text to be drawn / updated
        if len(EffectText.effect_text_list) > 0:
            
            # For each effect text
            for index, effect_text in enumerate(EffectText.effect_text_list):

                # If their display time is less than 0 or equal to 0
                if effect_text.display_time <= 0:
                    # Remove it from the effect text list
                    EffectText.effect_text_list.pop(index)

                # If their display time is greater than 0
                if effect_text.display_time > 0:
                    
                    # Fill the effect text's alpha surface with black
                    effect_text.alpha_surface.fill("black")

                    # Draw the text
                    draw_text(
                        text = effect_text.text,
                        text_colour = effect_text.colour,
                        font = effect_text.font,
                        x = 0,
                        y = 0,
                        surface = effect_text.alpha_surface,
                        )

                    # Draw the alpha surface onto the main surface
                    self.surface.blit(effect_text.alpha_surface, (effect_text.x, effect_text.y))
                    
                    # Decrease the y-pos of the effect text over time
                    effect_text.y -= self.effect_text_info_dict[effect_text.type_of_effect_text]["FloatUpTimeGradient"] * self.delta_time

                    # Adjust the alpha level of the effect text's alpha surface over time
                    effect_text.alpha_level += self.effect_text_info_dict[effect_text.type_of_effect_text]["AlphaLevelTimeGradient"] * self.delta_time
                    effect_text.alpha_surface.set_alpha(round(effect_text.alpha_level))

                    # Decrease the display time
                    effect_text.display_time -= 1000 * self.delta_time

                    # ------------------------------------------------
                    # Additional properties
                    
                    # If the effect text is "Sleep":
                    if effect_text.type_of_effect_text == "Sleep":
                        # Increase the x pos of the text
                        effect_text.x += self.effect_text_info_dict[effect_text.type_of_effect_text]["FloatRightTimeGradient"] * self.delta_time

    def create_angled_polygons_effects(self, purpose, position = None, angle = None, specified_number_of_pieces = None):
        
        # Identify what angled polygon effect this is
        match purpose:

            case "Shooting":
                
                # If the current tool equppied by the player is not the "BuildingTool"
                if self.player_gameplay_info_dict["CurrentToolEquipped"] != "BuildingTool":
                    
                    # If the player has shot
                    if self.player_tools[self.player_gameplay_info_dict["CurrentToolEquipped"]]["ShootingCooldownTimer"] != None:
                        
                        # If an angled polygons controller has not been created yet
                        if hasattr(self, "angled_polygons_controller") == False:
                            # Import the angled polygons VFX
                            from VFX.AngledPolygons import AngledPolygons
                            # Create an angled polygons controller
                            self.angled_polygons_controller = AngledPolygons(surface = self.angled_polygons_surface)

                        # If this weapon is the bamboo assault rifle
                        if self.player_gameplay_info_dict["CurrentToolEquipped"] == "BambooAssaultRifle":
                            # The settings for the polygons should be as follows
                            distance_to_travel = 1 
                            time_to_travel_distance = 0.05
                            polygon_sides_angle_change = random_randrange(15, 40)
                        
                        # If this is the bamboo launcher
                        elif self.player_gameplay_info_dict["CurrentToolEquipped"] == "BambooLauncher":
                            # The settings for the polygons should be as follows
                            distance_to_travel = 10
                            time_to_travel_distance = 0.05
                            polygon_sides_angle_change = random_randrange(30, 60)

                        # Create 3 polygons, angled slightly
                        for i in range(-1, 2, 1):

                            # Extends the polygon pointing towards the shooting direction
                            polygon_extension = lambda x: x + 12 if x == 0 else 0

                            # Create angled polygons at the tip of the gun
                            self.angled_polygons_controller.create_polygons(

                                                        # The spawning position of the angled polygons
                                                        origin_point = [self.player_gameplay_info_dict["AngledPolygonsShootingSpawningPosition"][0], self.player_gameplay_info_dict["AngledPolygonsShootingSpawningPosition"][1]],
                                                    
                                                        # The angle that the main polygon will point towards, with the 2 pointing to the left / right
                                                        look_angle = degrees(self.player_gameplay_info_dict["AngledPolygonsShootingAngle"]) + (i * 45),

                                                        # The length of each polygon
                                                        hypot_length = random_randrange(10, 14) + polygon_extension(i) ,

                                                        # The angle change between each side of the polygon
                                                        polygon_sides_angle_change = polygon_sides_angle_change,
                                                        
                                                        # The distance to travel
                                                        distance_to_travel = distance_to_travel,

                                                        # The time for the polygon to travel that distance
                                                        time_to_travel_distance = time_to_travel_distance,

                                                        # The selected colour palette
                                                        colour_palette = "Shooting",

                                                        # Boolean to use BLEND_RGB_ADD
                                                        blend_rgb_add_boolean = True

                                                        )
            
            case "ShatteredBambooPieces":

                # If an angled polygons controller has not been created yet
                if hasattr(self, "angled_polygons_controller") == False:
                    # Import the angled polygons VFX
                    from VFX.AngledPolygons import AngledPolygons
                    # Create an angled polygons controller
                    self.angled_polygons_controller = AngledPolygons(surface = self.angled_polygons_surface)

                # Choose a random type of shattered bamboo pieces effect
                shattered_bamboo_pieces_effect_type = random_randrange(0, 2) 
                
                # If the type of shattered bamboo pieces effect is the 1st type and an angle has been provided (e.g. a bamboo projectile)
                if shattered_bamboo_pieces_effect_type == 0 and angle != None:

                    for i in range(0, specified_number_of_pieces):
                        # Create angled polygons at the boss
                        self.angled_polygons_controller.create_polygons(

                                                    # The spawning position of the angled polygons
                                                    origin_point = [position[0] + random_randrange(-20, 20), position[1] + random_randrange(-20, 20)],
                                                    
                                                    # The angle is the direction that the bamboo projectile was moving towards, with an offset
                                                    look_angle = degrees(angle) + random_randrange(-50, 50),

                                                    # The length of each polygon
                                                    hypot_length = random_randrange(2, 10), 

                                                    # The angle change between each side of the polygon
                                                    polygon_sides_angle_change = 40,
                                                    
                                                    # The distance to travel
                                                    distance_to_travel = random_randrange(50, 75),

                                                    # The time for the polygon to travel that distance
                                                    time_to_travel_distance = 0.5,

                                                    # The selected colour palette
                                                    colour_palette = "ShatteredBambooPieces",

                                                    # Boolean to use BLEND_RGB_ADD
                                                    blend_rgb_add_boolean = True

                                                    )
                
                # If the type of shattered bamboo pieces effect is the 2nd type or an angle has not been provided (e.g. not a bamboo projectile)
                elif shattered_bamboo_pieces_effect_type == 1 or angle == None:
                    for i in range(0, specified_number_of_pieces):
                        # Create angled polygons at the boss
                        self.angled_polygons_controller.create_polygons(

                                                    # The spawning position of the angled polygons
                                                    origin_point = [position[0] + random_randrange(-20, 20), position[1] + random_randrange(-20, 20)],
                                                    
                                                    # Angle that increases as i increases
                                                    look_angle = i * (360 / specified_number_of_pieces),

                                                    # The length of each polygon
                                                    hypot_length = random_randrange(2, 10), 

                                                    # The angle change between each side of the polygon
                                                    polygon_sides_angle_change = 40,
                                                    
                                                    # The distance to travel
                                                    distance_to_travel = random_randrange(50, 75),

                                                    # The time for the polygon to travel that distance
                                                    time_to_travel_distance = 0.5,

                                                    # The selected colour palette
                                                    colour_palette = "ShatteredBambooPieces",

                                                    # Boolean to use BLEND_RGB_ADD
                                                    blend_rgb_add_boolean = True

                                                    )
            
            case "ChilliPieces":

                # If an angled polygons controller has not been created yet
                if hasattr(self, "angled_polygons_controller") == False:
                    # Import the angled polygons VFX
                    from VFX.AngledPolygons import AngledPolygons
                    # Create an angled polygons controller
                    self.angled_polygons_controller = AngledPolygons(surface = self.angled_polygons_surface)

                for i in range(0, specified_number_of_pieces):
                    # Create angled polygons at the boss
                    self.angled_polygons_controller.create_polygons(

                                                # The spawning position of the angled polygons
                                                origin_point = [position[0] + random_randrange(-15, 15), position[1] + random_randrange(-15, 15)],
                                                
                                                # Angle that increases as i increases
                                                look_angle = i * (360 / specified_number_of_pieces),

                                                # The length of each polygon
                                                hypot_length = random_randrange(2, 5), 

                                                # The angle change between each side of the polygon
                                                polygon_sides_angle_change = 20,
                                                
                                                # The distance to travel
                                                distance_to_travel = random_randrange(50, 75),

                                                # The time for the polygon to travel that distance
                                                time_to_travel_distance = 0.5,

                                                # The selected colour palette
                                                colour_palette = "ChilliPieces",

                                                # Boolean to use BLEND_RGB_ADD
                                                blend_rgb_add_boolean = True

                                                )

    def draw_angled_polygons_effects(self, camera_position, delta_time):
        
        # Fill the angled polygons surface as black
        self.angled_polygons_surface.fill("black")

        # If there are any angled polygons to draw
        if hasattr(self, "angled_polygons_controller") and len(self.angled_polygons_controller.polygons_dict) > 0:
            # Draw the angled polygons
            self.angled_polygons_controller.draw(delta_time = delta_time, camera_position = camera_position)

        # Blit the angled polygons surface onto the main surface
        self.surface.blit(self.angled_polygons_surface, (0, 0))


    def run(self, camera_position):

        # If the player is alive
        if self.player_gameplay_info_dict["CurrentHealth"] > 0:
            # Draw the camera pan bars if the conditions are met
            # Note: This transition is only for bosses
            self.draw_camera_pan_bars()

            # If a boss has been spawned and the camera has been panned back to the player
            if self.player_gameplay_info_dict["CanStartOperating"] == True:

                # Create shooting angled polygons effects
                self.create_angled_polygons_effects(purpose = "Shooting")

                # Draw the display cards onto the screen
                self.draw_display_cards()

                # Draw the boss' health if a boss has been spawned
                self.draw_boss_health()

                # Draw the golden monkey energy indicator if the boss is the golden monkey and they have spawned
                self.draw_golden_monkey_energy_indicator()

                # Draw the player's frenzy mode bar
                self.draw_player_frenzy_mode_bar()

                # Draw and update any effect text
                self.draw_and_update_effect_text()
                
                # Draw the mouse cursor
                self.draw_mouse_cursor()