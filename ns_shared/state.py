import logging
import threading
from ns_shared.config import DEFAULT_TIMELINE_CONFIG
logger = logging.Logger(__name__)


class SharedState:
    def __init__(self):
        # Always create a seperate lock for each variable to prevent chaos.
        self.sb_camera_frame_lock = threading.Lock()
        self.sb_camera_frame = None

        self.sb_gui_camera_frame_lock = threading.Lock()
        self.sb_gui_camera_frame = None

        self.eng_camera_frame_lock = threading.Lock()
        self.eng_camera_frame = None

        self.eng_gui_camera_frame_lock = threading.Lock()
        self.eng_gui_camera_frame = None

        self.raw_webcam_camera_frame_lock = threading.Lock()
        self.raw_webcam_camera_frame = None

        self.webcam_camera_frame_lock = threading.Lock()
        self.webcam_camera_frame = None

        self.phase_list_lock = threading.Lock()
        self.phase_list = list(DEFAULT_TIMELINE_CONFIG)
