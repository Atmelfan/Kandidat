import time
from enum import Enum

from agv_camera import AGVCamera
from agv_linefollow import LineMode
from bluetooth_server import BluetoothServer
from states import *

from agv_sensors import AGVSensors
from scpi_client import ScpiClient

if __name__ == '__main__':
    bluetooth = BluetoothServer(name="AGV-3")
    sensors = AGVSensors()
    motors = ScpiClient("/dev/ttyACM0")
    mode = LineMode.DISABLE
    state = AGVStateStop()
    cameras = AGVCamera()
    time.sleep(1)

    parameters = {"Dropoff":2}

    print("[MAIN] Starting main loop...")
    P = 500

    state.start() #initialize start state
    try:
        while True:
            #print("%s %d || %s %d" % (sensors.get_line(), sensors.get_rline(), sensors.get_line()[::-1], sensors.get_lline()))
            try:
                next_state = state.update(cameras.get_tags(), sensors.get_line())
                if next_state:
                    print("Switching state from [%s] to [%s]!" % (state.get_name(), next_state.get_name()))
                    state.stop()#clean stop of last state
                    state = next_state #switch state
                    state.start()#initialize new state
                mode = state.line_mode()
                print("%s" % mode.name)

            except Exception as e:
                print("Unexpected error during state update: %s" % e)

            i = sensors.get_rline() if mode == LineMode.KEEP_RIGHT else sensors.get_lline()
            if mode == LineMode.KEEP_STRAIGHT:
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK", 500)).encode(), 0)
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK", 500)).encode(), 0)
            elif i == -1 or mode == LineMode.DISABLE:
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK", 0)).encode(), 0)
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK", 0)).encode(), 0)
            elif i >= 4:
                react = (i - 4 + 1)*P
                lly = 1500-react
                rly = 1500
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK" if lly > 0 else "FORW", abs(lly))).encode(),0)
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK" if rly > 0 else "FORW", abs(rly))).encode(), 0)
            else:
                react = (3 - i + 1)*P
                lly = 1500 - react
                rly = 1500
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK" if lly > 0 else "FORW", abs(lly))).encode(), 0)
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK" if rly > 0 else "FORW", abs(rly))).encode(), 0)
            print("!2")
            time.sleep(0.05)
    except KeyboardInterrupt as e:
        pass
    finally:
        motors.send(("ch1:dir %s; vel %d\n\r" % ("FORW", 0)).encode(), 0)
        motors.send(("ch2:dir %s; vel %d\n\r" % ("FORW", 0)).encode(), 0)





