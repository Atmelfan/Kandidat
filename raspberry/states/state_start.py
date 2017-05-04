from states.agv_state import AGVState


class AGVStateStart(AGVState):
    def __init__(self):
        super(AGVStateStart, self).__init__()

    def get_name(self):
        return "START"
