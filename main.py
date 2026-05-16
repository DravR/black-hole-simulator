import pygame
import sys
import math

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Black Hole Light Bending")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 120)
DARK_GRAY = (20, 20, 20)

clock = pygame.time.Clock()

black_hole_x = WIDTH // 2
black_hole_y = HEIGHT // 2
black_hole_radius = 45

GRAVITY_STRENGTH = 1900
LIGHT_SPEED = 5


class Photon:
    def __init__(self, y):
        self.x = 0
        self.y = y

        self.vx = LIGHT_SPEED
        self.vy = 0

        self.trail = []

    def update(self):
        dx = black_hole_x - self.x
        dy = black_hole_y - self.y

        distance_squared = dx * dx + dy * dy
        distance = math.sqrt(distance_squared)

        if distance > black_hole_radius:
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

    def draw(self):
        if len(self.trail) > 1:
            pygame.draw.lines(screen, YELLOW, False, self.trail, 2)

        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 3)

    def is_dead(self):
        dx = self.x - black_hole_x
        dy = self.y - black_hole_y
        distance = math.sqrt(dx * dx + dy * dy)

        return (
            self.x > WIDTH + 100
            or self.y < -100
            or self.y > HEIGHT + 100
            or distance < black_hole_radius
        )


photons = []

for y in range(180, 521, 55):
    photons.append(Photon(y))


running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    pygame.draw.circle(
        screen,
        DARK_GRAY,
        (black_hole_x, black_hole_y),
        black_hole_radius + 18
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (black_hole_x, black_hole_y),
        black_hole_radius
    )

    for photon in photons[:]:
        photon.update()
        photon.draw()

        if photon.is_dead():
            photons.remove(photon)

    if len(photons) == 0:
        for y in range(0, HEIGHT, 25):
            photons.append(Photon(y))

    pygame.display.flip()

pygame.quit()
sys.exit()