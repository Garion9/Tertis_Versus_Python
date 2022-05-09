import socket
import netifaces
import binascii


def main():
    print(netifaces.interfaces())

    interface_name = input("Enter network interface name: ")
    mac_address_local = netifaces.ifaddresses(interface_name)[netifaces.AF_PACKET][0]['addr']
    ip_address_local = netifaces.ifaddresses(interface_name)[netifaces.AF_INET][0]['addr']
    mac_address_remote = input("Enter remote MAC address: ")
    ip_address_remote = input("Enter remote IPv4 address: ")

    mac_address_local_bytes = binascii.unhexlify(mac_address_local.replace(':', ''))
    ip_address_local_bytes = socket.inet_pton(socket.AF_INET, ip_address_local)
    mac_address_remote_bytes = binascii.unhexlify(mac_address_remote.replace(':', ''))
    ip_address_remote_bytes = socket.inet_pton(socket.AF_INET, ip_address_remote)

    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    s.bind((interface_name, 0))

    ethernet = mac_address_remote_bytes  # MAC Address Destination
    ethernet += mac_address_local_bytes  # MAC Address Source
    ethernet += b'\x08\x00'  # Protocol-Type: IPv4

    # ipv4
    ip_header = b'\x45\x00\x00\x28'  # Version, IHL, Type of Service | Total Length
    ip_header += b'\xab\xcd\x00\x00'  # Identification | Flags, Fragment Offset
    ip_header += b'\x40\x06\x00\x00'  # TTL, Protocol | Header Checksum
    ip_header += ip_address_local_bytes  # Source Address
    ip_header += ip_address_remote_bytes  # Destination Address

    # payload = bytes("Hello there!", 'utf-8')
    while True:
        payload = bytes(input("Enter message: "), "utf-8")

        packet = ethernet + ip_header + payload
        s.send(packet)


if __name__ == "__main__":
    main()
