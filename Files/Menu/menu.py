from sys import exit as sys_exit
from Menu.button import Button
from Global.settings import * 
from pygame.display import get_surface as pygame_display_get_surface
from pygame.font import Font as pygame_font_Font
from pygame.mouse import get_pos as pygame_mouse_get_pos
from pygame.mouse import get_pressed as pygame_mouse_get_pressed
from pygame import Rect as pygame_Rect
from pygame import quit as pygame_quit
from pygame.mouse import set_visible as pygame_mouse_set_visible
from pygame.draw import rect as pygame_draw_rect
from pygame.image import load as pygame_image_load
from Global.functions import draw_text, move_item_vertically_sin

class Menu:
    def __init__(self):

        # Screen
        self.surface = pygame_display_get_surface()
    
        # ------------------------------------------------------------------------------------------------------------------------------------------------

        # Game states

        """ Existing menus:
        - Main
        - Controls
        - Paused
        """

        # Stores the current menu that should be shown to the player
        self.current_menu = "main_menu"
        
        # Store the previous menu so that we can go back to previous menus when the "Back" button is clicked
        self.previous_menu = None 

        # Stores the menu to transition to
        self.transition_to_which_menu = "Nothing"

        # Stores whether the player decided to exit the session, in that case the game would need to be reset again
        self.session_exit = False

        # ------------------------------------------------------------------------------------------------------------------------------------------------
        # Mouse
        self.left_mouse_button_released = True # Attribute used to track if the left mouse button is released so that 

        # ------------------------------------------------------------------------------------------------------------------------------------------------
        # Buttons

        # Create the buttons
        self.create_buttons()

        # ------------------------------------------------------------------------------------------------------------------------------------------------
        # Title text    

        self.title_text = "Panda's Wit"
        self.title_text_font = pygame_font_Font("graphics/Fonts/menu_buttons_font.ttf", 140)
        self.title_text_font_size = self.title_text_font.size(self.title_text)
        self.title_text_current_sin_angle = 0
        self.title_text_displacement = 15
        self.title_text_original_position = (
                                            (self.surface.get_width() / 2) - (self.title_text_font_size[0] / 2),
                                            250 - (self.title_text_font_size[1] / 2)
                                            )
        self.title_text_current_position = [self.title_text_original_position[0], self.title_text_original_position[1]]
        self.title_text_angle_time_gradient = 360 / 3.5


        """ 'Hidden' attributes:
        self.controls_menu_dict
        """


    def create_buttons(self):

        # Width and height of buttons
        default_button_measurements = (500, 90)

        # Value for button spacing
        button_spacing =  (0, 150)

        """A dictionary used to contain all the information for each menu:
        - Each menu:
            - The purpose of each button
            - A buttons list to store the created buttons
            - The starting positions of the buttons
            - The button spacing between each 
        """
        self.menu_buttons_dict = {
            
            "main_menu": {"ButtonPurposes": ("Play", "Controls", "Quit"), "ButtonsList": [], "StartingPositions": (screen_width / 2, 450), "ButtonSpacing": button_spacing},
            "paused_menu": {"ButtonPurposes": ("Continue", "Controls", "Exit session"), "ButtonsList": [], "StartingPositions": (screen_width / 2, 350), "ButtonSpacing": button_spacing},
            "controls_menu": {"ButtonPurposes": ["Back"], "ButtonsList": [], "StartingPositions": (screen_width / 2, screen_height - 150), "ButtonSpacing": (0, 0)},
            "restart_menu": {"ButtonPurposes": ["Return to main menu", "Quit"], "ButtonsList": [], "StartingPositions": (screen_width / 2, 350), "ButtonSpacing": button_spacing}
                                    }

        # Index of the last button changed (i.e. the buttons' alpha level and size)
        self.index_of_last_button_changed = None

        # ------------------------------------------------------------------------

        # For each menu
        for menu in self.menu_buttons_dict:

            # For each button purpose in the list of button purposes 
            for index, button_purpose in enumerate(self.menu_buttons_dict[menu]["ButtonPurposes"]):
                
                """  Create the button, passing parameters:
                - A rect info dict containing the x and y positions and the measurements of the button 
                - The purpose of the button (e.g. "Play" button)
                - The font of the button text and the size
                - The surface that the button will be drawn onto
                """
                self.menu_buttons_dict[menu]["ButtonsList"].append(
                                            Button(
                                                rect_info_dict = {
                                                                    "x": self.menu_buttons_dict[menu]["StartingPositions"][0], 
                                                                    "y" : self.menu_buttons_dict[menu]["StartingPositions"][1] + (self.menu_buttons_dict[menu]["ButtonSpacing"][1] * index) ,
                                                                    "button_measurements": default_button_measurements}, 
                                                purpose = button_purpose,
                                                text_font = pygame_font_Font("graphics/Fonts/menu_buttons_font.ttf", 50),
                                                surface = self.surface
                                                )
                                            )

    def mouse_position_updating(self):

        # Creates a mouse rect and updates the mouse rect depending on the mouse position 

        # Retrieve the mouse position
        self.mouse_position = pygame_mouse_get_pos()

        # If a mouse rect has not been created already
        if hasattr(self, "mouse_rect") == False:
            # Create the mouse rect
            self.mouse_rect = pygame_Rect(self.mouse_position[0], self.mouse_position[1], 1, 1)
        # If a mouse rect already exists
        else:
            # Update the x and y positions of the mouse rect
            self.mouse_rect.x, self.mouse_rect.y = self.mouse_position[0], self.mouse_position[1]

    def update_buttons(self, menu_buttons_list):

        """
        - Updates delta time of buttons
        - Performs changes on the size and alpha level of the buttons if hovered over
        - Draws the button onto the main surface
        - Highlights the button if hovered over
        - Plays the border animations for the buttons
        """
        
        # For all buttons in the menu's button list
        for button in menu_buttons_list:

            # Update the delta time of the button
            button.delta_time = self.delta_time

            # If the mouse is currently hovering over the button
            if self.mouse_rect.colliderect(button.rect) == True:
                # Increase the size and alpha level of the button
                button.change_button_size(inflate = True)
                button.change_alpha_level(increase = True)

            # If the mouse is not currently hovering over the button
            elif self.mouse_rect.colliderect(button.rect) == False:
                # Reset the alpha level and button size if not already reset
                button.change_button_size(inflate = False)
                button.change_alpha_level(increase = False)

            # Draw the button
            button.draw()

            # Highlight the button if the player's mouse is hovering over the button
            button.highlight(mouse_rect = self.mouse_rect)

            # Play the button's border animation
            button.play_border_animations()

    def draw_title(self, delta_time):
        
        # Change the current position and sin angle
        self.title_text_current_position, self.title_text_current_sin_angle = move_item_vertically_sin(
                                                                                                        current_sin_angle = self.title_text_current_sin_angle,
                                                                                                        angle_time_gradient = self.title_text_angle_time_gradient,
                                                                                                        displacement = self.title_text_displacement,
                                                                                                        original_position = self.title_text_original_position,
                                                                                                        current_position = self.title_text_current_position,
                                                                                                        delta_time = delta_time,

                                                                                                        )
        
        # Draw the text onto the surface
        draw_text(
                text = self.title_text,
                text_colour = "white", 
                font = self.title_text_font,
                x = self.title_text_current_position[0],
                y = self.title_text_current_position[1],
                surface = self.surface
                )

    def run(self, delta_time):

        # Update delta time 
        self.delta_time = delta_time

        # Retrieve the mouse position and update the mouse rect
        self.mouse_position_updating()

        # Check if the left mouse button has been released, and if it has, set the attribute to True
        if pygame_mouse_get_pressed()[0] == 0:
            self.left_mouse_button_released = True

        # Fill the surface with a colour
        self.surface.fill((40, 40, 40))

        # ---------------------------------------------
        # Main menu

        if self.current_menu == "main_menu": 

            # Draw the title
            self.draw_title(delta_time = delta_time)

            # Draw and update the buttons
            self.update_buttons(menu_buttons_list = self.menu_buttons_dict["main_menu"]["ButtonsList"])

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame_mouse_get_pressed()[0] == True and self.left_mouse_button_released == True:

                    # Set the left mouse button as not released
                    self.left_mouse_button_released = False   

                    # Look for collisions between the mouse rect and the rect of any button inside the list
                    button_collision = self.mouse_rect.collidelist(self.menu_buttons_dict["main_menu"]["ButtonsList"])

                    # If the player did not click on empty space
                    # Note: This check is so that we check the purpose of the button at index -1
                    if button_collision != -1:

                        # Check for which button was clicked by looking at the purpose of the button
                        match self.menu_buttons_dict["main_menu"]["ButtonsList"][button_collision].purpose:
                            
                            # If the mouse collided with the "Play" button 
                            case "Play":
                                # Set the mouse to be invisible
                                pygame_mouse_set_visible(False)
                                
                                # Transition into the game
                                self.transition_to_which_menu = "game"

                            # If the mouse collided with the "Controls" button 
                            case "Controls":

                                # Transition to the controls menu
                                self.transition_to_which_menu = "controls_menu"
                                # Set the previous menu to be this menu so that we can come back to this menu when the "Back" button is clicked
                                self.previous_menu = "main_menu"

                            # If the mouse collided with the "Quit" button 
                            case "Quit":
                                # Exit the program
                                pygame_quit()
                                sys_exit()

        # ---------------------------------------------
        # Controls menu

        elif self.current_menu == "controls_menu":

            # Draw and update the buttons
            self.update_buttons(menu_buttons_list = self.menu_buttons_dict["controls_menu"]["ButtonsList"])

            # If this dict does not exist yet
            if hasattr(self, "controls_menu_dict") == False:
                # Create it
                self.controls_menu_dict = {
                                        "Image": pygame_image_load("graphics/Misc/ControlsDisplay.png").convert_alpha(),
                                        "BoxSize": (1000, 600),
                                        }

            # Calculate the box positions for the controls
            controls_box_positions = (
                                    (self.surface.get_width() / 2) - (self.controls_menu_dict["BoxSize"][0] / 2), 
                                    (self.surface.get_height() / 2.5) - (self.controls_menu_dict["BoxSize"][1] / 2), 
                                    )

            # Body
            pygame_draw_rect(
                            surface = self.surface, 
                            color = (113, 179, 64),
                            rect = (
                                    controls_box_positions[0],
                                    controls_box_positions[1],
                                    self.controls_menu_dict["BoxSize"][0],
                                    self.controls_menu_dict["BoxSize"][1]
                                    ), 
                            width = 0
                            )
            
            # Outline
            pygame_draw_rect(
                            surface = self.surface, 
                            color = "black",
                            rect = (
                                    controls_box_positions[0],
                                    controls_box_positions[1],
                                    self.controls_menu_dict["BoxSize"][0],
                                    self.controls_menu_dict["BoxSize"][1]
                                    ), 
                            width = 10
                            )

            self.surface.blit(
                            self.controls_menu_dict["Image"],
                            controls_box_positions

                            )

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame_mouse_get_pressed()[0] == 1 and self.left_mouse_button_released == True:

                # Set the left mouse button as not released
                self.left_mouse_button_released = False          

                # Look for collisions between the mouse rect and the rect of any button inside the list
                button_collision = self.mouse_rect.collidelist(self.menu_buttons_dict["controls_menu"]["ButtonsList"])

                # If the player did not click on empty space
                # Note: This check is so that we check the purpose of the button at index -1
                if button_collision != -1:

                    # Check for which button was clicked
                    match self.menu_buttons_dict["controls_menu"]["ButtonsList"][button_collision].purpose:
                        
                        # If the mouse collided with the "Back" button
                        case "Back":

                            # Check which menu the controls menu was entered from
                            match self.previous_menu:        

                                # From the main menu
                                case "main_menu":
                                    # Transition to the main menu
                                    self.transition_to_which_menu = "main_menu"
                                
                                # From the paused menu
                                case "paused_menu":
                                    # Transition to the paused menu
                                    self.transition_to_which_menu = "paused_menu"
        
        # ---------------------------------------------
        # Paused menu

        elif self.current_menu == "paused_menu":

            # Draw and update the buttons
            self.update_buttons(menu_buttons_list = self.menu_buttons_dict["paused_menu"]["ButtonsList"])

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame_mouse_get_pressed()[0] == 1 and self.left_mouse_button_released == True:

                # Set the left mouse button as not released
                self.left_mouse_button_released = False          

                # Look for collisions between the mouse rect and the rect of any button inside the list
                button_collision = self.mouse_rect.collidelist(self.menu_buttons_dict["paused_menu"]["ButtonsList"])

                # If the player did not click on empty space
                # Note: This check is so that we check the purpose of the button at index -1
                if button_collision != -1:

                    # Check for which button was clicked
                    match self.menu_buttons_dict["paused_menu"]["ButtonsList"][button_collision].purpose:

                        # If the mouse collided with the "Continue" button
                        case "Continue": 
                            # Transition back to the game
                            self.transition_to_which_menu = "game"

                        # If the mouse collided with the "Controls" button
                        case "Controls":

                            # Transition to the controls menu
                            self.transition_to_which_menu = "controls_menu"
                            # Set the previous menu to be this menu so that we can come back to this menu when the "Back" button is clicked
                            self.previous_menu = "paused_menu"

                        # If the mouse collided with the "Exit session" button 
                        case "Exit session":
                            # Transition to the main menu
                            self.transition_to_which_menu = "main_menu"

                            # Set this attribute to True, allowing for the game to be reset again
                            self.session_exit = True

        # ---------------------------------------------
        # Restart menu

        elif self.current_menu == "restart_menu":

            # Draw and update the buttons
            self.update_buttons(menu_buttons_list = self.menu_buttons_dict["restart_menu"]["ButtonsList"])

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame_mouse_get_pressed()[0] == 1 and self.left_mouse_button_released == True:

                # Set the left mouse button as not released
                self.left_mouse_button_released = False          

                # Look for collisions between the mouse rect and the rect of any button inside the list
                button_collision_index = self.mouse_rect.collidelist(self.menu_buttons_dict["restart_menu"]["ButtonsList"])

                # If the player did not click on empty space
                # Note: This check is so that we check the purpose of the button at index -1
                if button_collision_index != -1:

                    # Check for which button was clicked
                    match self.menu_buttons_dict["restart_menu"]["ButtonsList"][button_collision_index].purpose:

                        # If the mouse collided with the "Return to main menu" button
                        case "Return to main menu":
                            
                            # Set the transition to which menu attribute to be the main menu (That way the menu will be changed during the lock in time of the transition)
                            self.transition_to_which_menu = "main_menu"

                        # If the mouse collided with the "Quit" button 
                        case "Quit":
                            # Exit the program
                            pygame_quit()
                            sys_exit()