import pygame
import physics
import math
import time


def lerp_vector2(a, b, t):
    return (b - a) / t


# taken from: https://gamedev.stackexchange.com/questions/26550/how-can-a-pygame-image-be-colored
def colorize(image, new_color):
    """
    Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving the per-pixel alphas of
    original).
    :param image: Surface to create a colorized copy of
    :param new_color: RGB color to use (original alpha values are preserved)
    :return: New colorized Surface instance
    """
    image = image.copy()

    # zero out RGB values
    image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # add in new RGB values
    image.fill(new_color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

    return image


class Player:
    class Gun:
        class Bullet:
            def __init__(self, position: pygame.Vector2, direction: float, speed: float):
                self.position = pygame.Vector2(position)
                self.direction = direction - 90
                self.speed = speed

                self.xv = -math.sin(math.radians(self.direction)) * self.speed
                self.yv = -math.cos(math.radians(self.direction)) * self.speed

                self.surf = pygame.Surface((3, 3), flags=pygame.SRCALPHA)
                self.surf.fill((30, 30, 30))

                self.surf = pygame.transform.rotate(self.surf, self.direction)
                self.position -= pygame.Vector2(self.surf.get_size()) / 2

                self.created_time = time.time()
                self.destroy = False

                pygame.mixer.Sound("assets/snd/shoot1.wav").play()

            def update(self):
                self.position += pygame.Vector2(self.xv, self.yv)
                if time.time() - self.created_time >= 5:  # its been 5 seconds since the bullet was created
                    self.destroy = True

            def draw(self, wn):
                wn.blit(self.surf, self.position)

        def __init__(self, player, image: pygame.Surface):
            self.player = player
            self.image = pygame.transform.scale(image, (image.get_width() * 2, image.get_height() * 2))

            self.position = pygame.Vector2()
            self.rotation = 0
            self.bullets = []

            self.triple_shoot = False

        def update(self):
            self.position += lerp_vector2(self.position, self.player.physics.pos + pygame.Vector2(15, 20), 2)

            # point to mouse
            mouse = pygame.Vector2(pygame.mouse.get_pos())
            rel = pygame.Vector2(self.position.x - mouse.x, self.position.y - mouse.y)
            angle = math.degrees(math.atan2(rel.x, rel.y)) + 90

            self.rotation = angle

        def draw(self, wn, whited=False):
            surf = self.image.copy()

            if self.rotation > 90:
                # angle of incidence = self.rotation
                # angle of exedence = 0 - self.rotation

                surf = pygame.transform.rotate(surf, -self.rotation)
                surf = pygame.transform.flip(surf, False, True)
            else:
                surf = pygame.transform.rotate(self.image, self.rotation)

            new_pos = pygame.Vector2(self.position - (pygame.Vector2(surf.get_size()) / 2))

            to_destroy = []
            for bullet in self.bullets:
                bullet.update()
                bullet.draw(wn)

                if bullet.destroy:
                    to_destroy.append(bullet)

            for bullet in to_destroy:
                self.bullets.remove(bullet)
                print("Bullet destroyed")

            if whited:
                surf = colorize(surf, (255, 255, 255))

            wn.blit(surf, new_pos)

        def shoot(self):
            print("Bullet created")

            self.bullets.append(Player.Gun.Bullet(self.position, self.rotation, 15))

            if self.triple_shoot:
                self.bullets.append(Player.Gun.Bullet(self.position, self.rotation - 10, 15))
                self.bullets.append(Player.Gun.Bullet(self.position, self.rotation + 10, 15))

            # apply recoil
            rot = self.rotation - 90
            xv = -math.sin(math.radians(rot)) * 3
            yv = -math.cos(math.radians(rot)) * 5

            self.player.physics.velocity -= pygame.Vector2(xv, -yv)

    def __init__(self, position: pygame.Vector2,
                 size: pygame.Vector2,
                 gravity: float,
                 friction: float,
                 jump_height: int,
                 move_speed: float,
                 image: pygame.Surface):

        self.physics = physics.Physics(position, gravity, friction, jump_height)
        self.move_speed = move_speed
        self.size = size
        self.image = image

        self.gun = Player.Gun(self, pygame.image.load("assets/img/gun.png"))

        self.flip_x = False

        self._blink_deadline = 0
        self._blink_wait = 0.12

        self._last_blinked = 0
        self._white = False
        self._is_blinking = False

    def update(self, level, last_frame: float):
        keys = pygame.key.get_pressed()

        self.physics.velocity.y -= self.physics.gravity
        self.physics.pos.y -= self.physics.velocity.y  # because the y-axis on pygame is inverted

        if self.physics.is_colliding(level, self.size):
            while self.physics.is_colliding(level, self.size):
                try:
                    # if its negative -> -1, if its positive -> 1
                    self.physics.pos.y += abs(self.physics.velocity.y) / self.physics.velocity.y
                except ZeroDivisionError:
                    pass

            yv = self.physics.velocity.y
            jh = self.physics.jump_height

            # vertical controls (in one line)
            self.physics.velocity.y = ((keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]) and (abs(yv) / yv) == -1) * jh

        self.physics.pos.x += self.physics.velocity.x

        self.physics.velocity.x *= self.physics.friction
        self.physics.velocity.x += (-(keys[pygame.K_LEFT] or keys[pygame.K_a])
                                    + (keys[pygame.K_RIGHT] or keys[pygame.K_d])) * self.move_speed * last_frame

        self.gun.update()

        if self.gun.rotation > 90:
            self.flip_x = True
        else:
            self.flip_x = False

        if self.physics.is_colliding(level, self.size):
            while self.physics.is_colliding(level, self.size):
                self.physics.pos.x -= abs(self.physics.velocity.x) / self.physics.velocity.x
            self.physics.velocity.x = 0

    def draw(self, wn):
        surf = pygame.transform.flip(self.image, self.flip_x, False)

        if self._is_blinking:
            if time.time() - self._blink_wait > self._last_blinked:
                self._white = not self._white
                self._last_blinked = time.time()

            if self._white:
                surf = colorize(surf, (255, 255, 255))

            if time.time() > self._blink_deadline:
                self._is_blinking = False

        wn.blit(surf, self.physics.pos)

        self.gun.draw(wn, whited=self._white)

    def shoot(self):
        self.gun.shoot()

    def start_blinking(self, duration, wait):
        self._blink_deadline = time.time() + duration
        self._blink_wait = wait
        self._is_blinking = True
        self._last_blinked = time.time()
        self._white = False
