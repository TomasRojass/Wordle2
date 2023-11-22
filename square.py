import pygame


class Square:

    def __init__(self, xpos=0, ypos=0, color="gray", xoffset=100, yoffset=40, width=75, height=75, big_left_offset=100):
        # constants

        self.possible_colors = {
            "gray": (80, 80, 80),
            "yellow": (193, 174, 95),
            "green": (84, 139, 76),
            "blank": (120, 120, 120)
        }


        # vars
        self.color = color
        self.width = width
        self.height = height
        self.padding = 6
        self.rgb = self.possible_colors[self.color]
        self.xpos = xpos
        self.ypos = ypos
        self.x = self.xpos * (self.width + self.padding) + xoffset + big_left_offset
        self.y = self.ypos * (self.height + self.padding) + yoffset
        self.letter = " "

    @property
    def pygame_object(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value not in self.possible_colors:
            raise ValueError(f"Invalid color, must be one of {self.possible_colors.keys()}")
        self.rgb = self.possible_colors[value]
        self._color = value

    def keep_max_color(self, value):
        color_values = {"blank": 0, "gray": 1, "yellow": 2, "green": 3}

        new_color_number = max(color_values[self.color], color_values[value])

        for color_name, color_number in color_values.items():
            if new_color_number == color_number:
                self.color = color_name
