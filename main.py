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
from accretion_disk import AccretionDisk
from star_field import StarField


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Black Hole Simulator")

clock = pygame.time.Clock()

black_hole_x = WIDTH // 2
black_hole_y = HEIGHT // 2

photons = []
star_field = StarField()

accretion_disk = AccretionDisk(black_hole_x, black_hole_y)

for y in range(180, 521, 55):
    photons.append(Photon(y, black_hole_x, black_hole_y))


def draw_glow_circle(surface, center, radius, color, layers=8):
    for i in range(layers, 0, -1):
        alpha = int(22 * (i / layers))
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        pygame.draw.circle(
            glow,
            (*color, alpha),
            center,
            radius + i * 8,
            6
        )

        surface.blit(glow, (0, 0))


running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    star_field.update()
    star_field.draw(screen, black_hole_x, black_hole_y)

    accretion_disk.update()

    disk_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    accretion_disk.draw_back(disk_surface)
    accretion_disk.draw_front(disk_surface)

    small_disk = pygame.transform.smoothscale(
        disk_surface,
        (WIDTH // 4, HEIGHT // 4)
    )

    blurred_disk = pygame.transform.smoothscale(
        small_disk,
        (WIDTH, HEIGHT)
    )

    blurred_disk.set_alpha(120)

    screen.blit(blurred_disk, (0, 0))
    screen.blit(disk_surface, (0, 0))

    # Anillo brillante estilo Interestelar
    draw_glow_circle(
        screen,
        (black_hole_x, black_hole_y),
        BLACK_HOLE_RADIUS + 35,
        (255, 245, 210),
        layers=10
    )

    pygame.draw.circle(
        screen,
        (255, 245, 220),
        (black_hole_x, black_hole_y),
        BLACK_HOLE_RADIUS + 35,
        5
    )

    pygame.draw.circle(
        screen,
        (255, 210, 130),
        (black_hole_x, black_hole_y),
        BLACK_HOLE_RADIUS + 29,
        2
    )

    # Sombra del agujero negro
    pygame.draw.circle(
        screen,
        BLACK,
        (black_hole_x, black_hole_y),
        BLACK_HOLE_RADIUS + 25
    )

    # Disco frontal cruzando delante de la sombra
    front_line = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    pygame.draw.ellipse(
        front_line,
        (255, 230, 170, 180),
        (
            black_hole_x - 280,
            black_hole_y - 17,
            560,
            34
        ),
        3
    )

    pygame.draw.ellipse(
        front_line,
        (255, 255, 235, 220),
        (
            black_hole_x - 210,
            black_hole_y - 9,
            420,
            18
        ),
        2
    )

    screen.blit(front_line, (0, 0))

    # Fotones de prueba
    for photon in photons[:]:
        photon.update()
        photon.draw(screen)

        if photon.is_dead():
            photons.remove(photon)

    if len(photons) == 0:
        for y in range(0, HEIGHT, 25):
            photons.append(Photon(y, black_hole_x, black_hole_y))

    pygame.display.flip()

pygame.quit()
sys.exit()