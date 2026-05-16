import pygame


class AccretionDisk:
    def __init__(self, black_hole_x, black_hole_y):
        self.black_hole_x = black_hole_x
        self.black_hole_y = black_hole_y
        self.rotation = 0

    def update(self):
        self.rotation += 0.004

    def draw_back(self, screen):
        self._draw_plasma_disk(screen, back=True)

    def draw_front(self, screen):
        self._draw_plasma_disk(screen, back=False)

    def _draw_plasma_disk(self, screen, back):
        disk_layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        if back:
            y_offset = -32
            alpha_boost = 0.55
        else:
            y_offset = 0
            alpha_boost = 1.0

        # Capas exteriores suaves
        for i in range(12):
            width = 620 - i * 32
            height = 120 - i * 7

            alpha = int((18 + i * 6) * alpha_boost)

            color = (
                255,
                190 + min(i * 4, 55),
                120 + min(i * 5, 80),
                alpha
            )

            rect = (
                self.black_hole_x - width // 2,
                self.black_hole_y - height // 2 + y_offset,
                width,
                height
            )

            pygame.draw.ellipse(
                disk_layer,
                color,
                rect
            )

        # Núcleo brillante del disco
        for i in range(8):
            width = 430 - i * 32
            height = 46 - i * 4

            alpha = int((35 + i * 12) * alpha_boost)

            color = (
                255,
                235,
                185,
                alpha
            )

            rect = (
                self.black_hole_x - width // 2,
                self.black_hole_y - height // 2 + y_offset,
                width,
                height
            )

            pygame.draw.ellipse(
                disk_layer,
                color,
                rect
            )

        # Suavizado falso
        small = pygame.transform.smoothscale(
            disk_layer,
            (
                screen.get_width() // 3,
                screen.get_height() // 3
            )
        )

        smooth = pygame.transform.smoothscale(
            small,
            screen.get_size()
        )

        screen.blit(smooth, (0, 0))