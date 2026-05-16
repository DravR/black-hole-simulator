import pygame
import sys

from settings import (
    WIDTH,
    HEIGHT,
    BLACK,
    FPS,
    BLACK_HOLE_RADIUS,
)

from photon import Photon
from accretion_disk import AccretionParticle


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Black Hole Simulator")

clock = pygame.time.Clock()

black_hole_x = WIDTH // 2
black_hole_y = HEIGHT // 2


photons = []
accretion_particles = []

for _ in range(900):
    accretion_particles.append(
        AccretionParticle(black_hole_x, black_hole_y)
    )

for y in range(180, 521, 55):
    photons.append(
        Photon(y, black_hole_x, black_hole_y)
    )


running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    pygame.draw.circle(
        screen,
        (15, 15, 15),
        (black_hole_x, black_hole_y),
        BLACK_HOLE_RADIUS + 45
    )

    pygame.draw.circle(
        screen,
        (25, 25, 25),
        (black_hole_x, black_hole_y),
        BLACK_HOLE_RADIUS + 30
    )

    pygame.draw.circle(
        screen,
        (40, 40, 40),
        (black_hole_x, black_hole_y),
        BLACK_HOLE_RADIUS + 15
    )

    for particle in accretion_particles:
        particle.update()

    for particle in accretion_particles:
        if particle.is_behind_black_hole():
            particle.draw(screen)

    pygame.draw.circle(
        screen,
        BLACK,
        (black_hole_x, black_hole_y),
        BLACK_HOLE_RADIUS
    )

    for particle in accretion_particles:
        if not particle.is_behind_black_hole():
            particle.draw(screen)

    for photon in photons[:]:
        photon.update()
        photon.draw(screen)

        if photon.is_dead():
            photons.remove(photon)

    if len(photons) == 0:
        for y in range(0, HEIGHT, 25):
            photons.append(
                Photon(y, black_hole_x, black_hole_y)
            )

    pygame.display.flip()

pygame.quit()
sys.exit()