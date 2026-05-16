import math
import pygame

from settings import (
    WIDTH,
    HEIGHT,
    WHITE,
    YELLOW,
    BLACK_HOLE_RADIUS,
    GRAVITY_STRENGTH,
    LIGHT_SPEED,
)


class Photon:
    def __init__(self, y, black_hole_x, black_hole_y):
        self.black_hole_x = black_hole_x
        self.black_hole_y = black_hole_y

        self.x = 0
        self.y = y

        self.vx = LIGHT_SPEED
        self.vy = 0

        self.trail = []

    def update(self):
        dx = self.black_hole_x - self.x
        dy = self.black_hole_y - self.y

        distance_squared = dx * dx + dy * dy
        distance = math.sqrt(distance_squared)

        if distance > BLACK_HOLE_RADIUS:
            force = GRAVITY_STRENGTH / distance_squared

            self.vx += (dx / distance) * force
            self.vy += (dy / distance) * force

            speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)

            self.vx = (self.vx / speed) * LIGHT_SPEED
            self.vy = (self.vy / speed) * LIGHT_SPEED

        self.x += self.vx
        self.y += self.vy

        self.trail.append((int(self.x), int(self.y)))

        if len(self.trail) > 80:
            self.trail.pop(0)

    def draw(self, screen):
        if len(self.trail) > 1:
            pygame.draw.lines(screen, YELLOW, False, self.trail, 2)

        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 3)

    def is_dead(self):
        dx = self.x - self.black_hole_x
        dy = self.y - self.black_hole_y
        distance = math.sqrt(dx * dx + dy * dy)

        return (
            self.x > WIDTH + 100
            or self.y < -100
            or self.y > HEIGHT + 100
            or distance < BLACK_HOLE_RADIUS
        )