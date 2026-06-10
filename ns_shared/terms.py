import logging
from enum import Enum

logger = logging.Logger(__name__)


class State(Enum):
    """Class defining primary states/phases"""

    IDLE = 0

    Phase1 = 1
    Phase2 = 2
    Phase3 = 3
    Phase4 = 4


class MicroState(Enum):
    """this was gonna be used to flag the microstates of the shovelling red blue blocks
    task, not sure if I'll use it, but it's here"""

    pass


class RobotModel:
    SBBot = "SBBot"
    ENGBot = "ENGBot"
