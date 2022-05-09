import socket
import struct
import netifaces
import binascii


def main():
    print(netifaces.interfaces())

    interface_name = input("Enter network interface name: ")
    mac_address_local = netifaces.ifaddresses(interface_name)[netifaces.AF_PACKET][0]['addr']
    ip_address_local = netifaces.ifaddresses(interface_name)[netifaces.AF_INET][0]['addr']
    mac_address_remote = input("Enter remote MAC address: ")
    ip_address_remote = input("Enter remote IPv4 address: ")

    # mac_address_local_bytes = binascii.unhexlify(mac_address_local.replace(':', ''))
    # ip_address_local_bytes = socket.inet_pton(socket.AF_INET, ip_address_local)
    # mac_address_remote_bytes = binascii.unhexlify(mac_address_remote.replace(':', ''))
    # ip_address_remote_bytes = socket.inet_pton(socket.AF_INET, ip_address_remote)

    s = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))

    while True:
        packet = s.recvfrom(2048)

        ethernet_header = packet[0][0:14]

        eth_header = struct.unpack("!6s6s2s", ethernet_header)

        ipheader = packet[0][14:34]
        ip_header = struct.unpack("!12s4s4s", ipheader)

        if str(binascii.hexlify(eth_header[1], sep=":", bytes_per_sep=1), "utf-8") == str(mac_address_remote) and \
                str(binascii.hexlify(eth_header[0], sep=":", bytes_per_sep=1), "utf-8") == str(mac_address_local) and \
                socket.inet_ntoa(ip_header[2]) == ip_address_local and \
                socket.inet_ntoa(ip_header[1]) == ip_address_remote:
            print("Destination MAC: " + str(binascii.hexlify(eth_header[0], sep=":", bytes_per_sep=1), "utf-8") + " | Source MAC: " + str(binascii.hexlify(eth_header[1], sep=":", bytes_per_sep=1), "utf-8") + " | Type: " + str(binascii.hexlify(eth_header[2]), "utf-8"))
            print("Destination IP: " + socket.inet_ntoa(ip_header[2]) + " | Source IP: " + socket.inet_ntoa(ip_header[1]))
            print("Data: " + str(packet[0][34:], 'utf-8'))
            print("------------------------------------------------------------------------------------")


if __name__ == "__main__":
    main()
