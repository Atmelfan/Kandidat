from states.agv_state import AGVState


class AGVStateLead(AGVState):
    def __init__(self, datastore):
        super(AGVStateLead, self).__init__(datastore)

    def get_name(self):
        return "LEAD"
