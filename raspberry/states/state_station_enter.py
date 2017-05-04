from states.agv_state import AGVState


class AGVStateStationEnter(AGVState):
    def __init__(self):
        super(AGVStateStationEnter, self).__init__()

    def get_name(self):
        return "STATION ENTER"
