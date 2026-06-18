import base64
import cv2
import numpy as np
import logging
import queue

logger = logging.getLogger(__name__)

class BlockDetector:
    def __init__(
        self,
        QueueChannels,  # ns_shared.QueueChannels
        SharedState,    # ns_shared.SharedState
    ):
        self.queue_channels = QueueChannels
        self.shared_state = SharedState

        # --- 1. PHYSICAL & CALIBRATION PARAMETERS ---
        self.cube_real_width = 5.0
        self.calibrated_focal_length = 650.0

        # --- 2. HSV COLOR SELECTION BOUNDS (For Standard BGR-to-HSV conversion) ---
        self.lower_color = np.array([0, 120, 70])
        self.upper_color = np.array([10, 255, 255])

        self.min_contour_area = 200
        self.morphology_kernel = np.ones((3, 3), np.uint8)

        logger.info("BlockDetector initialized for Robot Camera stream successfully")

    def get_latest_frame(self):
        """Safely pulls a local copy of the frame from the robot camera's shared state."""
        # Adjust this lock and variable name to match wherever you save your robot's numpy frame!
        with self.shared_state.robot_camera_frame_lock:
            frame = self.shared_state.robot_camera_frame

        if frame is None:
            return None

        # Since TurboJPEG returns a clean numpy array, we can just return it.
        # If your background thread modifies it, use frame.copy(), otherwise pass-through for speed.
        return frame

    def process_frame(self, frame):
        """Performs sheer-optimized math tracking loops over the BGR robot frame."""
        if frame is None:
            return None

        # SHEER OPTIMIZATION: TurboJPEG decodes to BGR by default.
        # We pass it straight into BGR2HSV with zero overhead.
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.morphology_kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_blocks = []

        for cnt in contours:
            if cv2.contourArea(cnt) < self.min_contour_area:
                continue

            x, y, w, h = cv2.boundingRect(cnt)

            aspect_ratio = float(w) / h
            if not (0.75 <= aspect_ratio <= 1.35):
                continue

            moments = cv2.moments(cnt)
            if moments["m00"] == 0:
                continue
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])

            # Triangle Similarity math
            distance_z = (self.cube_real_width * self.calibrated_focal_length) / w

            detected_blocks.append({
                "pixel_center": (cx, cy),
                "pixel_bounds": (x, y, w, h),
                "distance_z": distance_z
            })

        return detected_blocks

    def update_data_queue(self, data):
        """Gracefully drops data into the Size-1 tracking queue."""
        if data is None:
            return

        if self.queue_channels.block_detection_data.full():
            try:
                self.queue_channels.block_detection_data.get_nowait()
            except queue.Empty:
                pass

        try:
            self.queue_channels.block_detection_data.put_nowait(data)
        except queue.Full:
            pass

    def mainloop(self):
        """Continuously running tracking loop bound to the process kill flag."""
        while not self.queue_channels.kill_flag.is_set():
            frame = self.get_latest_frame()
            blocks_data = self.process_frame(frame)
            self.update_data_queue(blocks_data)
