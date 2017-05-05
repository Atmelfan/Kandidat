from agv_linefollow import LineMode


class AGVState(object):
    def __init__(self):
        super(AGVState, self).__init__()

    # get_name()
    # Returns the state name, e.g. "START" or "LEADING"
    def get_name(self):
        return "???"

    # start()
    # Called when the state is switched to
    #
    def start(self):
        print("State %s started!" % self.get_name())

    # update(aruco_tags, line_data)
    # Called during the control loop
    # Returns a new state to switch to or None to continue
    def update(self, tags, line):
        print("%s update: %s, %s" % (self.get_name(), tags, line))
        return None

    # on_command()
    #
    #
    def on_command(self, command):
        return None

    def stop(self):
        print("State %s stopped!" % self.get_name())

    def override(self, next_state):
        pass

    def line_mode(self):
        return LineMode.DISABLE

    def log(self):
        return "%s" % self.get_name()

class AGVStateFault(AGVState):
    def __init__(self, msg = "MissingNo?"):
        super(AGVState, self).__init__()

    def get_name(self):
        return "FAULT: %s"

