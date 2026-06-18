import logging
import threading

logger = logging.Logger(__name__)


class SharedState:
    def __init__(self):
        # Always create a seperate lock for each variable to prevent chaos.
        self.sbb_camera_frame_lock = threading.Lock()
        self.sbb_camera_frame = None

        self.eng_camera_frame_lock = threading.Lock()
        self.eng_camera_frame = None

        self.raw_webcam_camera_frame_lock = threading.Lock()
        self.raw_webcam_camera_frame = None

        self.webcam_camera_frame_lock = threading.Lock()
        self.webcam_camera_frame = None
