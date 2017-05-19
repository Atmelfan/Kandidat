from threading import Thread

from bluetooth import *



class BluetoothServer(Thread):

    def __init__(self, name, scpi_server, uuid="00001101-0000-1000-8000-00805f9b34fb", port=PORT_ANY):
        Thread.__init__(self)
        self.name = name
        self.uuid = uuid
        self.socket = BluetoothSocket(RFCOMM)
        self.socket.bind(("", port))
        self.socket.listen(1)
        self.scpi_server = scpi_server
        #self.port = self.socket.port

        self.port = self.socket.getsockname()[1]

        # uuid = "00001101-0000-1000-8000-00805f9b34fb"

        advertise_service(self.socket, self.name,
                          service_id=self.uuid,
                          service_classes=[self.uuid, SERIAL_PORT_CLASS],
                          profiles=[SERIAL_PORT_PROFILE],
                          #                   protocols = [ OBEX_UUID ]
                          )

        print("[BLUETOOTH] Started bluetooth server on channel %d with uuid=%s" % (self.port, self.uuid))
        self.setName("RFCOMM:%d" % (self.port))
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
        while True:
            print("[BLUETOOTH] Waiting for client...")
            client_sock, client_info = self.socket.accept()
            print("[BLUETOOTH] Accepted connection from ", client_info)
            try:
                while True:
                    print("-----")
                    data = get_string(client_sock)
                    if len(data) == 0:
                        break

                    print(">> %s" % data)

                    s = data.decode()
                    returns = self.scpi_server.execute(s)
                    print("<< %s" % returns.encode())

                    client_sock.send(returns.encode())
            except Exception as e:
                print("[BLUETOOTH %s] Unexpected error: %s" % (self.getName(), e))
            finally:
                client_sock.close()
            self.scpi_server.execute("NAV:STOP")
            print("[BLUETOOTH] Disconnected.")


    def send_line(self, s):
        self.socket.send((s+"\r\n").encode())


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