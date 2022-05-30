import socket

from network.ipv6.util import standardize_ipv6_format


class SenderUdp:
    """
    A class implementing a high level sender of UDP datagrams over IPv6.

    Attributes:
        ip_address_remote (str): remote IPv6 address, that messages will be sent to
        port (int):  remote UDP port number, that messages will be sent to
        net_socket (socket): websocket, responsible for sending UDP datagrams over IPv6
    """
    def __init__(self, ip_address_remote):
        """
        Standard constructor.

        Parameters:
            ip_address_remote (str): remote IPv6 address to send messages to; format: fe80::0123:4567:89ab:cdef
        """
        self.ip_address_remote = standardize_ipv6_format(ip_address_remote)
        self.port = 50001
        self.net_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)  # IPv6, UDP

    def send(self, data):
        """
        Reads messages from user input in a loop and sends them.
        """
        data = bytes(data, 'utf-8')
        self.net_socket.sendto(data, (self.ip_address_remote, self.port))


def main():
    """
    Very simple and minimalistic main function to showcase functionality of SenderUdp class.
    """
    ip_address_remote = input("Enter remote IPv6 address: ")

    sender = SenderUdp(ip_address_remote)

    while True:
        data = input("Enter message: ")
        sender.send(data)


if __name__ == '__main__':
    main()
