import time

from agv_linefollow import LineMode
from agv_signs import AGVSigns


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

    def override(self, next_state):
        pass

    def line_mode(self):
        return LineMode.DISABLE

    def log(self):
        return "%s" % self.get_name()


class AGVStateFault(AGVState):
    def __init__(self, msg = "MissingNo?"):
        super(AGVState, self).__init__()

    def get_name(self):
        return "FAULT %s"


class AGVStateStop(AGVState):
    def __init__(self, datastore):
        super(AGVStateStop, self).__init__(datastore)

    def get_name(self):
        return "STOP"


class AGVStateFollow(AGVState):
    def __init__(self, datastore):
        super(AGVStateFollow, self).__init__(datastore)

    def get_name(self):
        return "FOLLOW"

    def update(self, tags, line):
        station = self.datastore['station']
        drop = self.datastore['drop']
        #print("%02x" % AGVSigns.make_id(AGVSigns.TYPE_STATION_ENTER, station))
        if drop != 0 and station != -1 and any(tag[0] == AGVSigns.make_id(AGVSigns.TYPE_STATION_ENTER, station) for tag in tags):
            print("Found my runway!")
            return AGVStateStationEnter(self.datastore)
        return super().update(tags, line)

    def line_mode(self):
        return LineMode.KEEP_LEFT

#nav:start;pick 0 1
    def log(self):
        return "%s %d" % (self.get_name(), 0)


class AGVStateLead(AGVState):
    def __init__(self, datastore):
        super(AGVStateLead, self).__init__(datastore)

    def get_name(self):
        return "LEAD"


class AGVStateStart(AGVState):
    def __init__(self, datastore):
        super(AGVStateStart, self).__init__(datastore)

    def update(self, tags, line):
        if any(line):
            return AGVStateFollow(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "START"

    def line_mode(self):
        return LineMode.KEEP_STRAIGHT


class AGVStateStationEnter(AGVState):
    def __init__(self, datastore):
        super(AGVStateStationEnter, self).__init__(datastore)

    def update(self, tags, line):
        #print("UPDATE!")
        station = self.datastore['station']
        #print("%02x"%station)
        if station != -1 and any(tag[0] == 0xD0 for tag in tags):
            print("Found my stop!")
            return AGVStateStationStop(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "STATION ENTER"

    def line_mode(self):
        return LineMode.KEEP_RIGHT


class AGVStateStationExit(AGVState):
    def __init__(self, datastore):
        super(AGVStateStationExit, self).__init__(datastore)

    def update(self, tags, line):
        station = self.datastore['station']
        if station != -1 and any(tag[0] == AGVSigns.make_id(AGVSigns.TYPE_STATION_EXIT, station) for tag in tags):
            return AGVStateFollow(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "STATION EXIT"

    def line_mode(self):
        return LineMode.KEEP_LEFT


TIME_TO_WAIT = 5

class AGVStateStationStop(AGVState):
    def __init__(self, datastore):
        super(AGVStateStationStop, self).__init__(datastore)
        self.t = time.time()
        passengers = datastore['passengers']
        old = passengers
        drop = datastore['drop']
        if drop < 0:#pick up
            passengers -= drop
            drop = 0
        else: #drop off
            amount = min(passengers, drop)
            passengers -= amount
            drop -= amount

        datastore['passengers'] = passengers
        datastore['drop'] = drop
        print("Dropped off %d of %d passengers" % (old - passengers, old))

    def update(self, tags, line):
        if time.time() - self.t > TIME_TO_WAIT:
            return AGVStateStationExit(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "STATION STOP"

    def line_mode(self):
        return LineMode.DISABLE



