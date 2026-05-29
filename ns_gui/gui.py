import ctypes

import pygame


class GUI:
    def __init__(self):
        pygame.init()
        # Query the user32.dll directly to find screen dimensions
        width = ctypes.windll.user32.GetSystemMetrics(0)  # 0 is for width
        # height = ctypes.windll.user32.GetSystemMetrics(1) # 1 is for height
        self.screen = pygame.display.set_mode((width, width / 180))

    def mainloop(self):
        for event in pygame.event.get():
            if event == pygame.QUIT:
                return 0
