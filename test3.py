import threading
import time

from ugot import ugot

from ns_shared import ENGBOT_IP


def print_the_damn_encoder_thing(bot: ugot.UGOT):
    while True:
        print(bot.read_motor_speed(1))


got = ugot.UGOT()
got.initialize(ENGBOT_IP)

t = threading.Thread(target=print_the_damn_encoder_thing, daemon=True, args=(got,))
# t.start()
print("started")
time.sleep(1)
print("stargint movement")
print(got.MODEL.mecanum_xyz_control(0, 0, 45))
time.sleep(2)
got.MODEL.mecanum_xyz_control(0, 0, 0)
print("movement stopped")
time.sleep(1)
# t.join()
