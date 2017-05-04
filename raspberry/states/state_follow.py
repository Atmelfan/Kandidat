from states.agv_state import AGVState


class AGVStateFollow(AGVState):
    def __init__(self):
        super(AGVStateFollow, self).__init__()

    def get_name(self):
        return "FOLLOW"
