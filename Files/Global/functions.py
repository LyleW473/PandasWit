from pygame.transform import smoothscale
from pygame import Surface as pygame_Surface
from pygame import BLEND_RGB_ADD as pygame_BLEND_RGB_ADD
from math import sin, radians

def draw_text(text, text_colour, font, x, y, surface, scale_multiplier = None):

    # If a scale multiplier has not been passed in
    if scale_multiplier == None:
        # Render the text as an image without anti-aliasing
        text_image = font.render(text, False, text_colour)
        # Blit the image onto the surface
        surface.blit(text_image, (x, y))

    # If a scale multiplier has been passed in
    elif scale_multiplier != None:
        # Render the text as an image with anti-aliasing
        text_image = font.render(text, True, text_colour)
        # Smoothscale and blit the image onto the surface
        surface.blit(smoothscale(text_image, (text_image.get_width() / scale_multiplier, text_image.get_height() / scale_multiplier)), (x, y))

def change_image_colour(current_animation_image, desired_colour = (255, 255, 255)): # Default colour is white

        # Create a new surface which will be blended with the current (animation) image to make an image change colour
        colour_layer = pygame_Surface(current_animation_image.get_size()).convert_alpha()

        # Fill the colour layer with the desired colour
        colour_layer.fill(desired_colour)
        
        # Set the current (animation) image to be a copy of the current (animation) image (so that the original image is not overwritten)
        current_animation_image = current_animation_image.copy()
        
        # Blit the colour layer onto the current (animation) image, with the special flag pygame_BLEND_RGB_ADD to add the RGB values
        current_animation_image.blit(colour_layer, (0, 0), special_flags = pygame_BLEND_RGB_ADD)

        # Return the coloured animation image (The result should be an image that has a different colour on top)
        return current_animation_image

def change_image_colour_v2(current_animation_image, desired_colour):

    # Changes the image colour completely, without flags

    # Create a copy of the image (So that you don't overwrite the original)
    changed_image = current_animation_image.copy().convert_alpha()

      # For each row
    for i in range(0, changed_image.get_width()):
        # For each column
        for j in range(0, changed_image.get_height()):
            
            # If the pixel is not fully transparent
            if changed_image.get_at((i, j)).a != 0:
                # Set the pixel as the desired colour
                changed_image.set_at((i, j), (desired_colour[0], desired_colour[1], desired_colour[2], 255))

    # Return the changed image
    return changed_image

def sin_change_object_colour(current_sin_angle, angle_time_gradient, colour_to_change, original_colour, delta_time, plus_or_minus_list, min_max_colours):

        """ Explanations of parameters:
        current_sin_angle = The current sin angle
        angle_time_gradient = The rate of change in the angle over time
        colour_to_change = The colour that will be changed and returned 
        original_colour = The original colour so that the midpoint colour can be found, so that the colour value can oscillate between the minimum and maximum colour values
        plus_or_minus_list = A list containing values -1, 0 or 1, which will indicate whether we add, subtract or do nothing 
        delta_time = delta time to increase the current angle
        """
        # Find the midpoint colour, so that the colour value will oscillate between the minimum colour and the maximum colour passed in
        midpoint_colour = [
                            round(original_colour[0] - ((min_max_colours[0][0] - min_max_colours[1][0]) / 2)), 
                            round(original_colour[1] - ((min_max_colours[0][1] - min_max_colours[1][1]) / 2)),
                            round(original_colour[2] - ((min_max_colours[0][2] - min_max_colours[1][2]) / 2))
                          ] 

        # Set the colour to change to be the midpoint colour
        colour_to_change = midpoint_colour
        
        # Find the differences in colour between the midpoint and the original colour
        colour_differences = (abs(original_colour[0] - midpoint_colour[0]), abs(original_colour[1] - midpoint_colour[1]), abs(original_colour[2] - midpoint_colour[2]))

        # Change the colour
        for i in range(0, len(colour_to_change)):
            
            # If plus or minus value is 0, go to the next RGB value
            if plus_or_minus_list[i] == 0:
                continue
            
            # If plus or minus value is 1, add the colour difference at this angle
            elif plus_or_minus_list[i] == 1:
                colour_to_change[i] += (colour_differences[i] * sin(radians(current_sin_angle)))
            
            # If plus or minus value is -1, subtract the colour difference at this angle
            elif plus_or_minus_list[i] == -1:
                colour_to_change[i] -= (colour_differences[i] * sin(radians(current_sin_angle)))

        # Increase the current sin angle
        current_sin_angle += angle_time_gradient * delta_time

        # Return the changed colour and the changed sin angle
        return colour_to_change, current_sin_angle

def move_item_vertically_sin(current_sin_angle, angle_time_gradient, delta_time, original_position, current_position, displacement):
    
    # Increase the sin angle
    current_sin_angle += angle_time_gradient * delta_time

    # Set the new position based on the current sin angle
    new_position = current_position
    new_position[1] = original_position[1] + (displacement * sin(radians(current_sin_angle)))

    # Return the new position and sin angle
    return new_position, current_sin_angle

def update_generic_timer(current_timer, delta_time):

    # Updates a generic timer
    
    # If the timer has been set
    if current_timer != None:

        # Decrease the timer
        current_timer -= 1000 * delta_time
        
        # If the spawning cooldown timer has finished counting down
        if current_timer <= 0:
            # Reset the timer back to None
            current_timer = None

        # Return the updated timer
        return current_timer

def simple_loop_animation(animation_index, animation_list, animation_frame_timer, time_between_anim_frames):

    # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
    if animation_index < (len(animation_list) - 1) and (animation_frame_timer) <= 0:
        # Go the next animation frame
        animation_index += 1
        # Reset the timer (adding will help with accuracy)
        animation_frame_timer = time_between_anim_frames

    # If the current animation index is at the last index inside the animation list and the animation frame timer has finished counting
    elif animation_index == (len(animation_list) - 1) and (animation_frame_timer <= 0):
        # Go the the first animation frame (reset the animation)
        animation_index = 0
        # Reset the timer (adding will help with accuracy)
        animation_frame_timer = time_between_anim_frames
    
    return animation_index, animation_frame_timer

def simple_play_animation_once(animation_index, animation_list, animation_frame_timer, time_between_anim_frames):

    # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
    if animation_index < (len(animation_list) - 1) and (animation_frame_timer) <= 0:
        # Go the next animation frame
        animation_index += 1

        # Reset the timer (adding will help with accuracy)
        animation_frame_timer = time_between_anim_frames

    return animation_index, animation_frame_timer
