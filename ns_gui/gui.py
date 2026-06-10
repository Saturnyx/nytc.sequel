import ctypes
import logging

import pygame

logger = logging.getLogger(__name__)


class GUI:
    def __init__(self):
        pygame.init()
        # Query the user32.dll directly to find screen dimensions
        width = ctypes.windll.user32.GetSystemMetrics(0)  # 0 is for width
        # height = ctypes.windll.user32.GetSystemMetrics(1) # 1 is for height
        WIDTH = width
        HEIGHT = int(width * (9 / 16))
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        logging.info(f"Screen created ({WIDTH},{HEIGHT})")

    def mainloop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.clock.tick(30)
        pygame.quit()
