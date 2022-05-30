import socket
import netifaces
import binascii

from network.ipv6.util import standardize_ipv6_format


class Receiver:
    """
    A class implementing a low level receiver of UDP datagrams over IPv6.

    Attributes:
        local_port (int): local UDP port number, on which to listen for messages
        interface_name (str): local network interface name
        mac_address_local (str): local MAC address
        ip_address_local (str): local IPv6 address
        mac_address_remote (str): remote MAC address
        ip_address_remote (str): remote IPv6 address
        handler (callable): function to handle received messages
        net_socket (socket): websocket (raw socket), responsible for receiving UDP datagrams over IPv6
    """
    def __init__(self, interface_name, mac_address_remote, ip_address_remote, handler):
        """
        Standard constructor.

        Parameters:
            interface_name (string): local network interface name, used to obtain information about local MAC and IP addresses
            mac_address_remote (string): remote MAC address; format: 01:23:45:67:89:AB
            ip_address_remote (string): remote IPv6 address; format: fe80::0123:4567:89ab:cdef
            handler (callable): function to handle received messages
        """
        self.local_port = 50001  # arbitrarily chosen port number, from among officially unused port numbers
        self.interface_name = interface_name
        self.mac_address_local = netifaces.ifaddresses(self.interface_name)[netifaces.AF_PACKET][0]['addr']  # local MAC address is being obtained from interface
        self.ip_address_local = netifaces.ifaddresses(self.interface_name)[netifaces.AF_INET6][0]['addr']  # local IPv6 address is being obtained from interface
        self.ip_address_local = standardize_ipv6_format(self.ip_address_local)
        self.mac_address_remote = mac_address_remote
        self.ip_address_remote = standardize_ipv6_format(ip_address_remote)
        self.handler = handler

        self.net_socket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))  # parameters specify that a raw socket is used

    def receive(self):
        """
        Most important method of the class. It looks through all network communication received on an interface and
        filters out messages coming from a remote host specified during initialization (through MAC and IPv6 addresses
        as well as UDP port number).
        Then it handles received messages using "handler" function.
        """
        while True:
            frame = self.net_socket.recvfrom(2048)[0]

            # received Ethernet packet is divided into parts to make filtering easier to understand
            ethernet_header = frame[0:14]
            ip_header = frame[14:54]
            udp_header = frame[54:62]

            frame_destination_mac = ethernet_header[0:6]
            frame_source_mac = ethernet_header[6:12]
            packet_destination_ip = ip_header[24:40]
            packet_source_ip = ip_header[8:24]
            datagram_destination_port = udp_header[2:4]

            # filtering of received traffic
            if str(binascii.hexlify(frame_destination_mac, sep=":", bytes_per_sep=1), "utf-8") == str(self.mac_address_local) and \
                    str(binascii.hexlify(frame_source_mac, sep=":", bytes_per_sep=1), "utf-8") == str(self.mac_address_remote) and \
                    standardize_ipv6_format(socket.inet_ntop(socket.AF_INET6, packet_destination_ip)) == self.ip_address_local and \
                    standardize_ipv6_format(socket.inet_ntop(socket.AF_INET6, packet_source_ip)) == self.ip_address_remote and \
                    int(str(binascii.hexlify(datagram_destination_port), "utf-8"), base=16) == self.local_port:

                self.handler(frame)


def main():
    """
    Very simple and minimalistic main function to showcase functionality of Receiver class.
    """
    interface_name = input("Enter network interface name: ")
    mac_address_remote = input("Enter remote MAC address: ")
    ip_address_remote = input("Enter remote IPv6 address: ")

    def sniffer(frame):
        """
        Handler function that prints detailed information about received packet.

        Parameters:
            frame (bytes): received ethernet frame in the form of a byte array
        """
        ethernet_header = frame[0:14]
        ip_header = frame[14:54]
        udp_header = frame[54:62]
        payload = frame[62:-4]

        frame_destination_mac = ethernet_header[0:6]
        frame_source_mac = ethernet_header[6:12]
        packet_destination_ip = ip_header[24:40]
        packet_source_ip = ip_header[8:24]
        datagram_destination_port = udp_header[2:4]

        message = "Destination MAC: " + str(binascii.hexlify(frame_destination_mac, sep=":", bytes_per_sep=1), "utf-8")
        message += " | Source MAC: " + str(binascii.hexlify(frame_source_mac, sep=":", bytes_per_sep=1), "utf-8")
        message += " | Type: " + str(binascii.hexlify(ethernet_header[12:14]), "utf-8") + "\n"
        message += "Destination IP: " + socket.inet_ntop(socket.AF_INET6, packet_destination_ip)
        message += " | Source IP: " + socket.inet_ntop(socket.AF_INET6, packet_source_ip) + "\n"
        message += "Data: " + str(payload, 'utf-8') + "\n"
        message += "------------------------------------------------------------------------------------"

        print(message)

    def payload_printer(frame):
        """
        Much simpler handler function that only prints UDP payload i.e. message.

        Parameters:
            frame (bytes): received ethernet frame in the form of a byte array
        """
        payload = str(frame[62:-4], 'utf-8')
        print(payload)

    receiver = Receiver(interface_name, mac_address_remote, ip_address_remote, sniffer)

    receiver.receive()


if __name__ == "__main__":
    main()
