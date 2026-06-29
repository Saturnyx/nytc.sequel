import logging
import os
import time

import pygame

from ns_shared import QueueChannels, SharedState

logger = logging.getLogger(__name__)

os.environ["SDL_JOYSTICK_HIDAPI_PS4_RUMBLE"] = "1"


class PS4ControllerDriver:
    def __init__(self, queue_channels: QueueChannels, shared_state: SharedState):
        self.queue_channels = queue_channels
        self.shared_state = shared_state

        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        self.deadzone = 0.12  # Filters out analog drift when sticks are resting

    def init_controller(self) -> bool:
        """Attempts to discover and lock onto a connected PS4 controller."""
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            logger.warning("No joysticks detected! Retrying...")
            return False

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        logger.info(f"Successfully locked onto controller: {self.joystick.get_name()}")
        self.joystick.rumble(0.5, 0.5, 250)
        return True

    def filter_deadzone(self, value: float) -> float:
        """Clips small analog stick outputs to prevent the robot from creeping."""
        if abs(value) < self.deadzone:
            return 0.0
        # Smooth out scale after deadzone reduction
        return (value - (self.deadzone * (1 if value > 0 else -1))) / (
            1.0 - self.deadzone
        )

    def mainloop(self):
        """Dedicated loop pumping hardware events and publishing vectors to state."""
        # Loop until controller is physically found
        while not self.queue_channels.kill_flag.is_set() and not self.joystick:
            if not self.init_controller():
                time.sleep(2.0)

        # Standard mapping layout for PS4 controller over Pygame

        # Left Stick:
        # Left -> Right   - Axis 0
        # Up   -> Down    - Axis 1

        # Right Stick:
        # Left -> Right   - Axis 2
        # Up   -> Down    - Axis 3

        # Left Trigger:
        # Out -> In       - Axis 4

        # Right Trigger:
        # Out -> In       - Axis 5

        # Buttons:
        # Cross Button    - Button 0
        # Circle Button   - Button 1
        # Square Button   - Button 2
        # Triangle Button - Button 3
        # Share Button    - Button 4
        # PS Button       - Button 5
        # Options Button  - Button 6
        # L. Stick In     - Button 7
        # R. Stick In     - Button 8
        # Left Bumper     - Button 9
        # Right Bumper    - Button 10
        # D-pad Up        - Button 11
        # D-pad Down      - Button 12
        # D-pad Left      - Button 13
        # D-pad Right     - Button 14
        # Touch Pad Click - Button 15

        while not self.queue_channels.kill_flag.is_set():
            pygame.event.pump()  # Must be called regularly to update states internally

            # 1. Capture Analog Stick Movements
            # Note: Pygame reads Y-axis inverted (Up is negative), so we flip it
            raw_x = self.joystick.get_axis(0)
            raw_y = -self.joystick.get_axis(1)
            raw_r = -self.joystick.get_axis(2)

            # 2. Process math limits
            x_vel = self.filter_deadzone(raw_x)
            y_vel = self.filter_deadzone(raw_y)
            r_vel = self.filter_deadzone(raw_r)

            # 3. Safely update coordinates
            with self.shared_state.drive_command_lock:
                self.shared_state.drive_x = x_vel
                self.shared_state.drive_y = y_vel
                self.shared_state.drive_r = r_vel

                # 4. Handle button callbacks (mapping can vary by OS, check default layout indices)
                self.shared_state.controller_buttons["cross"] = bool(
                    self.joystick.get_button(0)
                )
                self.shared_state.controller_buttons["circle"] = bool(
                    self.joystick.get_button(1)
                )

            # time.sleep(0.02)  # ~50Hz sampling is more than fast enough for human inputs
