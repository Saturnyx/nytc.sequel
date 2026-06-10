import threading
import logging
import time

from ugot import ugot

import ns_controller
import ns_gui
import ns_shared
import ns_robot
import ns_logger

logger = logging.Logger(__name__)

def main():
    ns_logger.setup_logging()
    ns_logger.print_logo()

    QueueChannels = ns_shared.QueueChannels()
    SharedState = ns_shared.SharedState()

    SBBot = ns_robot.RobotHardware(
        QueueChannels, SharedState
    )  # these are wrappers for ugot.UGOT.
    ENGBot = ns_robot.RobotHardware(
        QueueChannels, SharedState
    )  # call SDK methods by RobotHardware._sdk.whatever()

    gui = ns_gui.GUI()
    process_manager = ns_controller.ProcessManager(
        SBBot, ENGBot, QueueChannels, SharedState
    )

    threads = [
        threading.Thread(target=process_manager.mainloop()),
    ]

    for _ in threads:
        _.start()

    gui.mainloop()  # ensure pygame runs in the main thread

    QueueChannels.kill_flag.set()  # signal all threads to die

    # now wait for everyone to die, patiently

    for _ in threads:
        _.join()

    # now everyone's dead, rip main! bye im out


if __name__ == "__main__":
    main()
