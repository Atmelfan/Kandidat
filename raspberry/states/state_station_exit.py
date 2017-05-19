from agv_linefollow import LineMode
from agv_signs import AGVSigns
from states.state_follow import AGVStateFollow
from states.agv_state import AGVState


class AGVStateStationExit(AGVState):
    def __init__(self, datastore):
        super(AGVStateStationExit, self).__init__(datastore)

    def update(self, tags, line):
        station = self.datastore['drop'][0]

        if station != -1 and any(tag[0] == AGVSigns.make_id(AGVSigns.TYPE_STATION_EXIT, station) for tag in tags):
            print("Found my stop!")
            return AGVStateFollow(self.datastore)
        return super().update(tags, line)

    def get_name(self):
        return "STATION EXIT"

    def line_mode(self):
        return LineMode.KEEP_LEFT
