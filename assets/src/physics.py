# NOTE: this class only works with 'Player'
import pygame
import level as l


class Physics:
    def __init__(self, position: pygame.Vector2, gravity: float, friction: float, jump_height: int):
        self.pos = pygame.Vector2(position.x, position.y)  # so it creates a copy of the position
        self.gravity = gravity
        self.friction = friction
        self.jump_height = jump_height

        self.velocity = pygame.Vector2(0, 0)

    def is_colliding(self, level, dimensions: pygame.Vector2, detect_enemies=False, detect_powerups=False,
                     detect_blocks=True):
        for block in level:
            if pygame.Rect(*self.pos, *dimensions).colliderect(block.rect):
                if type(block) == l.Enemy and not detect_enemies:
                    continue
                if type(block) == l.Powerup and not detect_powerups:
                    continue
                if type(block) == l.Block and not detect_blocks:
                    continue

                return True
        return False

    def get_rect(self, dimensions):
        return pygame.Rect(*self.pos, *dimensions)
