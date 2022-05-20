import socket
import netifaces
import binascii

from network.ipv6.util import standardize_ipv6_format


class Receiver:
    def __init__(self, interface_name, mac_address_remote, ip_address_remote, handler):
        self.local_port = 50001
        self.interface_name = interface_name
        self.mac_address_local = netifaces.ifaddresses(self.interface_name)[netifaces.AF_PACKET][0]['addr']
        self.ip_address_local = netifaces.ifaddresses(self.interface_name)[netifaces.AF_INET6][0]['addr']
        self.ip_address_local = standardize_ipv6_format(self.ip_address_local)
        self.mac_address_remote = mac_address_remote
        self.ip_address_remote = standardize_ipv6_format(ip_address_remote)
        self.handler = handler

        self.net_socket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))

    def receive(self):
        while True:
            packet = self.net_socket.recvfrom(2048)[0]

            ethernet_header = packet[0:14]
            ip_header = packet[14:54]
            udp_header = packet[54:62]

            if str(binascii.hexlify(ethernet_header[0:6], sep=":", bytes_per_sep=1), "utf-8") == str(self.mac_address_local) and \
                    str(binascii.hexlify(ethernet_header[6:12], sep=":", bytes_per_sep=1), "utf-8") == str(self.mac_address_remote) and \
                    standardize_ipv6_format(socket.inet_ntop(socket.AF_INET6, ip_header[24:40])) == self.ip_address_local and \
                    standardize_ipv6_format(socket.inet_ntop(socket.AF_INET6, ip_header[8:24])) == self.ip_address_remote and \
                    int(str(binascii.hexlify(udp_header[2:4]), "utf-8"), base=16) == self.local_port:

                self.handler(packet)


def main():
    interface_name = input("Enter network interface name: ")
    mac_address_remote = input("Enter remote MAC address: ")
    ip_address_remote = input("Enter remote IPv6 address: ")

    def sniffer(packet):
        ethernet_header = packet[0:14]
        ip_header = packet[14:54]
        udp_header = packet[54:62]

        message = "Destination MAC: " + str(binascii.hexlify(ethernet_header[0:6], sep=":", bytes_per_sep=1), "utf-8")
        message += " | Source MAC: " + str(binascii.hexlify(ethernet_header[6:12], sep=":", bytes_per_sep=1), "utf-8")
        message += " | Type: " + str(binascii.hexlify(ethernet_header[12:14]), "utf-8") + "\n"
        message += "Destination IP: " + socket.inet_ntop(socket.AF_INET6, ip_header[24:40])
        message += " | Source IP: " + socket.inet_ntop(socket.AF_INET6, ip_header[8:24]) + "\n"
        message += "Data: " + str(packet[62:-4], 'utf-8') + "\n"
        message += "------------------------------------------------------------------------------------"

        print(message)

    def payload_printer(packet):
        payload = str(packet[62:-4], 'utf-8')
        print(payload)

    receiver = Receiver(interface_name, mac_address_remote, ip_address_remote, sniffer)

    receiver.receive()


if __name__ == "__main__":
    main()
