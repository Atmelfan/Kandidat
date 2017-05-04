import time
from enum import Enum

from agv_linefollow import LineMode
from states import *

from agv_sensors import AGVSensors
from scpi_client import ScpiClient

if __name__ == '__main__':
    sensors = AGVSensors()
    motors = ScpiClient("/dev/ttyACM0")
    mode = LineMode.KEEP_RIGHT
    state = AGVStateStop()

    sensors.start()
    P = 500

    while True:
        #print("%s %d || %s %d" % (sensors.get_line(), sensors.get_rline(), sensors.get_line()[::-1], sensors.get_lline()))
        try:
            next_state = state.update()
            if next_state:
                print("Switching state from [%s] to [%s]!" % (state.get_name(), next_state.get_name()))
                state = next_state

        except Exception:
            print("Unexpected error during state update!")

        i = sensors.get_rline() if mode == LineMode.KEEP_RIGHT else sensors.get_lline()
        if i == -1:
            motors.send(("ch1:dir %s; vel %d\n\r" % ("FORW", 0)).encode(), 0)
            motors.send(("ch2:dir %s; vel %d\n\r" % ("FORW", 0)).encode(), 0)
        elif i >= 4:
            react = (i - 4)*P
            lly = 1500-react
            rly = 1500
            motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK" if lly > 0 else "FORW", abs(lly))).encode(),0)
            motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK" if rly > 0 else "FORW", abs(rly))).encode(), 0)
        else:
            react = (3 - i)*P
            lly = 1500 - react
            rly = 1500
            motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK" if lly > 0 else "FORW", abs(lly))).encode(), 0)
            motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK" if rly > 0 else "FORW", abs(rly))).encode(), 0)

        time.sleep(0.05)




