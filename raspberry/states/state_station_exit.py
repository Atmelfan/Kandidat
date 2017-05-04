from states.agv_state import AGVState


class AGVStateStationExit(AGVState):
    def __init__(self):
        super(AGVStateStationExit, self).__init__()

    def get_name(self):
        return "STATION EXIT"
