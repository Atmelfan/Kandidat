import time

from agv_linefollow import LineMode
from states.state_station_exit import AGVStateStationExit
from states.agv_state import AGVState


TIME_TO_WAIT = 5

class AGVStateStationStop(AGVState):
    def __init__(self, datastore):
        super(AGVStateStationStop, self).__init__(datastore)
        self.t = time.time()
        passengers = datastore['passengers']
        old = passengers
        drop = datastore['drop'][0]
        if abs(drop) <= passengers:
            passengers -= drop
        else:
            drop -= passengers
            passengers = 0
        datastore['passengers'] = passengers
        datastore['drop'][0] = drop
        print("Dropped off %d passengers" % (old - passengers))

    def update(self, tags, line):
        if time.time() - self.t > TIME_TO_WAIT:
            return AGVStateStationExit(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "STATION STOP"

    def line_mode(self):
        return LineMode.DISABLE
