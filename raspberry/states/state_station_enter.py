import time

from agv_linefollow import LineMode
from agv_signs import AGVSigns
from states.state_station_stop import AGVStateStationStop
from states.agv_state import AGVState


class AGVStateStationEnter(AGVState):
    def __init__(self, datastore):
        super(AGVStateStationEnter, self).__init__(datastore)

    def update(self, tags, line):
        if any(tag[4] == AGVSigns.make_id(AGVSigns.TYPE_STATION_STOP, self.datastore['station']) for tag in tags):
            return AGVStateStationStop(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "STATION ENTER"

    def line_mode(self):
        return LineMode.KEEP_RIGHT


