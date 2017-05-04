from states.agv_state import AGVState


class AGVStateLead(AGVState):
    def __init__(self):
        super(AGVStateLead, self).__init__()

    def get_name(self):
        return "LEAD"
