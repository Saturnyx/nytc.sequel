import logging
from enum import Enum

logger = logging.Logger(__name__)

class PhaseType(Enum):
    """Class defining the two PhaseTypes (primarily for GUI usage.)"""
    AUTONOMOUS = "Autonomous"
    MANUAL = "Manual"

class Phase(Enum):
    """Class defining primary states/phases"""
    Phase1 = ("Phase 1", PhaseType.AUTONOMOUS)
    Phase2 = ("Phase 2", PhaseType.AUTONOMOUS)
    Phase2A = ("Phase 2A", PhaseType.MANUAL)
    Phase3 = ("Phase 3", PhaseType.AUTONOMOUS)
    Phase4 = ("Phase 4", PhaseType.AUTONOMOUS)
    Phase4A = ("Phase 4A", PhaseType.MANUAL)


class MicroState(Enum):
    """this was gonna be used to flag the microstates of the shovelling red blue blocks
    task, not sure if I'll use it, but it's here"""

    pass


class RobotModel:
    SBBot = "SBBot"
    ENGBot = "ENGBot"
