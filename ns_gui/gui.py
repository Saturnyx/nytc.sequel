import logging
import time

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
        with dpg.texture_registry():  # type: ignore
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
        ) as self.window_tag:  # type: ignore
            dpg.add_image(self.texture_tag, tag=self.image_tag)

    def update(self):
        with self.gui.shared_state.webcam_camera_frame_lock:
            frame = self.gui.shared_state.webcam_camera_frame
        if frame is None:
            return
        dpg.set_value(self.texture_tag, frame.ravel())


class PhaseTimeline(BaseWindow):
    def __init__(self, gui):
        super().__init__(gui, "PhaseTimeline")
        # Data model
        self.phases = []

        # UI tags
        self.window_tag = "PhaseTimeline"
        self.track_drawlist = "timeline_track_drawlist"
        self.header_drawlist = "timeline_header_drawlist"

        # Appearance & Dimensions
        self.sidebar_width = 80
        self.total_width = 1000
        self.track_width = self.total_width - self.sidebar_width

        self.header_height = 16
        self.track_height = 50
        self.window_height = self.header_height + self.track_height + 40

        # Phase block dimensions
        self.phase_width = 110
        self.phase_height = 38  # Bumped slightly to comfortably fit two lines of text
        self.phase_spacing = 4

    def build(self):
        with dpg.window(  # type: ignore
            label=self.title,
            tag=self.window_tag,
            width=self.total_width,
            height=self.window_height,
            pos=[0,1080-self.window_height],
            no_resize=True,
            #no_move=True,
            no_collapse=True,
        ):
            with dpg.group(horizontal=True, horizontal_spacing=0):  # type: ignore

                # --- LEFT SIDEBAR ---
                with dpg.child_window(width=self.sidebar_width, height=self.track_height + self.header_height, border=True):  # type: ignore
                    dpg.add_text("Phases", color=(150, 150, 150))

                # --- RIGHT WORKSPACE ---
                with dpg.group(horizontal_spacing=0):  # type: ignore

                    # 1. Playhead Header Margin Bar
                    with dpg.drawlist(width=self.track_width, height=self.header_height, tag=self.header_drawlist):  # type: ignore
                        pass

                    # 2. Main Track Timeline Background
                    with dpg.drawlist(width=self.track_width, height=self.track_height, tag=self.track_drawlist):  # type: ignore
                        pass

        self.redraw()

    # Added the function_name parameter as requested
    def add_phase(self, name, function_name="None"):
        self.phases.append({"name": name, "function_name": function_name})
        self.redraw()

    def delete_phase(self, index):
        if 0 <= index < len(self.phases):
            del self.phases[index]
        self.redraw()

    def redraw(self):
        dpg.delete_item(self.header_drawlist, children_only=True)
        dpg.delete_item(self.track_drawlist, children_only=True)

        # 1. Draw Grayed-Out Track Background
        dpg.draw_rectangle(
            (0, 0),
            (self.track_width, self.track_height),
            fill=(35, 35, 35, 255),
            color=(55, 55, 55, 255),
            parent=self.track_drawlist,
        )

        # 2. Draw Phases sequentially on the track
        x_offset = 15
        y_center = self.track_height // 2

        for phase in self.phases:
            y1 = y_center - (self.phase_height // 2)
            y2 = y_center + (self.phase_height // 2)

            # Modern flat phase block
            dpg.draw_rectangle(
                (x_offset, y1),
                (x_offset + self.phase_width, y2),
                fill=(54, 106, 201, 255),
                color=(30, 30, 30, 255),
                rounding=3.0,
                parent=self.track_drawlist,
            )

            # Top: Small function name aligned left
            dpg.draw_text(
                (x_offset + 6, y1 + 3),
                phase[
                    "function_name"
                ].upper(),  # Uppercase makes small system text look clean
                parent=self.track_drawlist,
                size=10,
                color=(180, 210, 255, 230),  # Subtle, lighter blue-gray accent color
            )

            # Bottom: Larger phase name aligned left
            dpg.draw_text(
                (x_offset + 6, y1 + 15),
                phase["name"],
                parent=self.track_drawlist,
                size=15,
                color=(255, 255, 255, 255),  # Bright white for readability
            )

            x_offset += self.phase_width + self.phase_spacing

        # 3. Draw Playhead
        playhead_x = self.track_width // 2

        dpg.draw_triangle(
            (playhead_x - 6, 2),
            (playhead_x + 6, 2),
            (playhead_x, self.header_height),
            fill=(230, 40, 40, 255),
            color=(230, 40, 40, 255),
            parent=self.header_drawlist,
        )

        dpg.draw_line(
            (playhead_x, 0),
            (playhead_x, self.track_height),
            color=(230, 40, 40, 220),
            thickness=1,
            parent=self.track_drawlist,
        )


class GUI:
    def __init__(self, QueueChannels, SharedState):
        self.queue_channels = QueueChannels
        self.shared_state = SharedState

        self.windows = []

    def build(self):

        dpg.create_context()
        dpg.configure_app(docking=True, docking_space=True)

        with dpg.font_registry():  # type: ignore

            default_font = dpg.add_font("ns_gui/assets/Inter_18pt-Regular.ttf", 18)

        dpg.bind_font(default_font)

        self.windows.append(CameraWindow(self))
        self.windows.append(PhaseTimeline(self))

        for window in self.windows:
            window.build()

        dpg.create_viewport(
            title="nytc.sequel", width=1920, height=1080, resizable=False
        )

        self.windows[1].add_phase("Phase 1", "phase1")
        self.windows[1].add_phase("Phase 2", "phase2")
        self.windows[1].add_phase("Phase 2A", "opcontrol")
        self.windows[1].add_phase("Phase 3", "phase3")
        self.windows[1].add_phase("Phase 4", "phase4")
        self.windows[1].add_phase("Phase 4A", "opcontrol")

        dpg.setup_dearpygui()
        dpg.show_viewport()

    def mainloop(self):
        last = time.time()
        frames = 0

        while dpg.is_dearpygui_running():
            for window in self.windows:
                window.update()

            dpg.render_dearpygui_frame()

            frames += 1

            if time.time() - last > 1:
                print("GUI FPS:", frames)
                frames = 0
                last = time.time()

        dpg.destroy_context()
