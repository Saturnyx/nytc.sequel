import logging
import time

import cv2

import ns_shared

logger = logging.getLogger(__name__)


class Webcam:
    def __init__(
        self,
        QueueChannels: ns_shared.QueueChannels,
        SharedState: ns_shared.SharedState,
        camera_frame,
        camera_frame_lock,
    ):
        self.queue_channels = QueueChannels
        self.shared_state = SharedState
        self.camera_frame = camera_frame
        self.camera_frame_lock = camera_frame_lock

        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FPS, 30)
        if not self.capture.isOpened():
            raise RuntimeError("Camera failed to open")
        logger.info("Initialised succesfully")

    def poll_camera_frame(self):
        self.capture.grab()  # fast: just grab latest frame
        ret, frame = self.capture.retrieve()

        if not ret:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def put_camera_frame(self, frame):
        with self.shared_state.webcam_camera_frame_lock:
            self.shared_state.webcam_camera_frame = frame

    def mainloop(self):
        while not self.queue_channels.kill_flag.is_set():
            self.put_camera_frame(self.poll_camera_frame())
            time.sleep(0.001)
