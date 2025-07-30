import pygame
import random
import time

import ui

Vec2 = pygame.Vector2


class EnemyDestroy:
    def __init__(self, position):
        self.position = position
        self.particles = []

        self.created = time.time()

        for i in range(random.randint(40, 60)):
            xv, yv = random.randint(-200, 200), random.randint(-400, 200)
            self.particles.append({"position": Vec2(self.position), "color": (228, 108, 108), "velocity": Vec2(xv, yv),
                                   "lifetime": random.uniform(0.5, 1)})

    def update(self, last_frame: float):
        to_destroy = []

        for particle in self.particles:
            particle["position"] += particle["velocity"] * last_frame
            particle["velocity"].y += 20

            if self.created < time.time() - particle["lifetime"]:
                to_destroy.append(particle)

        for particle in to_destroy:
            self.particles.remove(particle)

    def draw(self, wn):
        for particle in self.particles:
            pygame.draw.rect(wn, particle["color"], pygame.Rect(*particle["position"], 5, 5))


class Clouds:
    def __init__(self, window_dimensions: Vec2):
        self.wn_dims = window_dimensions
        self.particles = []

        self.last_spawned = time.time()

        self.spawn()
        self.particles[-1]["position"].y = int(self.wn_dims.x / 2)

    def update(self, last_frame):
        if time.time() - self.last_spawned > 10:
            self.spawn()
            self.last_spawned = time.time()

        to_destroy = []

        for particle in self.particles:
            particle["position"] += particle["velocity"] * last_frame

            if particle["on_left"]:
                if particle["position"].x > self.wn_dims.x:
                    to_destroy.append(particle)
            else:
                if particle["position"].x < -particle["dims"].x:
                    to_destroy.append(particle)

        for particle in to_destroy:
            self.particles.remove(particle)

    def draw(self, wn):
        for particle in self.particles:
            ui.dralpha(wn, (255, 255, 255, 100), pygame.Rect(*particle["position"], *particle["dims"]))

    def spawn(self):
        width, height = random.randint(300, 550), random.randint(100, 250)
        xv = random.randint(30, 50)

        on_left = random.randint(0, 1)  # half chance
        if on_left:
            pos = Vec2(-width, random.randint(int(-height / 2), int(self.wn_dims.y + height / 2)))
        else:
            pos = Vec2(self.wn_dims.x, random.randint(int(-height / 2), int(self.wn_dims.y + height / 2)))
            xv *= -1

        self.particles.append({"position": Vec2(*pos), "color": (228, 108, 108), "dims": Vec2(width, height),
                               "velocity": Vec2(xv, 0), "on_left": on_left})


class PowerupCollect:
    def __init__(self, position, color):
        self.position = position
        self.particles = []

        self.created = time.time()

        for i in range(random.randint(40, 60)):
            xv, yv = random.randint(-200, 200), random.randint(-400, 200)
            self.particles.append({"position": Vec2(self.position), "color": color, "velocity": Vec2(xv, yv),
                                   "lifetime": random.uniform(0.5, 1)})

    def update(self, last_frame: float):
        to_destroy = []

        for particle in self.particles:
            particle["position"] += particle["velocity"] * last_frame
            particle["velocity"].y += 10

            if self.created < time.time() - particle["lifetime"]:
                to_destroy.append(particle)

        for particle in to_destroy:
            self.particles.remove(particle)

    def draw(self, wn):
        for particle in self.particles:
            pygame.draw.rect(wn, particle["color"], pygame.Rect(*particle["position"], 5, 5))
