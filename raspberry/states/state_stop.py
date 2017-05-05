from states.state_start import AGVStateStart
from states.agv_state import AGVState


class AGVStateStop(AGVState):
    def __init__(self):
        super(AGVStateStop, self).__init__()

    def update(self, tags, line):

        return AGVStateStart()

    def get_name(self):
        return "STOP"
