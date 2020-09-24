import copy
import random
import time

import pygame

pygame.init()
pygame.font.init()
pygame.display.set_caption('Parsel Tongue')

MARGIN = 60
WINDOW_SIZE = (600, 600 + MARGIN)

RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 100)
WHITE = (255, 255, 255)

SNAKE_SIZE = 15
SNAKE_SPEED = 1

FONT_SIZE = 30

if WINDOW_SIZE[0] % SNAKE_SIZE != 0 or WINDOW_SIZE[1] % SNAKE_SIZE != 0 or MARGIN % SNAKE_SIZE != 0:
    raise Exception('Size of grid should be divisible by SNAKE_SIZE')


class Food:
    foods = []

    def __init__(self):
        self.add_to_list()
        self.coords = None
        self.count = 0
        self.create_food()

    def add_to_list(self):
        self.foods.append(self)

    def remove_from_list(self):
        self.foods.remove(self)

    def create_food(self):
        self.count += 1
        check = set(tuple(part[0]) for snake in Snake.snakes for part in snake.body)
        self.coords = random.choice([(i, j) for i in range(0, WINDOW_SIZE[0], SNAKE_SIZE)
                                     for j in range(MARGIN, WINDOW_SIZE[1], SNAKE_SIZE) if (i, j) not in check])

    def display(self, canvas):
        pygame.draw.rect(canvas, RED, (self.coords[0] + 1, self.coords[1] + 1, SNAKE_SIZE - 2, SNAKE_SIZE - 2))


class Snake:
    snakes = []

    def __init__(self, initial_body):
        self.add_to_list()
        self.body = initial_body.copy()
        self.lock_last = False
        self.last_key_function = self.prev_key_function = -1

    def add_to_list(self):
        self.snakes.append(self)

    def remove_from_list(self):
        self.snakes.remove(self)

    def update_key_function(self, keys):
        for key in keys:
            if key in (pygame.K_w, pygame.K_UP):
                self.last_key_function = 0

            if key in (pygame.K_s, pygame.K_DOWN):
                self.last_key_function = 2

            if key in (pygame.K_a, pygame.K_LEFT):
                self.last_key_function = 1

            if key in (pygame.K_d, pygame.K_RIGHT):
                self.last_key_function = 3

    def update(self):
        copy.deepcopy(self.body)

        if self.head_in_block():
            self.lock_last = False

            if self.last_key_function == 0:
                if not self.move_up():
                    self.last_key_function = self.prev_key_function

            elif self.last_key_function == 1:
                if not self.move_left():
                    self.last_key_function = self.prev_key_function

            elif self.last_key_function == 2:
                if not self.move_down():
                    self.last_key_function = self.prev_key_function

            elif self.last_key_function == 3:
                if not self.move_right():
                    self.last_key_function = self.prev_key_function

            self.prev_key_function = self.last_key_function

            for food in Food.foods:
                if self.body[0][0] == food.coords:
                    self.add_part(food)

        self.move()

    def add_part(self, food):
        self.lock_last = True
        self.body.append(self.body[-1].copy())
        food.create_food()

    def move(self):
        if self.last_key_function != -1:
            for part_index, (part_coords, part_velocity) in \
                    enumerate(self.body if not self.lock_last else self.body[:-1]):
                new_part_coords = (part_coords[0] + part_velocity[0], part_coords[1] + part_velocity[1])
                self.body[part_index][0] = new_part_coords

            if self.head_in_block():
                for part_index in range(len(self.body) - 1 - int(self.lock_last), 0, -1):
                    for new_part_index in range(part_index - 1, -1, -1):
                        if self.body[new_part_index][0] != self.body[part_index][0]:
                            self.body[part_index][1] = self.body[new_part_index][1]
                            break

    def move_up(self):
        if len(self.body) <= 1 or self.body[0][0][1] <= self.body[1][0][1]:
            self.body[0][1] = (0, -SNAKE_SPEED)
            return True
        return False

    def move_left(self):
        if len(self.body) <= 1 or self.body[0][0][0] <= self.body[1][0][0]:
            self.body[0][1] = (-SNAKE_SPEED, 0)
            return True
        return False

    def move_down(self):
        if len(self.body) <= 1 or self.body[0][0][1] >= self.body[1][0][1]:
            self.body[0][1] = (0, SNAKE_SPEED)
            return True
        return False

    def move_right(self):
        if len(self.body) <= 1 or self.body[0][0][0] >= self.body[1][0][0]:
            self.body[0][1] = (SNAKE_SPEED, 0)
            return True
        return False

    def head_in_block(self):
        return self.coords_in_block(self.body[0][0])

    @staticmethod
    def coords_in_block(coords):
        return coords[0] % SNAKE_SIZE == coords[1] % SNAKE_SIZE == 0

    def display(self, canvas):
        for part_index, (part_coords, part_velocity) in enumerate(self.body):
            pygame.draw.rect(canvas, WHITE, (part_coords[0] + 1, part_coords[1] + 1, SNAKE_SIZE - 2, SNAKE_SIZE - 2))

            if part_index != 0:
                while True:
                    part_coords = (part_coords[0] + part_velocity[0], part_coords[1] + part_velocity[1])
                    pygame.draw.rect(canvas, WHITE,
                                     (part_coords[0] + 1, part_coords[1] + 1, SNAKE_SIZE - 2, SNAKE_SIZE - 2))

                    if self.coords_in_block(part_coords):
                        break

            if part_index != len(self.body) - 1:
                while True:
                    part_coords = (part_coords[0] - part_velocity[0], part_coords[1] - part_velocity[1])
                    pygame.draw.rect(canvas, WHITE,
                                     (part_coords[0] + 1, part_coords[1] + 1, SNAKE_SIZE - 2, SNAKE_SIZE - 2))

                    if self.coords_in_block(part_coords):
                        break

    def collided(self):
        if not (0 <= self.body[0][0][0] < WINDOW_SIZE[0] - SNAKE_SIZE + 1) or \
                not (MARGIN <= self.body[0][0][1] < WINDOW_SIZE[1] - SNAKE_SIZE + 1):
            return True

        if self.head_in_block():
            for part_index, (part_coords, part_velocity) in enumerate(self.body[1:], 1):
                if abs(self.body[0][0][0] - part_coords[0]) < SNAKE_SIZE and \
                        abs(self.body[0][0][1] - part_coords[1]) < SNAKE_SIZE:
                    return True

        else:
            return False


