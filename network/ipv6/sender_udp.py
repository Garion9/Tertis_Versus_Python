import socket

from network.ipv6.util import standardize_ipv6_format


class SenderUdp:
    def __init__(self, ip_address_remote):
        self.ip_address_remote = standardize_ipv6_format(ip_address_remote)
        self.port = 50001
        self.net_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)  # IPv6, UDP

    def send(self, data):
        data = bytes(data, 'utf-8')
        self.net_socket.sendto(data, (self.ip_address_remote, self.port))


def main():
    ip_address_remote = input("Enter remote IPv6 address: ")

    sender = SenderUdp(ip_address_remote)

    while True:
        data = input("Enter message: ")
        sender.send(data)


if __name__ == '__main__':
    main()
