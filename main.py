import logging
import sys

import ns_controller
import ns_gui
import ns_logger
import ns_robot
import ns_shared


def main():
    ns_logger.print_logo()
    ns_logger.setup_logging()

    logger = logging.getLogger(__name__)

    logger.log(logging.INFO, "Logging setup successful")

    QueueChannels = ns_shared.QueueChannels()
    logger.log(logging.INFO, "QueueChannels object creation successful")
    SharedState = ns_shared.SharedState()
    logger.log(logging.INFO, "SharedState object creation successful")

    SBBot = ns_robot.RobotHardware(
        QueueChannels,
        SharedState,
        ns_shared.SBBOT_NAME,
        ns_shared.RobotModel.SBBot,
        ns_shared.SBBOT_IP,
    )  # these are wrappers for ugot.UGOT.
    ENGBot = ns_robot.RobotHardware(
        QueueChannels,
        SharedState,
        ns_shared.ENGBOT_NAME,
        ns_shared.RobotModel.ENGBot,
        ns_shared.ENGBOT_IP,
    )  # call SDK methods by RobotHardware._sdk.whatever()
    logger.log(logging.INFO, "SBBot and ENGBot object declaration succesful")

    gui = ns_gui.GUI(QueueChannels, SharedState)
    logger.log(logging.INFO, "GUI initialisation successful")

    process_manager = ns_controller.ProcessManager(
        SBBot, ENGBot, QueueChannels, SharedState
    )

    threads = [ns_shared.construct_thread(process_manager.mainloop)]

    for _ in threads:
        logging.log(logging.INFO, f"Starting thread for {_.name}")
        _.start()

    logging.info("Building GUI...")

    gui.build()

    logging.info("Starting GUI mainloop")

    gui.mainloop()  # ensure pygame runs in the main thread

    logging.log(logging.INFO, "Shutting down...")
    QueueChannels.kill_flag.set()  # signal all threads to die
    logging.log(logging.INFO, "Kill flag set!")

    # now wait for everyone to die, patiently

    for _ in threads:
        _.join()
        logging.log(
            logging.INFO,
            f"Thread {_.name} joined ({threads.index(_) + 1}/{len(threads)})",
        )

    logging.log(logging.INFO, "Program exit")
    # now everyone's dead, rip main! bye im out


if __name__ == "__main__":
    main()
    sys.exit()
