class EffectText:

    # effect_text_group = []

    def __init__(self, x, y, colour, display_time, text, font, alpha_surface, alpha_level, type_of_effect_text):

        # Colour of the text
        self.colour = colour

        # Time that the text will be displayed
        self.display_time = display_time

        # The text to be displayed
        self.text = text

        # The type of effect text
        self.type_of_effect_text = type_of_effect_text

        # The x and y co-ordinates of where the effect text alpha surface will be drawn onto
        self.x = x
        self.y = y

        # The font
        self.font = font

        # The alpha surface the effect text will be drawn onto
        self.alpha_surface = alpha_surface

        # The starting alpha level of the alpha surface
        self.alpha_level = alpha_level

        # Add self to the effect text list
        EffectText.effect_text_list.append(self)