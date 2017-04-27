from threading import Thread

from scpi_client import ScpiClient


class AGVSensors(Thread):
    main = None

    def __init__(self):
        super(AGVSensors, self).__init__(daemon=True)
        self.main=ScpiClient("/dev/ttyAMA0")
        idn = self.main.idn()
        if not idn:
            yield ConnectionError("Failed to query idn!")
        print("Found sensors! (%s)" % idn)

    def get_distance(self):
        return 0.0

    def get_line(self):
        return 0.0

    def get_battery (self):
        return 0.0

    def run(self):
        while True:
            bat, line, dist = self.main["SENS:BAT?;LINE?;DIST?"]

