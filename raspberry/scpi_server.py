

class ScpiServer(object):
    def __init__(self, tree, idn = "SCPI_SERVER"):
        self.idn = idn

    @scpi_registerspecial("*IDN?")
    def idn(self):
        return self.idn



if __name__ == '__main__':
    pass