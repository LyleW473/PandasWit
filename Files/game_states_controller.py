from pygame.display import set_mode as pygame_display_set_mode
from pygame import SCALED as pygame_SCALED
from pygame import FULLSCREEN as pygame_FULLSCREEN
from pygame import HWSURFACE as pygame_HWSURFACE
from pygame.mouse import set_visible as pygame_mouse_set_visible, get_visible as pygame_mouse_get_visible
from pygame.event import get as pygame_event_get
from pygame import QUIT as pygame_QUIT
from pygame import quit as pygame_quit
from pygame import KEYDOWN as pygame_KEYDOWN
from pygame import K_ESCAPE as pygame_K_ESCAPE
from pygame import K_F11 as pygame_K_F11
from pygame import K_1 as pygame_K_1
from pygame import K_2 as pygame_K_2
from pygame import K_3 as pygame_K_3
from pygame import K_SPACE as pygame_K_SPACE
from sys import exit as sys_exit
from Global.settings import screen_width, screen_height
from Menu.menu import Menu
from Level.game import Game
from pygame.draw import rect as pygame_draw_rect

class GameStatesController():
    def __init__(self):

        # Screen
        # Set the screen to be full screen 
        self.surface = pygame_display_set_mode((screen_width, screen_height), flags = pygame_SCALED + pygame_FULLSCREEN + pygame_HWSURFACE)

        self.full_screen = True

        # Game states
        self.menu = Menu()
        self.game = Game() # The actual level
        
        # Attribute so that we only load the level once, and not every frame
        self.level_loaded = False

        # ------------------------------------------------------------------------------------------------------------------------------------------------
        # Restart menu functionality

        # -----------------------------
        # Black bars

        # The height of the black bars
        self.bar_height = 0

        self.bar_height_change_time = 125
        self.bar_lock_in_time = 225 

        # The total transition time should be: The time it takes to increase and decrease the black bar height, and the lock in time
        self.bar_transition_time = (self.bar_height_change_time * 2) + self.bar_lock_in_time
        self.bar_transition_timer = None

        # The rate of change of the height over time
        self.bar_height_time_gradient = ((self.surface.get_height() / 2) - 0) / (self.bar_height_change_time / 1000)
        
        # A variable to store the new height (floating point accuracy)
        self.bar_new_height = 0

        # A variable that stores which menu is being transitioned to
        self.transition_where = "Nothing"
        """ Possible locations:
        "Nothing" = Nothing
        "Game" = The game / level
        The names of the menus = any menu
        
        """


    def load_level(self, chosen_level_number):
        # Note: Load level is here because in the future, a level select menu may be added (which will be inside the Menu class), so we need to retrieve the level selected from the Menu class and then pass it to the actual level (i.e. Game)
        
        # If we haven't loaded the level for the game yet
        if self.level_loaded == False:

            # ------------------------------------------------------------------------
            # Loading the tile map from the level tile maps text file

            # Open the text file which holds 
            with open("Files/Level/level_tile_maps.txt", "r") as level_tile_maps_file:
                
                for line_number, tile_map in enumerate(level_tile_maps_file.readlines()):
                    # If the line number is equal to the chosen level minus one (This is because the tile maps are zero indexed in order)
                    if line_number == (chosen_level_number - 1):
                        # [1:-1] to get rid of the "?" separator and the "\n" line break for each tile map
                        tile_map_to_convert = tile_map[1:-1]

            # ----------------------------------------------------------------------------------------
            # Convert the tile map into a series of tile numbers, so that inside the level, we can create objects 


            non_transformed_tile_map = [] # Holds the tile map of the tile's numbers
            tile_number = "" # Used as some tiles may have double digit tile numbers
            row_of_tiles_list = [] # Used to hold all the tiles in one row

            # For all characters in the tile map
            for i in range(0, len(tile_map_to_convert)):
                
                # Identify what the character is
                match tile_map_to_convert[i]:

                    # Comma separator
                    case ",":
                    
                        # Add the row of tiles to the final tile map
                        non_transformed_tile_map.append(row_of_tiles_list)

                        # Empty the row of tiles list
                        row_of_tiles_list = []

                    # Exclamation mark separator
                    case "!":
                        # Add the tile number to the row of tiles 
                        row_of_tiles_list.append(int(tile_number))

                        # Reset the tile number
                        tile_number = ""

                    # If it is neither a comma separator or an exclamation mark separator
                    case _: # Can also be "case other"
                        tile_number += tile_map_to_convert[i]

            # Create the level's object tile map, which is a tile map consisting of the objects (the actual game tile map)
            self.game.create_objects_tile_map(non_transformed_tile_map)

            # Set the level loaded attribute to True
            self.level_loaded = True
            
    def event_loop(self):

        # Event handler
        for event in pygame_event_get():
                
            # Identify the type of event
            match event.type:
                
                # Exit button on the window clicked
                case _ if event.type == pygame_QUIT:

                    # Close the program
                    pygame_quit()
                    sys_exit()

                # Key presses
                case _ if event.type == pygame_KEYDOWN:

                    # ------------------------------------------------------------
                    # Universal events
                    
                    # Find which key was pressed
                    match event.key:
                        
                        # "F11" key
                        case _ if event.key == pygame_K_F11:
                            
                            # Changing from full screen to windowed mode
                            if self.full_screen == True:
                                
                                # Change to windowed mode
                                self.surface = pygame_display_set_mode((screen_width, screen_height), pygame_HWSURFACE)
                                self.full_screen = False

                            # Changing from windowed to full screen mode
                            elif self.full_screen == False:
                                
                                # Change to full screen mode
                                self.surface = pygame_display_set_mode((screen_width, screen_height), pygame_SCALED + pygame_FULLSCREEN + pygame_HWSURFACE)
                                self.full_screen = True

                    # ------------------------------------------------------------
                    # In-game / Level events

                    if self.menu.current_menu == "game":
                        
                        # Find which key was pressed
                        match event.key:
                            
                            # "Space" key
                            case _ if event.key == pygame_K_SPACE:
                                # If this dict exists
                                if hasattr(self.game.game_ui, "introduction_box_dict"):
                                    # Go to the next introduction stage
                                    self.game.game_ui.introduction_box_dict["IntroductionStage"] += 1

                                    # If the player has reached the final stage
                                    if self.game.game_ui.introduction_box_dict["IntroductionStage"] > 2:
                                        # Set the introduction as completed
                                        self.game.game_ui.introduction_box_dict["IntroductionCompleted"] = True


                            # "Esc" key
                            case _ if event.key == pygame_K_ESCAPE:

                                # If the program is not already transitioning to the paused menu
                                if self.bar_transition_timer == None:

                                    # Set the mouse cursor back to visible
                                    pygame_mouse_set_visible(True)
                        
                                    # Transition to the paused menu (the menu's current menu will be set to "paused_menu")
                                    self.transition_where = "paused_menu"

                                    # Start the transition timer
                                    self.bar_transition_timer = self.bar_transition_time
                            
                            # "1" key
                            case _ if event.key == pygame_K_1:
                                # Switch the player's tool to the building tool
                                self.game.player.switch_tool(tool = "BuildingTool")
                            # "2" key
                            case _ if event.key == pygame_K_2:
                                # Switch the player's tool to the bamboo assault rifle
                                self.game.player.switch_tool(tool = "BambooAssaultRifle")
                            # "3" key
                            case _ if event.key == pygame_K_3:
                                # Switch the player's tool to the bamboo launcher
                                self.game.player.switch_tool(tool = "BambooLauncher")

    def detect_game_state_transitions(self):

        # Detects for game state transitions
        
        # If the player has died (Transition from the game to the restart menu) and the transition has not started
        if self.game.game_over == True and self.menu.current_menu != "restart_menu" and self.bar_transition_timer == None:

            # Show the mouse cursor
            pygame_mouse_set_visible(True)

            # Transition from the game to the restart menu
            self.transition_where = "restart_menu"

            # Start the transition timer
            self.bar_transition_timer = self.bar_transition_time

            # Set game over to False
            self.game.game_over = False

        # Transitions between menus and the menu and the game and the transition has not started
        elif self.menu.transition_to_which_menu != "Nothing" and self.menu.current_menu != self.menu.transition_to_which_menu and self.bar_transition_timer == None:

            # Set the transition to begin depending on what button was pressed
            self.transition_where = self.menu.transition_to_which_menu

            # Start the transition timer
            self.bar_transition_timer = self.bar_transition_time

    def detect_and_perform_game_over_reset(self):

        # If the player just played and died and has returned to the main menu OR the player left their current session
        """ Note: the self.menu.current_menu == "main_menu" check is so that the following only occurs once (as the player can spam click the exit session button, resulting in multiple resets)
        - Therefore by only resetting it once the player is back in the main menu, that issue can be prevented
        """
        if (self.game.game_over == True and self.menu.current_menu == "main_menu") or (self.menu.session_exit == True and self.menu.current_menu == "main_menu"):

            # Reset the player's attributes
            self.game.player.reset_player()

            # Empty the groups, reset the level, camera, etc.
            self.game.reset_level()

            # If the player died
            if self.game.game_over == True:
                # Set game over back to False
                self.game.game_over = False

            # If this was a session exit
            if self.menu.session_exit == True:
                # Set the menu session exit attribute back to False
                self.menu.session_exit = False

    def perform_transition(self, delta_time):

        # Performs the transition between game states (i.e. changes between the menu and draws the transition)

        # If a transition has been set to start
        if self.transition_where != "Nothing":

            # Top black bar
            pygame_draw_rect(
                surface = self.surface,
                color = (113, 179, 64),
                rect = (
                        0, 
                        0, 
                        self.surface.get_width(), 
                        self.bar_height
                        ),
                width = 0
                )

            # Bottom black bar
            pygame_draw_rect(
                surface = self.surface,
                color = (113, 179, 64),
                rect = (
                        0, 
                        self.surface.get_height() - self.bar_height, 
                        self.surface.get_width(), 
                        self.bar_height
                        ),
                width = 0
                )            


            # Updating the size of the black bar

            # Temp variable for the time elapsed
            time_elapsed = self.bar_transition_time - self.bar_transition_timer

            # If the time elapsed is less than the black bar change time (Increasing the black bar height)
            if time_elapsed < self.bar_height_change_time:
                # Increase the size of the bars
                self.bar_new_height += self.bar_height_time_gradient * delta_time
                self.bar_height = round(self.bar_new_height)

            # If we the time elapsed is past the increasing time and the lock in time (Decreasing the black bar height)
            elif time_elapsed > (self.bar_transition_time - self.bar_height_change_time):
                # Decrease the height of the bars
                self.bar_new_height -= self.bar_height_time_gradient * delta_time
                self.bar_height = round(self.bar_new_height)
        
            # --------------------------------------------------
            # Updating timer

            # If the timer has not finished counting down
            if self.bar_transition_timer > 0:
                
                # If the transition has finished increasing and locking in for a short period of time
                if self.bar_transition_timer < (self.bar_transition_time - (self.bar_height_change_time + self.bar_lock_in_time)):
                    
                    # If the current menu has not been set to the menu specified to be transitioned to or has not been set to transition from the menus to the game
                    if self.menu.current_menu != self.transition_where:
                        # Set the current menu as the game (so that it stops showing menus, and shows the game
                        self.menu.current_menu = self.transition_where

                # Decrease the timer
                self.bar_transition_timer -= 1000 * delta_time

            # If the timer has finished counting down
            elif self.bar_transition_timer <= 0:

                # Reset the timer back to None
                self.bar_transition_timer = None

                # Reset the black bar heights
                self.bar_height = 0
                self.bar_new_height = 0

                # Stop the transition
                self.transition_where = "Nothing"
                self.menu.transition_to_which_menu = "Nothing"

    def run(self, delta_time):
        
        # Run the event loop
        self.event_loop()

        # Check if we need to reset the game, and reset the game if we do
        self.detect_and_perform_game_over_reset()

        # Detect for game state transitions
        self.detect_game_state_transitions()

        # If none of the menus are being shown
        if self.menu.current_menu == "game":

            # Load the level (Has conditions which will only perform this if the level hasn't been loaded into the game yet)
            self.load_level(chosen_level_number = 1)

            # If the player has not died
            if self.game.game_over == False:
                # Run the game
                self.game.run(delta_time)

        # If any menus are being shown
        elif self.menu.current_menu != "game":
            # Run the menus
            self.menu.run(delta_time)

        # Performs the transition between game states (i.e. changes between the menu and draws the transition)
        self.perform_transition(delta_time = delta_time)