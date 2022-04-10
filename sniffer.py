import socket
import struct
import binascii

HOST = socket.gethostbyname(socket.gethostname())

s = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
# s.bind((HOST, 10000))
# s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
# s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

while True:
    packet = s.recvfrom(2048)

    ethernet_header = packet[0][0:14]

    eth_header = struct.unpack("!6s6s2s", ethernet_header)

    print("Destination MAC:" + str(binascii.hexlify(eth_header[0], sep=":", bytes_per_sep=1)) + "  | Source MAC:" + str(binascii.hexlify(eth_header[1], sep=":", bytes_per_sep=1)) + " Type:" + str(binascii.hexlify(eth_header[2])))

    ipheader = packet[0][14:34]
    ip_header = struct.unpack("!12s4s4s", ipheader)
    print("Destination IP:" + socket.inet_ntoa(ip_header[2]) + " \t\t  | Source IP:" + socket.inet_ntoa(ip_header[1]))
    print("------------------------------------------------------------------------------------")
