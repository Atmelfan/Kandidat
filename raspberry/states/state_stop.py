from states.state_start import AGVStateStart
from states.agv_state import AGVState


class AGVStateStop(AGVState):
    def __init__(self, datastore):
        super(AGVStateStop, self).__init__(datastore)

    def get_name(self):
        return "STOP"
