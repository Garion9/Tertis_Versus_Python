import socket

port = 50001

s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)  # IPv6, UDP
s.bind(('', port))

while True:
    data, address = s.recvfrom(1024)
    print("Source address: " + address[0] + " | Source port: " + str(address[1]))
    print("Message: " + str(data, 'utf-8'))
    print("------------------------------------------------------------------------------------")

