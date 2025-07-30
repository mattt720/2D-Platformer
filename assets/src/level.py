import pygame
import spritesheet
import random
import math

Vec2 = pygame.Vector2


class Enemy:
    def __init__(self, position: pygame.Vector2, image: pygame.Surface, move_range: list, speed: float = 80):
        self.position = position
        self.rect = pygame.Rect(*self.position, *image.get_size())
        self.image = image

        self.speed = speed

        self.range = move_range
        self.x_change = speed

        self.destroy = False
        self.id = "enemy"

    def update(self, rel, last_frame: float):
        self.position.x += self.x_change * last_frame
        self.rect.x, self.rect.y = self.position

        if self.position.x > self.range[1] - self.rect.w:  # right-most distance
            self.x_change = -1 * self.speed
        elif self.position.x < self.range[0]:  # left-most distance
            self.x_change = 1 * self.speed

    def draw(self, wn):
        surf = pygame.transform.flip(self.image, self.x_change < 0, False)
        wn.blit(surf, self.position)


class Block:
    def __init__(self, position: pygame.Vector2, image: pygame.Surface):
        self.position = position
        self.rect = pygame.Rect(*self.position, *image.get_size())
        self.image = image

        self.id = ""
        self.destroy = False
        self.bounce = 0

    def update(self, rel, last_frame: float):
        pass

    def draw(self, wn):
        wn.blit(self.image, self.position)


class Powerup(Block):
    def __init__(self, position: pygame.Vector2, image: pygame.Surface):
        super(Powerup, self).__init__(position, image)

        self.transparency_min = 100
        self.transparency_max = 200
        self.transparency_add = 2

        self._transparency_direction = 1
        self.transparency = self.transparency_min

        self.image_num = 0

    def draw(self, wn):
        surf = self.image.copy()
        surf.fill((255, 255, 255, self.transparency), special_flags=pygame.BLEND_RGBA_MULT)

        wn.blit(surf, self.position)

        self.transparency += self.transparency_add * self._transparency_direction

        if self.transparency > self.transparency_max:
            self._transparency_direction *= -1
        elif self.transparency < self.transparency_min:
            self._transparency_direction *= -1


class Level:
    def __init__(self, file_path, images: spritesheet.SpriteSheet, powerups=2):
        self.data = []
        self.enemy_count = 0

        block_no_enemies = []

        with open(file_path, "r") as f:
            data = f.read()
            data_split = data.split(":")

            for block in data_split:
                block_info = block.split(",")
                block_id = block_info[3]

                if block_id == "grass":
                    surf = images[0]
                elif block_id == "stone":
                    surf = images[1]
                elif block_id == "dirt":
                    surf = images[2]
                elif block_id == "spike":
                    surf = images[3]
                elif block_id == "brick":
                    surf = images[4]
                elif block_id == "enemy":
                    self.enemy_count += 1
                    surf = images[5]

                if block_info[0] == "EnemyEditor":
                    move_range = [int(block_info[4]), int(block_info[5])]
                    self.data.append(Enemy(Vec2(int(block_info[1]), int(block_info[2])), surf, move_range))
                else:
                    block_class = eval(block_info[0])
                    self.data.append(block_class(Vec2(int(block_info[1]), int(block_info[2])), surf))
                    block_no_enemies.append(self.data[-1])

                self.data[-1].id = block_id

        if powerups > 0:
            random.shuffle(block_no_enemies)

            types = [9, 10, 11] * math.ceil(powerups / 3)
            random.shuffle(types)
            types_index = 0

            i = 0
            while i < powerups:
                at = self.at(block_no_enemies[i].position + Vec2(0, -images.size[1]+2))

                if at is not None:
                    powerups += 1
                    i += 1
                    continue

                t = types[types_index]
                self.data.append(Powerup(block_no_enemies[i].position + Vec2(0, -images.size[1]+2), images[t]))
                self.data[-1].image_num = t
                types_index += 1

                i += 1

    def __iter__(self):
        return iter(self.data)

    def at(self, position: Vec2):
        for block in self.data:
            if block.position == position:
                return block
        return None
