


class AGVState(object):
    def __init__(self):
        super(AGVState, self).__init__()

    def get_name(self):
        return "???"

    def update(self):
        pass

    def override(self, next_state):
        pass

class AGVStateFault(AGVState):
    def __init__(self, msg = "MissingNo?"):
        super(AGVState, self).__init__()

    def get_name(self):
        return "FAULT: %s"

    def update(self):
        pass
