import socket
import struct
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
            packet = self.net_socket.recvfrom(2048)

            ethernet_header = packet[0][0:14]

            eth_header = struct.unpack("!6s6s2s", ethernet_header)

            ipheader = packet[0][14:54]

            udpheader = packet[0][54:62]

            if str(binascii.hexlify(eth_header[0], sep=":", bytes_per_sep=1), "utf-8") == str(self.mac_address_local) and \
                str(binascii.hexlify(eth_header[1], sep=":", bytes_per_sep=1), "utf-8") == str(self.mac_address_remote) and \
                standardize_ipv6_format(socket.inet_ntop(socket.AF_INET6, ipheader[24:40])) == self.ip_address_local and \
                standardize_ipv6_format(socket.inet_ntop(socket.AF_INET6, ipheader[8:24])) == self.ip_address_remote and \
                int(str(binascii.hexlify(udpheader[2:4]), "utf-8"), base=16) == self.local_port:

                received_data = ""
                received_data += "Destination MAC: " + str(binascii.hexlify(eth_header[0], sep=":", bytes_per_sep=1), "utf-8") + " | Source MAC: " + str(binascii.hexlify(eth_header[1], sep=":", bytes_per_sep=1), "utf-8") + " | Type: " + str(binascii.hexlify(eth_header[2]), "utf-8")
                received_data += "\nDestination IP: " + socket.inet_ntop(socket.AF_INET6, ipheader[24:40]) + " | Source IP: " + socket.inet_ntop(socket.AF_INET6, ipheader[8:24])
                received_data += "\nData: " + str(packet[0][62:-4], 'utf-8')
                received_data += "\n------------------------------------------------------------------------------------"

                self.handler(received_data)

                # print("Destination MAC: " + str(binascii.hexlify(eth_header[0], sep=":", bytes_per_sep=1), "utf-8") + " | Source MAC: " + str(binascii.hexlify(eth_header[1], sep=":", bytes_per_sep=1), "utf-8") + " | Type: " + str(binascii.hexlify(eth_header[2]), "utf-8"))
                # print("Destination IP: " + socket.inet_ntop(socket.AF_INET6, ipheader[24:40]) + " | Source IP: " + socket.inet_ntop(socket.AF_INET6, ipheader[8:24]))
                # print("Data: " + str(packet[0][54:], 'utf-8'))
                # print("------------------------------------------------------------------------------------")

def main():
    print(netifaces.interfaces())

    interface_name = input("Enter network interface name: ")
    mac_address_local = netifaces.ifaddresses(interface_name)[netifaces.AF_PACKET][0]['addr']
    ip_address_local = netifaces.ifaddresses(interface_name)[netifaces.AF_INET6][0]['addr']
    ip_address_local = standardize_ipv6_format(ip_address_local)
    mac_address_remote = input("Enter remote MAC address: ")
    ip_address_remote = input("Enter remote IPv6 address: ")
    ip_address_remote = standardize_ipv6_format(ip_address_remote)

    # mac_address_local_bytes = binascii.unhexlify(mac_address_local.replace(':', ''))
    # ip_address_local_bytes = socket.inet_pton(socket.AF_INET6, ip_address_local)
    # mac_address_remote_bytes = binascii.unhexlify(mac_address_remote.replace(':', ''))
    # ip_address_remote_bytes = socket.inet_pton(socket.AF_INET6, ip_address_remote)

    s = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))

    while True:
        packet = s.recvfrom(2048)

        ethernet_header = packet[0][0:14]

        eth_header = struct.unpack("!6s6s2s", ethernet_header)

        ipheader = packet[0][14:54]

        if str(binascii.hexlify(eth_header[0], sep=":", bytes_per_sep=1), "utf-8") == str(mac_address_local) and \
                str(binascii.hexlify(eth_header[1], sep=":", bytes_per_sep=1), "utf-8") == str(mac_address_remote) and \
                standardize_ipv6_format(socket.inet_ntop(socket.AF_INET6, ipheader[24:40])) == ip_address_local and \
                standardize_ipv6_format(socket.inet_ntop(socket.AF_INET6, ipheader[8:24])) == ip_address_remote:
            print("Destination MAC: " + str(binascii.hexlify(eth_header[0], sep=":", bytes_per_sep=1), "utf-8") + " | Source MAC: " + str(binascii.hexlify(eth_header[1], sep=":", bytes_per_sep=1), "utf-8") + " | Type: " + str(binascii.hexlify(eth_header[2]), "utf-8"))
            print("Destination IP: " + socket.inet_ntop(socket.AF_INET6, ipheader[24:40]) + " | Source IP: " + socket.inet_ntop(socket.AF_INET6, ipheader[8:24]))
            print("Data: " + str(packet[0][54:], 'utf-8'))
            print("------------------------------------------------------------------------------------")

def main_2():
    interface_name = input("Enter network interface name: ")
    mac_address_remote = input("Enter remote MAC address: ")
    ip_address_remote = input("Enter remote IPv6 address: ")

    def printer(message):
        print(message)

    receiver = Receiver(interface_name, mac_address_remote, ip_address_remote, printer)

    receiver.receive()


if __name__ == "__main__":
    # main()
    main_2()

