import pygame

import socket
import struct
import netifaces
import binascii

from network.ipv6.util import standardize_ipv6_format

import threading


class ReceiverThread(threading.Thread):
    def __init__(self, interface_name, mac_address_remote, ip_address_remote, remote_positions):
        super().__init__()
        self.interface_name = interface_name
        self.mac_address_local = netifaces.ifaddresses(self.interface_name)[netifaces.AF_PACKET][0]['addr']
        self.ip_address_local = netifaces.ifaddresses(self.interface_name)[netifaces.AF_INET6][0]['addr']
        self.ip_address_local = standardize_ipv6_format(self.ip_address_local)
        self.mac_address_remote = mac_address_remote
        self.ip_address_remote = ip_address_remote
        self.ip_address_remote = standardize_ipv6_format(self.ip_address_remote)
        self.remote_positions = remote_positions

    def run(self):
        s = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        while True:
            packet = s.recvfrom(2048)
            ethernet_header = packet[0][0:14]
            eth_header = struct.unpack("!6s6s2s", ethernet_header)
            ipheader = packet[0][14:54]

            if str(binascii.hexlify(eth_header[0], sep=":", bytes_per_sep=1), "utf-8") == str(self.mac_address_local) and \
                    str(binascii.hexlify(eth_header[1], sep=":", bytes_per_sep=1), "utf-8") == str(
                self.mac_address_remote) and \
                    standardize_ipv6_format(socket.inet_ntop(socket.AF_INET6, ipheader[24:40])) == self.ip_address_local and \
                    standardize_ipv6_format(socket.inet_ntop(socket.AF_INET6, ipheader[8:24])) == self.ip_address_remote:

                updated_coordinates = str(packet[0][54:], 'utf-8').split(":")

                self.remote_positions["x"], self.remote_positions["y"] = int(updated_coordinates[1]), int(updated_coordinates[3])



    def get_positions(self):
        return self.remote_positions

def main():
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

    ethernet = mac_address_remote_bytes  # MAC Address Destination
    ethernet += mac_address_local_bytes  # MAC Address Source
    ethernet += b'\x86\xdd'  # Protocol-Type: IPv6

    ip_header = b'\x60\x00\x00\x00'  # Version, Traffic Class, Flow Label
    ip_header += b'\x04\x00\x06\x40'  # Payload Length, Next Header, Hop Limit
    ip_header += ip_address_local_bytes  # Source Address
    ip_header += ip_address_remote_bytes  # Destination Address

    # pygame starts here

    pygame.init()

    x_lower_bound = 0
    x_upper_bound = 400
    y_lower_bound = 0
    y_upper_bound = 600

    x_pos = 200
    y_pos = 200
    side_length = 40
    unit_of_movement = side_length
    x_pos_mod = 0
    y_pos_mod = 0

    remote_x_pos = 200
    remote_y_pos = 200
    remote_positions = {"x": remote_x_pos, "y": remote_y_pos}

    fps = 60
    time = 0

    screen = pygame.display.set_mode([2*x_upper_bound, y_upper_bound])
    pygame.display.set_caption("TERTIS Versus (WIP)")

    running = True

    clock = pygame.time.Clock()

    receiverThread = ReceiverThread(interface_name, mac_address_remote, ip_address_remote, remote_positions)
    receiverThread.start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    y_pos_mod -= unit_of_movement
                elif event.key == pygame.K_DOWN:
                    y_pos_mod += unit_of_movement
                elif event.key == pygame.K_LEFT:
                    x_pos_mod -= unit_of_movement
                elif event.key == pygame.K_RIGHT:
                    x_pos_mod += unit_of_movement
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    y_pos_mod += unit_of_movement
                    time = 251
                elif event.key == pygame.K_DOWN:
                    y_pos_mod -= unit_of_movement
                    time = 251
                elif event.key == pygame.K_LEFT:
                    x_pos_mod += unit_of_movement
                    time = 251
                elif event.key == pygame.K_RIGHT:
                    x_pos_mod -= unit_of_movement
                    time = 251

        screen.fill((255, 255, 255))

        if time > 200:
            if x_pos_mod != 0:
                x_pos += x_pos_mod
                x_pos = max(min(x_pos, x_upper_bound - side_length), x_lower_bound)
                time = 0
            if y_pos_mod != 0:
                y_pos += y_pos_mod
                y_pos = max(min(y_pos, y_upper_bound - side_length), y_lower_bound)
                time = 0

        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x_pos, y_pos, side_length, side_length))

        remote_positions = receiverThread.get_positions()

        pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(remote_positions.get("x") + x_upper_bound, remote_positions.get("y") + y_lower_bound, side_length, side_length))

        pygame.draw.line(screen, (0, 0, 0), (x_upper_bound, y_lower_bound), (x_upper_bound, y_upper_bound), 1)

        pygame.display.flip()

        payload = bytes("x:"+str(x_pos)+":y:"+str(y_pos), 'utf-8')
        packet = ethernet + ip_header + payload
        s.send(packet)

        time += clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
