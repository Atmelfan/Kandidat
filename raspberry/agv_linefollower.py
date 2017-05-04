import time

from agv_sensors import AGVSensors
from scpi_client import ScpiClient

dropoff = (-1, 0)
pickup = (-1, 0)




if __name__ == '__main__':
    sensors = AGVSensors()
    motors = ScpiClient("/dev/ttyACM0")

    sensors.start()
    P = 500

    while True:
        #print("%s %d || %s %d" % (sensors.get_line(), sensors.get_rline(), sensors.get_line()[::-1], sensors.get_lline()))
        i = sensors.get_rline()
        if i >= 4:
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




