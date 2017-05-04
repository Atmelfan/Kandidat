from states.agv_state import AGVState


class AGVStateStop(AGVState):
    def __init__(self):
        super(AGVStateStop, self).__init__()

    def get_name(self):
        return "STOP"
