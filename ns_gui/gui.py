import logging

import cv2
import numpy as np
from dearpygui import dearpygui as dpg

logger = logging.getLogger(__name__)


class BaseWindow:
    def __init__(self, gui, title: str):
        self.gui = gui
        self.title = title
        self.window_tag = None

    def build(self):
        raise NotImplementedError

    def update(self):
        pass


class CameraWindow(BaseWindow):
    def __init__(self, gui):
        super().__init__(gui, "Camera")

        self.texture_tag = "camera_texture"
        self.image_tag = "camera_image"

        self.width = 640
        self.height = 480
        self.rgba_buffer = np.empty((480, 640, 4), dtype=np.float32)

    def build(self):
        # dpg.set_item_callback(self.texture_tag, lambda: None)
        with dpg.texture_registry():
            dpg.add_dynamic_texture(
                width=self.width,
                height=self.height,
                default_value=[0.0] * (self.width * self.height * 4),
                tag=self.texture_tag,
            )

        with dpg.window(
            label=self.title,
            width=self.width + 20,
            height=self.height + 40,
        ) as self.window_tag:
            dpg.add_image(self.texture_tag, tag=self.image_tag)

    def update(self):
        with self.gui.shared_state.webcam_camera_frame_lock:
            frame = self.gui.shared_state.webcam_camera_frame

        if frame is None:
            return
        # force correct size ALWAYS
        frame = cv2.resize(frame, (self.width, self.height))

        # ensure RGB float
        frame = frame.astype(np.float32) / 255.0

        # add alpha channel
        alpha = np.ones((self.height, self.width, 1), dtype=np.float32)
        frame = np.concatenate((frame, alpha), axis=2)

        dpg.set_value(self.texture_tag, frame.ravel())


class GUI:
    def __init__(self, QueueChannels, SharedState):
        self.queue_channels = QueueChannels
        self.shared_state = SharedState

        self.windows = []

    def build(self):

        dpg.create_context()
        dpg.configure_app(docking=True, docking_space=True)
        self.windows.append(CameraWindow(self))

        for window in self.windows:
            window.build()

        dpg.create_viewport(
            title="Robot Control",
            width=1280,
            height=720,
        )

        dpg.setup_dearpygui()
        dpg.show_viewport()

    def mainloop(self):

        while dpg.is_dearpygui_running():
            for window in self.windows:
                window.update()

            dpg.render_dearpygui_frame()

        dpg.destroy_context()
