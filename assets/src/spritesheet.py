"""
Script to parse spritesheets
"""

import pygame


class SpriteSheet:
    def __init__(self, path, img_size=(16, 16), enlarge=1):
        # load the full image, ready for editing
        self.full = pygame.image.load(path)  # type: pygame.Surface
        self.surfaces = []

        for x in range(0, self.full.get_width(), img_size[0]):  # basically tile the whole image and get all the...
            for y in range(0, self.full.get_height(), img_size[1]):  # ...blocks from a grid

                sub_surf = self.full.subsurface((x, y, *img_size))  # create a sub surface (crop out) of the full sheet
                sub_surf = pygame.transform.scale(sub_surf, (img_size[0]*enlarge, img_size[1]*enlarge))

                self.size = (img_size[0]*enlarge, img_size[1]*enlarge)

                self.surfaces.append(sub_surf.convert_alpha())

    def __iter__(self):  # when someone tries to iterate over SpriteSheet
        return iter(self.surfaces)

    def __len__(self):  # when someone calls len(SpriteSheet)
        return len(self.surfaces)

    def __getitem__(self, item):
        return self.surfaces[item]
