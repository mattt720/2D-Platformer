import pygame


def dralpha(wn, color, rect):
    surf = pygame.Surface(rect[2:])

    surf.fill(color[:-1])  # (int, int, int)
    surf.set_alpha(color[-1])  # int

    wn.blit(surf, rect[0:2])


class Positions:
    def __init__(self, window):
        self.dims = window.get_rect()[2:]

        self.topleft = (0, 0)
        self.topcenter = (self.dims[0] / 2, 0)
        self.topright = (self.dims[0], 0)

        self.centerleft = (0, self.dims[1] / 2)
        self.center = (self.dims[0] / 2, self.dims[1] / 2)
        self.centerright = (self.dims[0], self.dims[1] / 2)

        self.bottomleft = (0, self.dims[1])
        self.bottomcenter = (self.dims[0] / 2, self.dims[1])
        self.bottomright = (self.dims[0], self.dims[1])


def write(window, text, position, rel, color=(255, 255, 255), size=32, align="center-center", font="calibri",
          render=True, antialias=True):
    try:
        # try load the font path
        font = pygame.font.Font(font, size)
    except:
        # load the font from the system OR use the system default if that cant be found
        font = pygame.font.SysFont(font, size)

    surf = font.render(text, antialias, color)
    align = align.split("-")

    position = list(position)

    if align[0] == "center":
        position[0] -= surf.get_width() / 2
    elif align[0] == "right":
        position[0] -= surf.get_width()

    if align[1] == "center":
        position[1] -= surf.get_height() / 2
    elif align[1] == "top":
        position[1] -= surf.get_height()

    if rel is not None:
        position = (rel[0] + position[0], rel[1] + position[1])

    if render:
        window.blit(surf, position)

    rect = pygame.Rect(*position, surf.get_width(), surf.get_height())

    return rect, surf


class TextButton:
    def __init__(self, text, position, rel, color=((255, 255, 255), (240, 240, 240)), size=32, align="center-center"
                 , font="calibri"):
        self.text = text
        self.position = position
        self.rel = rel
        self.color = color
        self.size = size
        self.align = align
        self.font = font

        self.hover = False

    def draw(self, window):
        if self.hover:
            new = self.color[1]
        else:
            new = self.color[0]

        rect = write(window, self.text, self.position, self.rel, new, self.size, self.align, self.font)[0]
        write(window, self.text, self.position, self.rel, new, self.size, self.align, self.font)

        self.hover = rect.collidepoint(*pygame.mouse.get_pos())

    def pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.hover
