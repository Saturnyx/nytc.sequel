import logging
import time

import pygame  # for controller
from numpy.testing import print_assert_equal

# from ugot import ugot
import ns_robot
import ns_shared

logger = logging.getLogger(__name__)


class RobotController:
    def __init__(
        self,
        sbbot: ns_robot.RobotHardware,
        engbot: ns_robot.RobotHardware,
        QueueChannels,
        SharedState,
    ):

        self.queue_channels = QueueChannels
        self.sharedState = SharedState

        if not ns_shared.DEBUG_MODE:
            self.setup_engbot(engbot)
            self.setup_sbbot(sbbot)

    def setup_engbot(self, engbot):
        self.engbot = engbot
        logger.info("Attempting to connect ENGBot...")
        self.engbot.connect()

    def setup_sbbot(self, sbbot):
        self.sbbot = sbbot
        logger.info("Attempting to connect SBBot...")
        self.sbbot.connect()

    def mainloop(self):
        """
        The main purpose of this slave mainloop is to listen to the process_manager mainloop,
        be a good boy, and just be easily killable by process_manager."""

        # very temporary just for testing please delete later

        while not self.queue_channels.kill_flag.is_set():
            self.sharedState.phase_state.is_running.wait()  # this will freeze the thread until it is running
            match self.sharedState.phase_state.phase_queue[
                self.sharedState.phase_state.current_phase_index
            ]:
                case ns_shared.Phase.Phase1:
                    self.phase1()
                case ns_shared.Phase.Phase2:
                    self.phase2()
                case ns_shared.Phase.Phase2A:
                    self.phase2a()
                case ns_shared.Phase.Phase3:
                    self.phase3()
                case ns_shared.Phase.Phase4:
                    self.phase4()
                case ns_shared.Phase.Phase4A:
                    self.phase4a()
                case _:
                    logger.error(
                        f"The phase {
                            self.sharedState.phase_state.phase_queue[
                                self.sharedState.phase_state.current_phase_index
                            ]
                        } does not have a corresponding function tied to it in robot_controller!"
                    )
                    self.advance_phase()  # to make sure nothing softlocks
        # try and kill bots
        if not ns_shared.DEBUG_MODE:
            self.kill_bots()
        # now it shld die

    # def test(self):
    #     self.engbot._sdk.mecanum_motor_control(360, 360, 360, 360)
    #     # time.sleep(2)
    #     self.engbot._sdk.mecanum_move_speed_times(0, 80, 2, 0)
    #     self.engbot._sdk.mecanum_stop()
    #     time.sleep(10)

    def kill_bots(self):
        try:
            self.sbbot._sdk.balance_stop_balancing()
        except Exception as e:
            logger.exception(e)
            logger.warning("FAILED TO STOP SBBOT, WARNING!")
        try:
            self.engbot._sdk.mecanum_stop()
        except Exception as e:
            logger.exception(e)
            logger.warning("FAILED TO STOP SBBOT, WARNING!")

    def phase1(self):
        """sbb moves to april tag"""
        time.sleep(1)
        self.advance_phase()

    def phase2(self):
        time.sleep(1)
        self.advance_phase()

    # with self.gui.shared_state.webcam_camera_frame_lock:
    #   frame = self.gui.shared_state.webcam_camera_frame
    # sharedState
    # shared_state
    # SharedState

    def phase2a(self):
        # call opcontrol portion
        self.opcontrol()
        self.advance_phase()

    def phase3(self):
        time.sleep(1)
        self.advance_phase()

    def phase4(self):
        time.sleep(1)
        self.advance_phase()

    def phase4a(self):
        # call opcontrol portion
        self.opcontrol()
        self.advance_phase()

    def opcontrol(self):
        time.sleep(1)

    def advance_phase(self):
        with self.sharedState.phase_state.lock:
            if self.sharedState.phase_state.current_phase_index is None:
                self.sharedState.phase_state.current_phase_index = 0
            else:
                self.sharedState.phase_state.current_phase_index += 1

            # Check if we ran out of phases
            if self.sharedState.phase_state.current_phase_index >= len(
                self.sharedState.phase_state.phase_queue
            ):
                self.sharedState.phase_state.current_phase_index = None
            self.sharedState.phase_state.is_running.clear()
