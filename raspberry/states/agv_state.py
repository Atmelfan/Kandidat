from agv_linefollow import LineMode


class AGVState(object):
    def __init__(self):
        super(AGVState, self).__init__()

    def get_name(self):
        return "???"

    def start(self):
        pass

    def update(self):
        return None

    def stop(self):
        pass

    def override(self, next_state):
        pass

    def line_mode(self):
        return LineMode.DISABLE

class AGVStateFault(AGVState):
    def __init__(self, msg = "MissingNo?"):
        super(AGVState, self).__init__()

    def get_name(self):
        return "FAULT: %s"

