import base64
import logging
import time

import numpy as np
from turbojpeg import TurboJPEG

from ns_robot import RobotHardware
from ns_shared import TURBOJPEG_PATH, QueueChannels, SharedState

logger = logging.getLogger(__name__)


class Camera:
    def __init__(
        self,
        robot: RobotHardware,
        queue_channels: QueueChannels,
        shared_state: SharedState,
        camera_frame,
        camera_frame_lock,
    ):
        self.robot = robot
        self.tj = TurboJPEG(lib_path=TURBOJPEG_PATH)
        self.queue_channels = queue_channels
        self.shared_state = shared_state
        self.camera_frame = camera_frame
        self.camera_frame_lock = camera_frame_lock
        self.fps = 30
        self.dt_target = 1 / self.fps

        logger.info("Initialised succesfully")

    def readEncodedFrame(self) -> str:
        """Returns raw base64 encoded JPEG frame from robot camera."""
        return (
            self.robot._sdk.VISION.readCameraData().pdata
        )  # reads from low-level unary_unary channel

    def b64_to_numpy_turbo(self, b64_string: str):
        """Converts raw base64 encoded JPEG into pygame surface"""
        jpg_bytes = base64.b64decode(b64_string)
        if not jpg_bytes:
            return None
        print(jpg_bytes)
        return self.tj.decode(jpg_bytes)  # returns a numpy array (H, W, 3)

    def mainloop(self):
        while not self.queue_channels.kill_flag.is_set():
            start_time = time.perf_counter()
            frame = self.b64_to_numpy_turbo(self.readEncodedFrame())
            with self.camera_frame_lock:
                # now we have access
                self.camera_frame = frame
            # now we release the lock, calculate delta time and do dynamic delays
            end_time = time.perf_counter()
            dt = end_time - start_time
            sleep_time = self.dt_target - dt
            if sleep_time > 0:
                time.sleep(sleep_time)
