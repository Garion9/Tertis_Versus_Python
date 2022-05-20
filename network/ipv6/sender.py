import socket
import netifaces
import binascii

from network.ipv6.util import standardize_ipv6_format, calculate_checksum


class Sender:
    def __init__(self, interface_name, mac_address_remote, ip_address_remote):
        self.__source_port = 50000
        self.__destination_port = 50001

        self.__interface_name = interface_name
        mac_address_local = netifaces.ifaddresses(self.__interface_name)[netifaces.AF_PACKET][0]['addr']
        ip_address_local = netifaces.ifaddresses(self.__interface_name)[netifaces.AF_INET6][0]['addr']
        ip_address_local = standardize_ipv6_format(ip_address_local)
        ip_address_remote = standardize_ipv6_format(ip_address_remote)

        self.__mac_address_local_bytes = binascii.unhexlify(mac_address_local.replace(':', ''))
        self.__ip_address_local_bytes = socket.inet_pton(socket.AF_INET6, ip_address_local)
        self.__mac_address_remote_bytes = binascii.unhexlify(mac_address_remote.replace(':', ''))
        self.__ip_address_remote_bytes = socket.inet_pton(socket.AF_INET6, ip_address_remote)

        self.__s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        self.__s.bind((self.__interface_name, 0))

    def create_packet(self, data):
        payload_length = len(data) + 8
        payload_length_hex = hex(payload_length).lstrip("0x").rstrip("L")
        payload_length_hex_padded = "0" * (4 - len(payload_length_hex)) + payload_length_hex
        payload_length_bytes = binascii.unhexlify(payload_length_hex_padded)

        source_port_hex = hex(self.__source_port).lstrip("0x").rstrip("L")
        source_port_bytes = binascii.unhexlify("0" * (4 - len(source_port_hex)) + source_port_hex)
        destination_port_hex = hex(self.__destination_port).lstrip("0x").rstrip("L")
        destination_port_bytes = binascii.unhexlify("0" * (4 - len(destination_port_hex)) + destination_port_hex)

        ip_pseudo_header = self.__ip_address_local_bytes
        ip_pseudo_header += self.__ip_address_remote_bytes
        ip_pseudo_header += binascii.unhexlify("0" * (32 - len(payload_length_hex)) + payload_length_hex)
        ip_pseudo_header += b'\x00\x00\x00\x11'
        ip_pseudo_header += source_port_bytes
        ip_pseudo_header += destination_port_bytes
        ip_pseudo_header += payload_length_bytes
        ip_pseudo_header += b'\x00\x00'
        ip_pseudo_header += data
        if len(data) % 2 != 0:
            ip_pseudo_header += b'\x00'

        checksum = calculate_checksum(ip_pseudo_header)

        udp = source_port_bytes  # Source port
        udp += destination_port_bytes  # Destination port
        udp += payload_length_bytes  # Length
        udp += checksum  # Checksum

        ip_header = b'\x60\x00\x00\x00'  # Version, Traffic Class, Flow Label
        ip_header += payload_length_bytes  # Payload Length
        ip_header += b'\x11\x40'  # Next Header, Hop Limit
        ip_header += self.__ip_address_local_bytes  # Source Address
        ip_header += self.__ip_address_remote_bytes  # Destination Address

        ethernet = self.__mac_address_remote_bytes  # MAC Address Destination
        ethernet += self.__mac_address_local_bytes  # MAC Address Source
        ethernet += b'\x86\xdd'  # Protocol-Type: IPv6

        crc = binascii.crc32(ethernet + ip_header + udp + data).to_bytes(4, 'little')

        return ethernet + ip_header + udp + data + crc

    def send(self, data):
        data = bytes(data, 'utf-8')
        packet = self.create_packet(data)
        self.__s.send(packet)


def main():
    print(netifaces.interfaces())
    interface_name = input("Enter network interface name: ")
    mac_address_remote = input("Enter remote MAC address: ")
    ip_address_remote = input("Enter remote IPv6 address: ")

    sender = Sender(interface_name, mac_address_remote, ip_address_remote)

    while True:
        data = input("Enter message: ")
        sender.send(data)


if __name__ == "__main__":
    main()
