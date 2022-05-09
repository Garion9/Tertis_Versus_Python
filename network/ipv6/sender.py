import socket
import netifaces
import binascii

from network.ipv6.util import standardize_ipv6_format


def main():
    print(netifaces.interfaces())

    interface_name = input("Enter network interface name: ")
    mac_address_local = netifaces.ifaddresses(interface_name)[netifaces.AF_PACKET][0]['addr']
    ip_address_local = netifaces.ifaddresses(interface_name)[netifaces.AF_INET6][0]['addr']
    ip_address_local = standardize_ipv6_format(ip_address_local)
    mac_address_remote = input("Enter remote MAC address: ")
    ip_address_remote = input("Enter remote IPv6 address: ")
    ip_address_remote = standardize_ipv6_format(ip_address_remote)

    mac_address_local_bytes = binascii.unhexlify(mac_address_local.replace(':', ''))
    ip_address_local_bytes = socket.inet_pton(socket.AF_INET6, ip_address_local)
    mac_address_remote_bytes = binascii.unhexlify(mac_address_remote.replace(':', ''))
    ip_address_remote_bytes = socket.inet_pton(socket.AF_INET6, ip_address_remote)

    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    s.bind((interface_name, 0))

    ethernet = mac_address_remote_bytes   # MAC Address Destination
    ethernet += mac_address_local_bytes  # MAC Address Source
    ethernet += b'\x86\xdd'                  # Protocol-Type: IPv6

    ip_header = b'\x60\x00\x00\x00'   # Version, Traffic Class, Flow Label
    ip_header += b'\x04\x00\x06\x40'  # Payload Length, Next Header, Hop Limit
    ip_header += ip_address_local_bytes  # Source Address
    ip_header += ip_address_remote_bytes  # Destination Address

    # payload = bytes("Hello there!", 'utf-8')
    while True:
        payload = bytes(input("Enter message: "), 'utf-8')

        packet = ethernet + ip_header + payload
        s.send(packet)


if __name__ == "__main__":
    main()
