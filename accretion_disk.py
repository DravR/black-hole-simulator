import math
import random
import pygame


class AccretionParticle:
    def __init__(self, black_hole_x, black_hole_y):
        self.black_hole_x = black_hole_x
        self.black_hole_y = black_hole_y

        self.angle = math.radians(random.randint(0, 360))
        self.distance = random.randint(75, 210)
        self.speed = random.uniform(0.006, 0.022)
        self.size = random.randint(1, 3)

        colors = [
            (255, 70, 20),
            (255, 120, 30),
            (255, 180, 70),
            (255, 230, 160),
        ]

        self.color = random.choice(colors)

    def update(self):
        self.angle += self.speed

    def get_position(self):
        x = self.black_hole_x + math.cos(self.angle) * self.distance
        y = self.black_hole_y + math.sin(self.angle) * self.distance * 0.28
        return x, y

    def is_behind_black_hole(self):
        return math.sin(self.angle) < 0

    def draw(self, screen):
        x, y = self.get_position()

        pygame.draw.circle(
            screen,
            self.color,
            (int(x), int(y)),
            self.size
        )