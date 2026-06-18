import logging

# import ns_shared
import time

# from ugot import ugot
import ns_robot

logger = logging.getLogger(__name__)


class RobotController:
    def __init__(
        self,
        sbbot: ns_robot.RobotHardware,
        engbot: ns_robot.RobotHardware,
        QueueChannels,
        SharedState,
    ):
        self.sbbot = sbbot
        self.engbot = engbot
        self.queue_channels = QueueChannels
        self.sharedState = SharedState

        # logger.info("Attempting to connect SBBot...")
        # self.sbbot.connect()
        # logger.info("Attempting to connect ENGBot...")
        # self.engbot.connect()

    def mainloop(self):
        """
        The main purpose of this slave mainloop is to listen to the process_manager mainloop,
        be a good boy, and just be easily killable by process_manager."""
        self.engbot._sdk.mecanum_stop()
        while not self.queue_channels.kill_flag.is_set():
            self.phase1()
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

        # now it shld die

    def phase1(self):
        # self.engbot._sdk.mecanum_motor_control(360, 360, 360, 360)
        # time.sleep(2)
        self.engbot._sdk.mecanum_move_speed_times(0, 80, 2, 0)
        self.engbot._sdk.mecanum_stop()
        time.sleep(10)

    def phase2(self):
        pass

    def phase3(self):
        pass

    def phase4(self):
        pass
