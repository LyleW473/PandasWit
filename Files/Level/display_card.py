from pygame.draw import rect as pygame_draw_rect
from pygame.draw import line as pygame_draw_line
from pygame import Rect as pygame_Rect
from Global.functions import draw_text
from pygame import Surface as pygame_Surface
from Global.settings import BAR_ALPHA_LEVEL

class DisplayCard:
    
    # Default attributes of all display cards

    # Alpha surface of the player stats display card at all times
    player_stats_alpha_surface_alpha_level = 125

    # Alpha surface for the inner and outer body
    tools_maximum_alpha_surface_alpha_level = 125
    tools_minimum_alpha_surface_alpha_level = 30

    # Alpha surface for the outlines, icon image and text
    tools_maximum_second_alpha_surface_alpha_level = 255 
    tools_minimum_second_alpha_surface_alpha_level = 125 
    
    # Thicknesses for all display cards
    border_thickness = 12
    inner_outline_thickness = 1
    outer_outline_thickness = 2

    # tools_display_card_number_text_font = ?? # This will be set when the display cards for the tools are created

    def __init__(self, rect, surface, alpha_surface, images, purpose, display_card_number = None, which_tool = None, text_font = None, extra_information_dict = None):
        
        # Main surface that the display card alpha surface is drawn onto
        self.surface = surface
        
        # The surface that the display card is drawn onto
        self.alpha_surface = alpha_surface

        # Display card's rect
        self.rect = rect
        
        # Save the purpose of this display card in an attribute
        self.purpose = purpose
        
        # If the purpose of this display card is for the players' stats e.g. Number of building tiles, amount of bamboo resource, etc.
        if purpose == "PlayerStats":

            # Images for each "stat"
            self.images = images

            # Dictionary holding extra information
            self.extra_information_dict = extra_information_dict

            # Create an attribute to keep track if the health bar alpha surface has been created
            # Note: This is so that we don't need to check if a key "health_bar_alpha_surface" exists in the extra information dict O(n) time complexity
            self.health_bar_alpha_surface_created = False

            # A list of the size of each "stat" image
            self.images_size = [self.images[i].get_size() for i in range(0, len(self.images))]

            # Font used for the stats text
            self.text_font = text_font

            # Set a colorkey and alpha level for the alpha surface
            self.alpha_surface.set_colorkey("black")
            self.alpha_surface.set_alpha(DisplayCard.player_stats_alpha_surface_alpha_level)

        # If the purpose of this display card is for the players' tools
        elif purpose == "PlayerTools":
            # Set the image to be the icon image
            self.image = images

            # The tool this display card represents
            self.which_tool = which_tool

            # Set the display card number
            self.display_card_number = display_card_number

            # Alpha surface for the inner body and outer body
            self.alpha_surface.set_colorkey("black")
            self.alpha_surface.set_alpha(DisplayCard.tools_maximum_alpha_surface_alpha_level)

            # Second alpha surface for the outlines, icon image and text
            self.second_alpha_surface = pygame_Surface((self.rect.width + (DisplayCard.outer_outline_thickness * 2), self.rect.height + (DisplayCard.outer_outline_thickness * 2)))
            self.second_alpha_surface.set_colorkey("blue")
            self.second_alpha_surface.set_alpha(DisplayCard.tools_maximum_second_alpha_surface_alpha_level)

    # --------------------------------------------
    # Common methods

    def draw_inner_and_outer_body(self):

        # ------------------------------
        # Drawing the outer body
        pygame_draw_rect(
                        surface = self.alpha_surface, 
                        color = (78, 159, 61),
                        rect = pygame_Rect(0, 0, self.rect.width, self.rect.height), 
                        width = 0)

        # ------------------------------
        # Inner body rect
        inner_body_rect = pygame_Rect(
                        0 + (DisplayCard.border_thickness / 2), 
                        0 + (DisplayCard.border_thickness  / 2), 
                        self.rect.width - DisplayCard.border_thickness,
                        self.rect.height - DisplayCard.border_thickness
                                )
        
        # Drawing the inner body
        pygame_draw_rect(surface = self.alpha_surface, color = (168, 232, 144), rect = inner_body_rect, width = 0) #(168, 232, 144)

        # Return the inner body rect
        return inner_body_rect

    def draw_outlines(self, inner_body_rect):

        # If this is a player stats display card
        if self.purpose == "PlayerStats":

            # Inner body outline (Other approach would be creating a new rect and inflating it in place with 2 * the inner outline thickness)
            # Note: This uses the inner body rect's starting position on the screen and moves back by the inner outline thickness, increasing the height and width of the entire rect by the (inner outline thickness * 2).
            pygame_draw_rect(
                            surface = self.surface,
                            color = "white", 
                            rect = pygame_Rect(
                                                (self.rect.x + inner_body_rect.x) - DisplayCard.inner_outline_thickness,
                                                (self.rect.y + inner_body_rect.y) - DisplayCard.inner_outline_thickness, 
                                                inner_body_rect.width + (DisplayCard.inner_outline_thickness * 2), 
                                                inner_body_rect.height + (DisplayCard.inner_outline_thickness * 2)),
                            width = DisplayCard.inner_outline_thickness 
                        )

            # Outer body outline
            pygame_draw_rect(
                            surface = self.surface,
                            color = "black", 
                            rect = (
                                    self.rect.x - DisplayCard.outer_outline_thickness,
                                    self.rect.y - DisplayCard.outer_outline_thickness,
                                    self.rect.width + (DisplayCard.outer_outline_thickness * 2),
                                    self.rect.height + (DisplayCard.outer_outline_thickness * 2),
                                ),
                            width = DisplayCard.outer_outline_thickness
                            )
        
        # If this is a player tools display card
        elif self.purpose == "PlayerTools":

            # Inner body outline
            pygame_draw_rect(
                            surface = self.second_alpha_surface,
                            color = "white", 
                            rect = pygame_Rect(
                                                ((inner_body_rect.x) - DisplayCard.inner_outline_thickness) + DisplayCard.outer_outline_thickness, # Outer outline thickness the second alpha surface includes the outer outlines
                                                ((inner_body_rect.y) - DisplayCard.inner_outline_thickness) + DisplayCard.outer_outline_thickness,
                                                inner_body_rect.width + (DisplayCard.inner_outline_thickness * 2), 
                                                inner_body_rect.height + (DisplayCard.inner_outline_thickness * 2)
                                                ),
                            width = DisplayCard.inner_outline_thickness
                        )
            # pygame_draw_rect(surface = self.second_alpha_surface, color = "purple", rect = inner_body_rect, width = 0) #colour (120, 120, 120)

            # Outer body outline
            pygame_draw_rect(
                            surface = self.second_alpha_surface,
                            color = "black", 
                            rect = (
                                    0,
                                    0,
                                    self.rect.width + (DisplayCard.outer_outline_thickness * 2),
                                    self.rect.height + (DisplayCard.outer_outline_thickness * 2),
                                ),
                            width = DisplayCard.outer_outline_thickness,

                            )
    # --------------------------------------------
    # Specific methods for different purposes

    def draw_tool_display_card_contents(self, inner_body_rect):

        # --------------------------------------------
        # Draw the icon image at the center of the display card  

        # Distance between center of the inner rect minus the center of the icon image
        dx = inner_body_rect.centerx - (self.image.get_width() / 2)
        dy = inner_body_rect.centery - (self.image.get_height() / 2)

        # Blit the icon image at the center of the second alpha surface
        self.second_alpha_surface.blit(
                        self.image, 
                        ((dx, dy))
                        )
        
        # Draw the display card number
        draw_text(
                text = str(self.display_card_number),
                font = DisplayCard.tools_display_card_number_text_font,
                text_colour = "white", 
                x = (inner_body_rect.width) - 2, # -2 is an offset
                y = (DisplayCard.border_thickness / 2) + 2, # + 2 is an offset
                surface = self.second_alpha_surface,
                )
 
    def draw_stats_display_card_contents(self, inner_body_rect, player_tools, player_gameplay_info_dict):

        # -----------------------------------------------------------------
        # Drawing the amount of existing building tiles that the player has

        # Position that the building tile image
        building_tile_image_position = (
                                        self.rect.x + inner_body_rect.x + self.extra_information_dict["starting_position_from_inner_rect"][0], 
                                        self.rect.y + inner_body_rect.y + self.extra_information_dict["starting_position_from_inner_rect"][1]
                                    )

        # Draw the building tile image 
        self.surface.blit(self.images[0], building_tile_image_position)

        # The text that displays how many building tiles exist inside the map currently
        existing_building_tiles_text = f'Number of tiles: {len(player_tools["BuildingTool"]["ExistingBuildingTilesList"])}/{player_tools["BuildingTool"]["MaximumNumberOfTilesAtOneTime"]}'

        # Draw the text displaying the number of building tiles that exist inside the map currently
        draw_text(
                text = existing_building_tiles_text, 
                text_colour = "white",
                font = self.text_font,
                x = building_tile_image_position[0] + self.images_size[0][0] + self.extra_information_dict["spacing_x_between_image_and_text"], # self.images_size[1][0] = image width
                y = building_tile_image_position[1],
                surface = self.surface, 
                scale_multiplier = self.extra_information_dict["scale_multiplier"]
                )

        # -----------------------------------------------------------------
        # Drawing the amount of bamboo resource that the player has (used for ammo and building tiles)

        bamboo_resource_image_position = (
                    building_tile_image_position[0],
                    building_tile_image_position[1] + self.images_size[1][1] + self.extra_information_dict["spacing_y_between_stats"])

        # Building tile image 
        self.surface.blit(self.images[1], bamboo_resource_image_position)

        # The text that displays how much bamboo resource the player has
        amount_of_bamboo_resource_text = f'Bamboo: {player_gameplay_info_dict["AmountOfBambooResource"]} / {player_gameplay_info_dict["MaximumAmountOfBambooResource"]}'
        # Save the text inside the dictionary so that the effect text can be positioned randomly across the text 
        self.extra_information_dict["bamboo_resource_text"] = amount_of_bamboo_resource_text

        # Draw the text displaying the amount of bamboo resource
        draw_text(
                text = amount_of_bamboo_resource_text, 
                text_colour = "white",
                font = self.text_font,
                x = bamboo_resource_image_position[0] + self.images_size[1][0] + self.extra_information_dict["spacing_x_between_image_and_text"],
                y = bamboo_resource_image_position[1],
                surface = self.surface, 
                scale_multiplier = self.extra_information_dict["scale_multiplier"]
                )
        
        # -----------------------------------------------------------------
        # Drawing the health bar

        # Player's health bar

        # Difference between the bottom of the inner body rect and the bottom of the last 
        bottom_of_inner_body_rect = self.rect.y + (inner_body_rect.y + inner_body_rect.height)
        bottom_of_final_stat = (bamboo_resource_image_position[1] + self.images_size[1][1])
    
        dy = bottom_of_inner_body_rect - bottom_of_final_stat
        displacement_from_bottom_of_final_stat = (dy - self.extra_information_dict["health_bar_height"]) / 2

        health_bar_measurements = (
                                bamboo_resource_image_position[0], # x
                                bottom_of_final_stat + displacement_from_bottom_of_final_stat, # y
                                inner_body_rect.width - (self.extra_information_dict["starting_position_from_inner_rect"][0] * 2), # width
                                self.extra_information_dict["health_bar_height"] # height
                               )

        # If a health bar alpha surface has not been created
        if self.health_bar_alpha_surface_created == False:
            # Create the health bar alpha surface and set an alpha level and color key
            self.extra_information_dict["health_bar_alpha_surface"] = pygame_Surface((health_bar_measurements[2], self.extra_information_dict["health_bar_height"]))
            self.extra_information_dict["health_bar_alpha_surface"].set_colorkey("black")
            self.extra_information_dict["health_bar_alpha_surface"].set_alpha(BAR_ALPHA_LEVEL)

            # Set this attribute to True so that another health bar alpha surface is not created
            self.health_bar_alpha_surface_created = True

        # Empty health bar
        pygame_draw_rect(
                        surface = self.extra_information_dict["health_bar_alpha_surface"],
                        color = "gray21", # "dimgray"
                        rect = (
                                0, 
                                0,
                                health_bar_measurements[2],
                                health_bar_measurements[3]
                                ),
                        width = 0,
                        border_radius = self.extra_information_dict["health_bar_border_radius"]
                        )
        # -----------------------------------------
        # Changing health bar

        # The width should be the percentage of the current health compared to the maximum health, multiplied by the default health bar width
        # Limit the width to be 0 if the player's current health is negative
        green_health_bar_width = max((player_gameplay_info_dict["CurrentHealth"] / player_gameplay_info_dict["MaximumHealth"]) * health_bar_measurements[2], 0)

        # Update the text that will be displayed on the screen depending on the player's current health
        players_health_text = f'{max(player_gameplay_info_dict["CurrentHealth"], 0)} / {player_gameplay_info_dict["MaximumHealth"]}'

        # Calculate the font size, used to position the text at the center of the health bar
        players_health_text_font_size = self.text_font.size(players_health_text)

        # Save the health bar positioning information to grant access to the game UI to create effect text for the player
        self.health_bar_positioning_information = (health_bar_measurements, green_health_bar_width)

        # First half of the current health bar
        pygame_draw_rect(
                        surface = self.extra_information_dict["health_bar_alpha_surface"],
                        color = (0, 128, 0), 
                        rect = (
                                0, 
                                0, 
                                green_health_bar_width,
                                (health_bar_measurements[3] / 2)
                                ),
                        width = 0,
                        border_radius = self.extra_information_dict["health_bar_border_radius"]
                        )      

        # Second half of the current health bar
        pygame_draw_rect(
                        surface = self.extra_information_dict["health_bar_alpha_surface"],
                        color = "green4", 
                        rect = (
                                0, 
                                0 + (health_bar_measurements[3] / 2), 
                                green_health_bar_width,
                                (health_bar_measurements[3] / 2) 
                                ),
                        width = 0,
                        border_radius = self.extra_information_dict["health_bar_border_radius"]
                        )      

        # Only draw the edge when the width of the health bar is greater than 0
        if green_health_bar_width > 0:

            # Edge at the end of the changing part of the player's health
            pygame_draw_line(
                            surface = self.extra_information_dict["health_bar_alpha_surface"], 
                            color = (0, 150, 0),
                            start_pos = ((0 + green_health_bar_width) - (self.extra_information_dict["changing_health_bar_edge_thickness"] / 2), 0),
                            end_pos = ((0 + green_health_bar_width) - (self.extra_information_dict["changing_health_bar_edge_thickness"] / 2), 0 + health_bar_measurements[3]),
                            width = self.extra_information_dict["changing_health_bar_edge_thickness"]
                            )

        # --------------------------------------
        # Draw the alpha surface onto the main surface
        self.surface.blit(self.extra_information_dict["health_bar_alpha_surface"], (health_bar_measurements[0], health_bar_measurements[1]))

        # -----------------------------------------
        # Health bar outer outline
        
        pygame_draw_rect(
                        surface = self.surface,
                        color = "black", 
                        rect = (
                                health_bar_measurements[0] - self.extra_information_dict["health_bar_outline_thickness"], 
                                health_bar_measurements[1] - self.extra_information_dict["health_bar_outline_thickness"], 
                                health_bar_measurements[2] + (self.extra_information_dict["health_bar_outline_thickness"] * 2),
                                health_bar_measurements[3] + (self.extra_information_dict["health_bar_outline_thickness"] * 2)
                                ),
                        width = self.extra_information_dict["health_bar_outline_thickness"],
                        border_radius = self.extra_information_dict["health_bar_border_radius"]
                        )
        
        # -----------------------------------------
        # Player health text

        # Draw the text displaying the player's health
        draw_text(
                text = players_health_text, 
                text_colour = "white",
                font = self.text_font,
                x = (health_bar_measurements[0] + (health_bar_measurements[2] / 2)) - ((players_health_text_font_size[0] / self.extra_information_dict["scale_multiplier"]) / 2),
                y = (health_bar_measurements[1] + (health_bar_measurements[3] / 2)) - ((players_health_text_font_size[1] / self.extra_information_dict["scale_multiplier"]) / 2),
                surface = self.surface, 
                scale_multiplier = self.extra_information_dict["scale_multiplier"]
                )
        
    # --------------------------------------------
    # Main draw method
    
    def draw(self, player_tools = None, player_gameplay_info_dict = None):

        # Fill the alpha surface with black
        self.alpha_surface.fill("black")

        # --------------------------------------------
        # Draw the inner and outer body, save the returned inner body rect for positioning other elements of the display card
        inner_body_rect = self.draw_inner_and_outer_body()

        # --------------------------------------------
        # Draw the alpha surface onto the main surface
        self.surface.blit(self.alpha_surface, (self.rect.x, self.rect.y))

        # If this display card is for the players' tools
        if self.purpose == "PlayerTools":
            
            # Fill the second alpha surface with blue
            self.second_alpha_surface.fill("blue")

            # Draw the outlines onto the second alpha surface
            self.draw_outlines(inner_body_rect = inner_body_rect)

            # Draw the contents of the tool display card
            self.draw_tool_display_card_contents(inner_body_rect = inner_body_rect)

            # Blit the second alpha surface onto the main surface
            self.surface.blit(self.second_alpha_surface, (self.rect.x - DisplayCard.outer_outline_thickness, self.rect.y - DisplayCard.outer_outline_thickness))

        # If this display card is for the players' stats
        elif self.purpose == "PlayerStats":
            # Draw the contents of the stats display card
            self.draw_stats_display_card_contents(inner_body_rect = inner_body_rect, player_tools = player_tools, player_gameplay_info_dict = player_gameplay_info_dict)

            # --------------------------------------------
            # Outlines
            self.draw_outlines(inner_body_rect = inner_body_rect)
