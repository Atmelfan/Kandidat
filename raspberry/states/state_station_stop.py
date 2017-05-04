from states.agv_state import AGVState


class AGVStateStationStop(AGVState):
    def __init__(self):
        super(AGVStateStationStop, self).__init__()

    def get_name(self):
        return "STATION STOP"
