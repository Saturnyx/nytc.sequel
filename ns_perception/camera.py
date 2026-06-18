import base64
import logging
import time
import cv2
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

        self.queue_channels = queue_channels
        self.shared_state = shared_state
        self.camera_frame = camera_frame
        self.camera_frame_lock = camera_frame_lock
        self.fps = 30
        self.dt_target = 1 / self.fps
        try:
            self.tj = TurboJPEG(lib_path=TURBOJPEG_PATH)
        except Exception as e:
            logger.exception(e)
            logger.error(
                f"TurboJPEG DLL was not found at {TURBOJPEG_PATH}! Please double check installation!"
            )

        logger.info("Initialised succesfully")

    def readEncodedFrame(self) -> str:
        """Returns raw base64 encoded JPEG frame from robot camera."""
        return (
            self.robot._sdk.VISION.readCameraData().pdata
        )  # reads from low-level unary_unary channel

    def b64_to_numpy_turbo(self, b64_string: str):
        """Converts raw base64 encoded JPEG into numpy array"""
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

class CameraGUIProcessor:
    """Thine only purpose is to make the raw frame usable by DearPyGUI."""

    def __init__(
        self,
        QueueChannels: QueueChannels,
        SharedState: SharedState,
        raw_camera_frame,
        raw_camera_frame_lock,
        camera_frame,
        camera_frame_lock,
    ):
        self.queue_channels = QueueChannels
        self.shared_state = SharedState
        self.camera_frame = camera_frame
        self.camera_frame_lock = camera_frame_lock
        self.raw_camera_frame = raw_camera_frame
        self.raw_camera_frame_lock = raw_camera_frame_lock

        self.width = 640
        self.height = 480

        # self.alpha = np.ones((self.height, self.width), dtype=np.float32)
        # self.output = np.empty((self.height, self.width, 4), dtype=np.float32)

    def process(self, frame):
        if frame is None:
            return None

        # Safety resize if needed
        if frame.shape[0] != self.height or frame.shape[1] != self.width:
            frame = cv2.resize(frame, (self.width, self.height))

        # SHEER OPTIMIZATION:
        # 1. frame[:, :, ::-1] flips BGR to RGB via zero-overhead memory strides
        # 2. .ravel() flattens it to a 1D sequence
        # 3. Converting to float32 and dividing normalizes it perfectly for DPG
        rgb_flat = frame[:, :, ::-1].ravel().astype(np.float32) / 255.0
        return rgb_flat

    def mainloop(self):


        while not self.queue_channels.kill_flag.is_set():
            with self.raw_camera_frame_lock:
                frame = self.raw_camera_frame

            if frame is None:
                time.sleep(0.001)
                continue

            processed = self.process(frame)

            with self.camera_frame_lock:
                self.camera_frame = processed
