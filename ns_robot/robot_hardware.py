from ugot import ugot

import logging

logger = logging.Logger(__name__)

class RobotHardware:
    """Wrapper for the ugot.UGOT instance to allow for custom methods."""

    def __init__(self, queue_channels, shared_state):
        self._sdk = ugot.UGOT()
        self.queue_channels = queue_channels
        self.shared_state = shared_state
