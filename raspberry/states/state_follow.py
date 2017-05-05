from agv_linefollow import LineMode
from states.state_station_enter import AGVStateStationEnter
from states.agv_state import AGVState


class AGVStateFollow(AGVState):
    def __init__(self):
        super(AGVStateFollow, self).__init__()

    def get_name(self):
        return "FOLLOW"

    def update(self, tags, line):
        if any(tag[4] == 0 for tag in tags):
            return AGVStateStationEnter()
        return super().update(tags, line)

    def line_mode(self):
        return LineMode.KEEP_RIGHT


