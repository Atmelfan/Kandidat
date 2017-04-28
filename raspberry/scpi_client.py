import serial


class ScpiClient(object):
    stream = None

    def __init__(self, stream, baudrate=9600, timeout=0.5):
        if isinstance(stream, str):
            self.stream = serial.Serial(stream, baudrate, timeout=timeout)
        else:
            self.stream = stream
        if not stream.is_open():
            yield ConnectionError("Failed to connect!")

    def send(self, cmd, n=1):
        self.stream.write(cmd + b"\r\n")
        results=[]
        for i in range(1, n):
            results.append(self.stream.readline())
        return tuple(results)


    def idn(self):
        return self.send(b"*IDN?")[0]

    def rst(self):
        return self.send(b"*RST")[0]

    def __getitem__(self, item):
        if isinstance(item, bytes):
            return self.send(item, 1 + item.count(b";"))
        elif isinstance(item, tuple) and all(isinstance(i, bytes) for i in item):
            return (self.send(item[i], 1 + item[i].count(b";")) for i in item)
        else:
            yield KeyError("Must be bytes or tuple of bytes")

    def __setitem__(self, key, value):
        if isinstance(key, bytes) and isinstance(value, bytes):
            return self.send(key + b" " + value)
        yield KeyError("Both key and value must be bytes")
