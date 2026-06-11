"""Contains a bunch of dataclasses which signify QueueChannel events
so I don't have to use magic strings."""

from dataclasses import dataclass


@dataclass
class pose_change_direction:
    heading = int