class Game:
    def __init__(self):
        clock = pygame.time.Clock()
        self.canvas = pygame.display.set_mode(WINDOW_SIZE)
        self.font = pygame.font.SysFont('Arial', FONT_SIZE)

        self.finished = False
        self.lost = self.paused = False
        self.lose_time = self.pause_time = None

        self.init_head = (WINDOW_SIZE[0] // 2 // 10 * 10, WINDOW_SIZE[1] // 2 // 10 * 10)
        self.init_body = [[self.init_head, (0, 0)]]

        self.snake = Snake(self.init_body)
        self.food = Food()

        while not self.finished:
            self.canvas.fill(BLACK)
            self.__update()

            clock.tick(180)

            pygame.draw.rect(self.canvas, WHITE, ((0, MARGIN - 1), (WINDOW_SIZE[0], 1)))
            pygame.display.update()

        self.__reset()

    def __reset(self):
        self.finished = False
        self.lost = self.paused = False
        self.lose_time = self.pause_time = None

        self.init_head = (WINDOW_SIZE[0] // 2 // 10 * 10, WINDOW_SIZE[1] // 2 // 10 * 10)
        self.init_body = [[self.init_head, (0, 0)]]

        self.snake.remove_from_list()
        self.food.remove_from_list()

        self.snake = Snake(self.init_body)
        self.food = Food()

    def __update(self):
        snake_update_keys = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.finished = True

            if event.type == pygame.KEYDOWN:
                if not self.lost and (event.key == pygame.K_p or event.key == pygame.K_ESCAPE):
                    self.paused = not self.paused
                    self.pause_time = time.time() if self.paused else None

                snake_update_keys.append(event.key)

                if self.lost and event.key == pygame.K_r:
                    self.__reset()

        if not self.lost and self.snake.collided():
            self.lost = True
            self.lose_time = time.time()

        if not self.lost and not self.paused:
            self.snake.update_key_function(snake_update_keys)
            self.snake.update()

        self.food.display(self.canvas)
        self.snake.display(self.canvas)

        self.__update_score()
        self.__update_pause()
        self.__update_fail()

    def __update_score(self):
        self.score = self.food.count - 1
        self.score_text = self.font.render('Score: ' + str(self.score), True, GREEN)
        self.canvas.blit(self.score_text, (10, 10))

    def __update_fail(self):
        if self.lost:
            fail_text = self.font.render('You lost!', True, GREEN)
            self.canvas.blit(fail_text, (WINDOW_SIZE[0] - 10 - fail_text.get_rect().width, 10))

            if (time.time() - self.lose_time) % 1 > 0.5:
                restart = self.font.render('Press R to restart', True, GREEN)
                self.canvas.blit(restart, (WINDOW_SIZE[0] // 2 - restart.get_rect().width // 2,
                                           WINDOW_SIZE[1] // 2 - restart.get_rect().height // 2))

    def __update_pause(self):
        if self.paused:
            if (time.time() - self.pause_time) % 1 > 0.5:
                self.pause_text = self.font.render('Press P or Esc to resume', True, GREEN)
                self.canvas.blit(self.pause_text, (WINDOW_SIZE[0] - 10 - self.pause_text.get_rect().width, 10))

        elif not self.lost:
            self.pause_text = self.font.render('Press P or Esc to pause', True, GREEN)
            self.canvas.blit(self.pause_text, (WINDOW_SIZE[0] - 10 - self.pause_text.get_rect().width, 10))


game = Game()
