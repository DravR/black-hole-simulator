import random
import math
import pygame

from settings import WIDTH, HEIGHT, BLACK_HOLE_RADIUS


class Star:
    def __init__(self):
        self.original_x = random.randint(0, WIDTH)
        self.original_y = random.randint(0, HEIGHT)

        self.size = random.choice([1, 1, 1, 2])

        self.brightness = random.randint(80, 255)

        self.twinkle_speed = random.uniform(0.3, 1.2)

        self.direction = random.choice([-1, 1])

    def update(self):

        self.brightness += self.direction * self.twinkle_speed

        if self.brightness >= 255:
            self.brightness = 255
            self.direction = -1

        if self.brightness <= 80:
            self.brightness = 80
            self.direction = 1

    def draw(self, screen, black_hole_x, black_hole_y):

        dx = self.original_x - black_hole_x
        dy = self.original_y - black_hole_y

        distance = math.sqrt(dx * dx + dy * dy)

        lens_strength = 0

        if BLACK_HOLE_RADIUS + 20 < distance < 260:
            lens_strength = (260 - distance) / 260

        if distance > 0:

            distortion = lens_strength * 28

            draw_x = self.original_x + (dx / distance) * distortion
            draw_y = self.original_y + (dy / distance) * distortion

        else:
            draw_x = self.original_x
            draw_y = self.original_y

        color = (
            int(self.brightness),
            int(self.brightness),
            int(self.brightness)
        )

        pygame.draw.circle(
            screen,
            color,
            (int(draw_x), int(draw_y)),
            self.size
        )


class StarField:

    def __init__(self, amount=220):

        self.stars = []

        for _ in range(amount):
            self.stars.append(Star())

    def update(self):

        for star in self.stars:
            star.update()

    def draw(self, screen, black_hole_x, black_hole_y):

        for star in self.stars:
            star.draw(screen, black_hole_x, black_hole_y)