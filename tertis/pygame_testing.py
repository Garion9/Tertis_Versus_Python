import pygame


def main():
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

    fps = 60
    time = 0

    screen = pygame.display.set_mode([2*x_upper_bound, y_upper_bound])
    pygame.display.set_caption("TERTIS Versus (WIP)")

    running = True

    clock = pygame.time.Clock()

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

        pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(x_pos + x_upper_bound, y_pos, side_length, side_length))

        pygame.draw.line(screen, (0, 0, 0), (x_upper_bound, y_lower_bound), (x_upper_bound, y_upper_bound), 1)

        pygame.display.flip()

        time += clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
