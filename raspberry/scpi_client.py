import serial


class ScpiClient(object):

    def __init__(self, stream, baudrate=115200, timeout=0.5):
        if isinstance(stream, str):
            self.stream = serial.Serial(stream, baudrate, timeout=timeout)
        else:
            self.stream = stream

        if not self.stream.is_open:
            raise ConnectionError("[SCPI] Failed to connect!")
        id = self.idn()
        if not id:
            raise ConnectionError("[SCPI] Failed to query *IDN!")
        print("[SCPI] Connected to %s!" % id)

    def send(self, cmd, n=1):
        self.stream.write(cmd + b"\r\n")
        self.stream.flush()

        results=[]
        for i in range(0, n):
            results.append(self.stream.readline())
        if n==1:
            return results
        return tuple(results)


    def idn(self):
        return self.send(b"*IDN?")[0]

    def rst(self):
        return self.send(b"*RST")[0]

    def __getitem__(self, item):
        return self.send(item, 1 + item.count(b";"))

    def __setitem__(self, key, value):
        if isinstance(key, bytes) and isinstance(value, bytes):
            return self.send(key + b" " + value)
        raise KeyError("Both key and value must be bytes")
