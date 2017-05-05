from threading import Thread

import time

from scpi_client import ScpiClient


class AGVSensors(Thread):
    main = None
    realline = []

    def __init__(self):
        super(AGVSensors, self).__init__(daemon=True)
        self.main=ScpiClient("/dev/ttyS0")
        idn = self.main.idn()
        print("[SENSORS] Found sensors! (%s)" % idn)
        self.start()

    def get_distance(self):
        return 0.0

    def get_line(self):
        return self.realline

    def get_rline(self):
        try:
            return self.realline.index(True)
        except ValueError:
            return -1

    def get_lline(self):
        try:
            return 7 - self.realline[::-1].index(True)
        except ValueError:
            return -1

    def get_battery (self):
        return 0.0

    def run(self):
        while True:
            line, dist = self.main[b"SENS:LINE?;DIST?"]
            line = [float(s) > 0.75 for s in line.split()]
            if any(line):
                self.realline = [line[3], line[0], line[1], line[2], line[4], line[6], line[7], line[5]]
            #print(self.realline)
            time.sleep(0.1)


