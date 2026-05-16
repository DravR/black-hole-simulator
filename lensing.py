import math
import pygame


class GravitationalLensing:

    def __init__(self, black_hole_x, black_hole_y, radius):

        self.black_hole_x = black_hole_x
        self.black_hole_y = black_hole_y

        self.radius = radius

        self.lens_radius = 260

    def apply(self, source_surface):

        width, height = source_surface.get_size()

        result = pygame.Surface((width, height))

        for y in range(height):

            for x in range(width):

                dx = x - self.black_hole_x
                dy = y - self.black_hole_y

                distance = math.sqrt(dx * dx + dy * dy)

                sample_x = x
                sample_y = y

                if self.radius < distance < self.lens_radius:

                    distortion_strength = (
                        (self.lens_radius - distance)
                        / self.lens_radius
                    )

                    bend = distortion_strength * 42

                    if distance > 0:

                        sample_x += (dx / distance) * bend
                        sample_y += (dy / distance) * bend

                sample_x = int(max(0, min(width - 1, sample_x)))
                sample_y = int(max(0, min(height - 1, sample_y)))

                color = source_surface.get_at((sample_x, sample_y))

                result.set_at((x, y), color)

        return result