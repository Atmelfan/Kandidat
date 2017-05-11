import time

from agv_linefollow import LineMode
from agv_signs import AGVSigns


def get_closest_tag(tags):
    if not tags:
        return None
    return min(tags, key=lambda t: t[3])


def get_agvs(tags):
    return [t for t in tags if AGVSigns.get_type(t[0]) == AGVSigns.TYPE_REGISTRATION]


class AGVState(object):
    def __init__(self, datastore):
        super(AGVState, self).__init__()
        self.datastore = datastore

    # get_name()
    # Returns the state name, e.g. "START" or "LEADING"
    def get_name(self):
        return "???"

    # start()
    # Called when the state is switched to
    #
    def start(self):
        print("State %s started!" % self.get_name())

    # update(aruco_tags, line_data)
    # Called during the control loop
    # Returns a new state to switch to or None to continue
    def update(self, tags, line):
        #print("%s update: %s, %s" % (self.get_name(), tags, line))
        return None

    # on_command()
    #
    #
    def on_command(self, command):
        return None

    def stop(self):
        print("State %s stopped!" % self.get_name())

    def override(self, tags, sensors, motors):
        pass

    def line_mode(self):
        return LineMode.DISABLE

    def log(self):
        return "%s" % self.get_name()

    def speed_factor(self):
        return 1.0



class AGVStateFault(AGVState):
    def __init__(self, msg = "MissingNo?"):
        super(AGVState, self).__init__()

    def get_name(self):
        return "FAULT %s"


class AGVStateStop(AGVState):
    def __init__(self, datastore):
        super(AGVStateStop, self).__init__(datastore)

    def update(self, tags, line):
        #print("Closest %s; agvs: %s" % (get_closest_tag(tags), get_agvs(tags)))
        return super().update(tags, line)

    def get_name(self):
        return "STOP"


class AGVStateFollow(AGVState):
    def __init__(self, datastore):
        super(AGVStateFollow, self).__init__(datastore)
        self.front = -1

    def get_name(self):
        return "LEADING" if self.datastore["lead"] else "FOLLOWING %d" % self.front

    def update(self, tags, line):
        station = self.datastore['station']
        drop = self.datastore['drop']
        closest_agv = get_closest_tag(get_agvs(tags))
        self.front = closest_agv[0] if closest_agv else -1
        #print("%02x" % AGVSigns.make_id(AGVSigns.TYPE_STATION_ENTER, station))
        if drop != 0 and station != -1 and any(tag[0] == AGVSigns.make_id(AGVSigns.TYPE_STATION_ENTER, station) and tag[3] < 1000 for tag in tags):
            print("Found my runway!")
            return AGVStateStationEnter(self.datastore)
        return super().update(tags, line)

    def line_mode(self):
        return LineMode.KEEP_LEFT

    def speed_factor(self):
        return 0.5 if self.datastore["lead"] else super().speed_factor()


class AGVStateStart(AGVState):
    def __init__(self, datastore):
        super(AGVStateStart, self).__init__(datastore)
        self.has_line = False
        self.finished = False
        self.t = 0.0

    def update(self, tags, line):
        if any(line.get_actual_line()) and not self.has_line:
            self.t = time.time()
            self.has_line = True
        if self.finished:
            return AGVStateStart2(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "START"

    def override(self, tags, sensors, motors):
        if time.time() - self.t < 1.0:
            motors.send(("ch1:dir %s; vel %d\n\r" % ("FORW", 500)).encode(), 0)
            motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK", 500)).encode(), 0)
        else:
            motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK", 0)).encode(), 0)
            motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK", 0)).encode(), 0)
            self.finished = True

        super().override(tags, sensors, motors)

    def speed_factor(self):
        return 0.25

    def line_mode(self):
        return LineMode.KEEP_STRAIGHT if not self.has_line else LineMode.OVERRIDE


class AGVStateStart2(AGVState):
    def __init__(self, datastore):
        super(AGVStateStart2, self).__init__(datastore)
        self.has_line = False
        self.finished = False
        self.t = 0.0

    def update(self, tags, line):
        if line.get_actual_line()[7]:
            return AGVStateFollow(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "START"

    def speed_factor(self):
        return 0.25

    def line_mode(self):
        return LineMode.KEEP_STRAIGHT


class AGVStateStationEnter(AGVState):
    def __init__(self, datastore):
        super(AGVStateStationEnter, self).__init__(datastore)

    def update(self, tags, line):
        #print("UPDATE!")
        station = self.datastore['station']
        #print("%02x"%station)
        if station != -1 and any(tag[0] == AGVSigns.make_id(AGVSigns.TYPE_STATION_STOP, station) and tag[3] < 1000 for tag in tags):
            print("Found my stop!")
            return AGVStateStationStop(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "STATION ENTER"

    def line_mode(self):
        return LineMode.KEEP_RIGHT

    def speed_factor(self):
        return 0.4


class AGVStateStationExit(AGVState):
    def __init__(self, datastore):
        super(AGVStateStationExit, self).__init__(datastore)

    def update(self, tags, line):
        closest_agv = get_agvs(tags)
        if closest_agv:
            return AGVStateFollow(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "STATION EXIT"

    def line_mode(self):
        return LineMode.DISABLE

    def speed_factor(self):
        return 0.4

TIME_TO_WAIT = 5


class AGVStateStationStop(AGVState):
    def __init__(self, datastore):
        super(AGVStateStationStop, self).__init__(datastore)
        self.t = time.time()
        passengers = datastore['passengers']
        old = passengers
        drop = datastore['drop']
        if drop < 0:# pick up
            passengers -= drop
            drop = 0
        else: # drop off
            amount = min(passengers, drop)
            passengers -= amount
            drop -= amount

        datastore['passengers'] = passengers
        datastore['drop'] = drop
        print("Dropped off %d of %d passengers" % (old - passengers, old))

    def update(self, tags, line):
        station = self.datastore['station']
        if line.get_linewidth() > 4:
            return AGVStateStationExit(self.datastore)
        #if station != -1 and any(tag[0] == AGVSigns.make_id(AGVSigns.TYPE_STATION_EXIT, station) and tag[3] < 1000 for tag in tags):
        #    return AGVStateStationExit(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "STATION STOP"

    def line_mode(self):
        return LineMode.KEEP_LEFT if time.time() - self.t > TIME_TO_WAIT else LineMode.DISABLE

    def speed_factor(self):
        return 0.4



