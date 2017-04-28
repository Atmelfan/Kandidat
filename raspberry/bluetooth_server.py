from threading import Thread

from bluetooth import *

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "00001101-0000-1000-8000-00805f9b34fb"

advertise_service( server_sock, "AGV-3",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ],
#                   protocols = [ OBEX_UUID ]
                   )

print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)

print(b"\n")

class BluetoothServer(Thread):
    port = 0
    uuid = ""
    name = ""

    def __init__(self, name, uuid = "00001101-0000-1000-8000-00805f9b34fb", port = PORT_ANY):
        Thread.__init__(self)
        self.name = name
        self.uuid = name

        self.setDaemon(True)
        self.start()

    def get_string(self, client):
        tmp = b""
        data = client.recv(1)
        while len(data) != 0:
            tmp = tmp + data
            if b"\n" == data:
                break

            # print(tmp)
            data = client.recv(1)
        return tmp

    def run(self):
        server_sock = BluetoothSocket(RFCOMM)
        server_sock.bind(("", self.port))
        server_sock.listen(1)

        self.port = server_sock.getsockname()[1]

        # uuid = "00001101-0000-1000-8000-00805f9b34fb"

        advertise_service(server_sock, self.name,
                          service_id=self.uuid,
                          service_classes=[self.uuid, SERIAL_PORT_CLASS],
                          profiles=[SERIAL_PORT_PROFILE],
                          #                   protocols = [ OBEX_UUID ]
                          )

        print("Started bluetooth server on channel %d with uuid=%s" % (self.port, self.uuid))
        self.setName("RFCOMM:%s:%d" % (uuid, port))
        try:
            while True:
                data = get_string(client_sock)
                if len(data) == 0: break
                print("received [%s]" % data)
                client_sock.send(b"OK\r\n")
        except:
            print("Unexpected error in %s!" % self.getName())


def get_string(client):
        tmp = b""
        data = client.recv(1)
        while len(data) != 0:
                tmp = tmp + data
                if b"\n" == data:
                        break

                #print(tmp)
                data = client.recv(1)
        return tmp



if __name__ == '__main__':
    server = BluetoothServer("AGV3")
    x = input("Press the any key...")