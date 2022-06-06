import pygame
import threading
import platform

from typing import Tuple, Union
from pygame.surface import Surface, SurfaceType

from network.ipv6.sender import Sender
from network.ipv6.sender_udp import SenderUdp
from network.ipv6.receiver import Receiver
from network.ipv6.receiver_udp import ReceiverUdp


class Colours:
    Red = (255, 0, 0)
    OrangeRed = (255, 69, 0)
    Green = (0, 255, 0)
    Blue = (0, 0, 255)
    LightBlue = (0, 191, 255)
    White = (255, 255, 255)
    Black = (0, 0, 0)


class GameBoard:
    def __init__(self, background_color: Tuple[int, int, int], border_color: Tuple[int, int, int]):
        self.x_lower_bound = 0
        self.x_upper_bound = 400
        self.y_lower_bound = 0
        self.y_upper_bound = 600
        self.block_side_length = 40
        self.unit_of_movement = 40
        self.starting_position_x = 200
        self.starting_position_y = 200
        self.fps = 60
        self.background_color = background_color
        self.border_color = border_color

    def draw(self, screen: Union[Surface, SurfaceType]):
        screen.fill(self.background_color)
        pygame.draw.line(screen, Colours.Black, (self.x_upper_bound, self.y_lower_bound), (self.x_upper_bound, self.y_upper_bound), 1)


class Player:
    class PlayerPosition:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y

    class PlayerSpeed:
        def __init__(self, horizontal: int, vertical: int):
            self.horizontal = horizontal
            self.vertical = vertical

    def __init__(self, starting_position_x: int, starting_position_y: int, color: Tuple[int, int, int], is_controlled: bool = True):
        self.position = self.PlayerPosition(starting_position_x, starting_position_y)
        self.speed = self.PlayerSpeed(0, 0) if is_controlled else None
        self.color = color

    def move(self, game_board: GameBoard):
        if self.speed.horizontal != 0:
            self.position.x += self.speed.horizontal
            self.position.x = max(min(self.position.x, game_board.x_upper_bound - game_board.block_side_length), game_board.x_lower_bound)
            return True
        if self.speed.vertical != 0:
            self.position.y += self.speed.vertical
            self.position.y = max(min(self.position.y, game_board.y_upper_bound - game_board.block_side_length), game_board.y_lower_bound)
            return True
        return False

    def draw(self, screen: Union[Surface, SurfaceType], game_board: GameBoard):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.position.x, self.position.y, game_board.block_side_length, game_board.block_side_length))


class ReceiverThread(threading.Thread):
    def __init__(self, interface_name: str, mac_address_remote: str, ip_address_remote: str, opponent_position: Player.PlayerPosition, game_board: GameBoard):
        super().__init__()

        self.opponent_position = opponent_position

        if platform.system() == "Linux":
            def update_opponent_positions(packet):
                payload = str(packet[62:-4], 'utf-8')
                position_updates = payload.split(":")
                self.opponent_position.x = int(position_updates[1]) + game_board.x_upper_bound
                self.opponent_position.y = int(position_updates[3])

            self.network_receiver = Receiver(interface_name, mac_address_remote, ip_address_remote, update_opponent_positions)
        elif platform.system() == "Windows":
            def update_opponent_positions(data, address):
                payload = str(data, 'utf-8')
                position_updates = payload.split(":")
                self.opponent_position.x = int(position_updates[1]) + game_board.x_upper_bound
                self.opponent_position.y = int(position_updates[3])

            self.network_receiver = ReceiverUdp(update_opponent_positions)

    def run(self):
        self.network_receiver.receive()


def main():
    interface_name = input("Enter network interface name: ")
    mac_address_remote = input("Enter remote MAC address: ")
    ip_address_remote = input("Enter remote IPv6 address: ")

    if platform.system() == "Linux":
        network_sender = Sender(interface_name, mac_address_remote, ip_address_remote)
    elif platform.system() == "Windows":
        network_sender = SenderUdp(ip_address_remote)

    pygame.init()

    game_board = GameBoard(Colours.White, Colours.Black)
    player = Player(game_board.starting_position_x, game_board.starting_position_y, Colours.LightBlue)
    opponent = Player(game_board.starting_position_x + game_board.x_upper_bound, game_board.starting_position_y, Colours.OrangeRed, is_controlled=False)

    screen = pygame.display.set_mode([2*game_board.x_upper_bound, game_board.y_upper_bound])
    pygame.display.set_caption("TERTIS Versus (WIP)")

    running = True

    time = 0
    clock = pygame.time.Clock()

    receiver_thread = ReceiverThread(interface_name, mac_address_remote, ip_address_remote, opponent.position, game_board)
    receiver_thread.start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    player.speed.vertical -= game_board.unit_of_movement
                elif event.key == pygame.K_DOWN:
                    player.speed.vertical += game_board.unit_of_movement
                elif event.key == pygame.K_LEFT:
                    player.speed.horizontal -= game_board.unit_of_movement
                elif event.key == pygame.K_RIGHT:
                    player.speed.horizontal += game_board.unit_of_movement
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    player.speed.vertical += game_board.unit_of_movement
                    time = 251
                elif event.key == pygame.K_DOWN:
                    player.speed.vertical -= game_board.unit_of_movement
                    time = 251
                elif event.key == pygame.K_LEFT:
                    player.speed.horizontal += game_board.unit_of_movement
                    time = 251
                elif event.key == pygame.K_RIGHT:
                    player.speed.horizontal -= game_board.unit_of_movement
                    time = 251

        game_board.draw(screen)

        if time > 200:
            if player.move(game_board):
                time = 0

        player.draw(screen, game_board)
        opponent.draw(screen, game_board)

        pygame.display.flip()

        message = "x:"+str(player.position.x)+":y:"+str(player.position.y)
        network_sender.send(message)

        time += clock.tick(game_board.fps)

    pygame.quit()


if __name__ == "__main__":
    main()
