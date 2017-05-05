from agv_linefollow import LineMode
from states.agv_state import AGVState
from states.state_follow import AGVStateFollow



class AGVStateStart(AGVState):
    def __init__(self):
        super(AGVStateStart, self).__init__()

    def update(self, tags, line):
        if any(line):
            return AGVStateFollow()
        return super().update(tags, line)

    def get_name(self):
        return "START"

    def line_mode(self):
        return LineMode.KEEP_STRAIGHT





