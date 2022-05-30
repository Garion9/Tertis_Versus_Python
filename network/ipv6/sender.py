import socket
import netifaces
import binascii

from network.ipv6.util import standardize_ipv6_format, calculate_checksum


class Sender:
    """
    A class implementing a low level sender of UDP datagrams over IPv6.

    Attributes:
        source_port (int): local UDP port number
        destination_port (int): remote UDP port number
        interface_name (int): local network interface name
        mac_address_local_bytes (bytes): local MAC address in the form of a byte array
        ip_address_local_bytes (bytes): local IPv6 address in the form of a byte array
        mac_address_remote_bytes (bytes): remote MAC address in the form of a byte array
        ip_address_remote_bytes (bytes): remote IPv6 address in the form of a byte array
        net_socket (socket): websocket (raw socket), responsible for sending UDP datagrams over IPv6
    """
    def __init__(self, interface_name, mac_address_remote, ip_address_remote):
        """
        Standard constructor.

        Parameters:
            interface_name (str): local network interface name
            mac_address_remote (str): remote MAC address; format: 01:23:45:67:89:AB
            ip_address_remote (str): remote IPv6 address; format: fe80::0123:4567:89ab:cdef
        """
        self.source_port = 50000  # arbitrarily chosen port number, from among officially unused port numbers
        self.destination_port = 50001  # arbitrarily chosen port number, from among officially unused port numbers

        self.interface_name = interface_name
        mac_address_local = netifaces.ifaddresses(self.interface_name)[netifaces.AF_PACKET][0]['addr']  # local MAC address is being obtained from interface
        ip_address_local = netifaces.ifaddresses(self.interface_name)[netifaces.AF_INET6][0]['addr']  # local IPv6 address is being obtained from interface
        ip_address_local = standardize_ipv6_format(ip_address_local)
        ip_address_remote = standardize_ipv6_format(ip_address_remote)

        # string representations of IP and MAC addresses are converted to bytes
        self.mac_address_local_bytes = binascii.unhexlify(mac_address_local.replace(':', ''))
        self.ip_address_local_bytes = socket.inet_pton(socket.AF_INET6, ip_address_local)
        self.mac_address_remote_bytes = binascii.unhexlify(mac_address_remote.replace(':', ''))
        self.ip_address_remote_bytes = socket.inet_pton(socket.AF_INET6, ip_address_remote)

        self.net_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)  # parameters specify that a raw socket is used
        self.net_socket.bind((self.interface_name, 0))

    def create_packet(self, data):
        """
        Method for putting together the ethernet frame to be later sent.

        Parameters:
            data (bytes): message to be sent in the form of a byte array

        Returns:
            frame consisting of Ethernet header, IPv6 header, UDP header, payload (message) and control sum (FCS)
        """

        # payload of UDP payload is computed fo use in both the ip_pseudo_header as well as UDP and IPv6 headers later
        payload_length = len(data) + 8
        payload_length_hex = hex(payload_length).lstrip("0x").rstrip("L")
        payload_length_hex_padded = "0" * (4 - len(payload_length_hex)) + payload_length_hex
        payload_length_bytes = binascii.unhexlify(payload_length_hex_padded)

        # source and destination port numbers are first converted to hexadecimal values and then to byte array representation
        source_port_hex = hex(self.source_port).lstrip("0x").rstrip("L")
        source_port_bytes = binascii.unhexlify("0" * (4 - len(source_port_hex)) + source_port_hex)
        destination_port_hex = hex(self.destination_port).lstrip("0x").rstrip("L")
        destination_port_bytes = binascii.unhexlify("0" * (4 - len(destination_port_hex)) + destination_port_hex)

        # ip_pseudo_header is used solely to compute UDP header's control sum
        ip_pseudo_header = self.ip_address_local_bytes
        ip_pseudo_header += self.ip_address_remote_bytes
        ip_pseudo_header += binascii.unhexlify("0" * (32 - len(payload_length_hex)) + payload_length_hex)
        ip_pseudo_header += b'\x00\x00\x00\x11'
        ip_pseudo_header += source_port_bytes
        ip_pseudo_header += destination_port_bytes
        ip_pseudo_header += payload_length_bytes
        ip_pseudo_header += b'\x00\x00'
        ip_pseudo_header += data
        if len(data) % 2 != 0:
            ip_pseudo_header += b'\x00'

        # UDP checksum is calculated as 16-bit one's complement of the one's complement sum of
        # pseudo-header bytes (padded with zeroes at the end in order to make a multiple of two octets)
        checksum = calculate_checksum(ip_pseudo_header)

        # with the checksum calculated, the UDP header is assembled from following fields
        udp_header = source_port_bytes  # Source port number
        udp_header += destination_port_bytes  # Destination port number
        udp_header += payload_length_bytes  # Length (length of UDP header and UDP payload)
        udp_header += checksum  # Checksum

        # IPv6 header is assembled from following fields
        ip_header = b'\x60\x00\x00\x00'  # Version (version of IP protocol: 6), Traffic Class, Flow Label (this class sends more general packets that do not belong to any specific traffic class or any specific flow, thus both fields have a value of 0)
        ip_header += payload_length_bytes  # Payload Length (length of IP packet's payload, i.e. UDP datagram)
        ip_header += b'\x11\x40'  # Next Header (type of encapsulated header's protocol, i.e. UDP, for which value is 17 in decimal or 11 in hexadecimal), Hop Limit (equivalent of Time To Live field in IPv6, arbitrarily set to 64 which is recommended default value)
        ip_header += self.ip_address_local_bytes  # Source IPv6 Address
        ip_header += self.ip_address_remote_bytes  # Destination IPv6 Address

        # Ethernet header is assembled from following fields
        ethernet_header = self.mac_address_remote_bytes  # MAC Address Destination
        ethernet_header += self.mac_address_local_bytes  # MAC Address Source
        ethernet_header += b'\x86\xdd'  # Protocol-Type: IPv6

        # frame check sequence, calculated as 32-bit cyclic redundancy check (CRC)
        fcs = binascii.crc32(ethernet_header + ip_header + udp_header + data).to_bytes(4, 'little')

        # entire frame is put together and returned
        return ethernet_header + ip_header + udp_header + data + fcs

    def send(self, data):
        """
        Simple function to encode message as byte array and pass the formed frame to the socket in order for it to be sent.

        Parameters:
            data (str): UDP datagram payload (i.e. message) to be sent
        """
        data = bytes(data, 'utf-8')
        packet = self.create_packet(data)
        self.net_socket.send(packet)


def main():
    """
    Very simple and minimalistic main function to showcase functionality of Sender class.
    """
    interface_name = input("Enter network interface name: ")
    mac_address_remote = input("Enter remote MAC address: ")
    ip_address_remote = input("Enter remote IPv6 address: ")

    sender = Sender(interface_name, mac_address_remote, ip_address_remote)

    while True:
        data = input("Enter message: ")
        sender.send(data)


if __name__ == "__main__":
    main()
