import socket

class ReceiverUdp:
    def __init__(self, handler):
        self.port = 50001
        self.handler = handler
        self.net_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)  # IPv6, UDP

    def receive(self):
        self.net_socket.bind(('', self.port))
        while True:
            data, address = self.net_socket.recvfrom(1024)
            self.handler(data, address)


def main():
    def detailed_printer(data, address):
        print("Source address: " + address[0] + " | Source port: " + str(address[1]))
        print("Message: " + str(data, 'utf-8'))
        print("------------------------------------------------------------------------------------")

    def simple_printer(data, address):
        print("Message: " + str(data, 'utf-8'))

    receiver = ReceiverUdp(detailed_printer)

    receiver.receive()


if __name__ == '__main__':
    main()
