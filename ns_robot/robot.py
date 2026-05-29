class Robot:
    def __init__(self, robot, QueueChannels, SharedState):
        self.robot = robot
        self.queue_channels = QueueChannels
        self.sharedState = SharedState

    def mainloop(self):
        """
        The main purpose of this slave mainloop is to listen to the process_manager mainloop,
        be a good boy, and just be easily killable by process_manager."""
        while not self.queue_channels.kill_flag.is_set():
            pass
        self.robot.mecanum_stop()
        # now it shld die

    def phase1(self):
        pass

    def phase2(self):
        pass

    def phase3(self):
        pass

    def phase4(self):
        pass
