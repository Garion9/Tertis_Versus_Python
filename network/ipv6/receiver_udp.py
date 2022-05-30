import socket


class ReceiverUdp:
    """
    A class implementing a high level receiver of UDP datagrams over IPv6.

    Attributes:
        port (int): local UDP port number, to listen for messages on
        handler (callable): function to handle received messages
        net_socket (socket): websocket, responsible for receiving UDP datagrams over IPv6
    """
    def __init__(self, handler):
        """
        Standard constructor.

        Parameters:
            handler (callable): function to handle received messages
        """
        self.port = 50001
        self.handler = handler
        self.net_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)  # parameters describe protocols to be used: IPv6, UDP

    def receive(self):
        """
        Receives messages in a loop and handles them (via handler).
        """
        self.net_socket.bind(('', self.port))
        while True:
            data, address = self.net_socket.recvfrom(1024)
            self.handler(data, address)


def main():
    """
    Very simple and minimalistic main function to showcase functionality of SenderUdp class.
    """
    def detailed_printer(data, address):
        """
        Simple handler function for showcase, prints address and port message was sent from as well as the message itself.

        Parameters:
            data (bytes): message's data
            address (address_tuple): address that message was sent from
        """
        print("Source address: " + address[0] + " | Source port: " + str(address[1]))
        print("Message: " + str(data, 'utf-8'))
        print("------------------------------------------------------------------------------------")

    def simple_printer(data, address):
        """
        Even simpler handler, prints only the message itself.

        Parameters:
            data (bytes): message's data
            address (address_tuple): address that message was sent from
        """
        print("Message: " + str(data, 'utf-8'))

    receiver = ReceiverUdp(detailed_printer)

    receiver.receive()


if __name__ == '__main__':
    main()
