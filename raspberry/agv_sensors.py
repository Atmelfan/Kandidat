
from threading import Thread, Lock

import time

import _thread

from scpi_client import ScpiClient


class AGVSensors(Thread):

    DIST_C_TO_V = 4.9/4096.0

    def __init__(self):
        super(AGVSensors, self).__init__(daemon=True)
        self.main=ScpiClient("/dev/ttyAMA0")
        idn = self.main.idn()
        print("[SENSORS] Found sensors! (%s)" % idn)
        self.start()
        self.realline = [False for x in range(0, 8)]
        self.actual = [False for x in range(0, 8)]

        self.dist = [0.0, 0.0, 0.0]
        self.lock = Lock()
        self.battery = 0

    def get_linewidth(self):
        return 8 - self.get_lline() - self.get_rline()

    def get_distance(self):
        with self.lock:
            return min([13.0/(self.DIST_C_TO_V*c) for c in self.dist[0:1]])

    def get_lastline(self):
        with self.lock:
            return self.realline

    def get_rline(self):
        try:
            return self.get_lastline().index(True)
        except ValueError:
            return -1

    def get_lline(self):
        try:
            return 7 - self.get_lastline()[::-1].index(True)
        except ValueError:
            return -1

    def get_battery (self):
        return self.battery

    def get_actual_line(self):
        return self.actual

    def run(self):
        print("[SENSORS] Started...")
        while True:
            line, dist, bat = self.main[b"SENS:LINE?;DIST?;BAT?"]
            try:
                self.battery = float(bat)

                self.dist = [float(s) for s in dist.split()]
                line = [int(s) > 3000 for s in line.split()]
                self.actual = [line[3], line[0], line[1], line[2], line[4], line[6], line[7], line[5]]
                if any(line):
                    self.realline = [line[3], line[0], line[1], line[2], line[4], line[6], line[7], line[5]]
                #print(self.realline)
            except ValueError as ve:
                print("%s %s: %s" % (line, dist, ve))
            except IndexError as ve:
                print("%s %s: %s" % (line, dist, ve))

            time.sleep(0.02)
            #print(self.get_distance())


