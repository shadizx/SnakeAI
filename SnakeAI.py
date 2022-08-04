import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

class SnakeGameAI:

    def __init__(self, width=1200, height=800):
        self.WIDTH = width
        self.HEIGHT = height
        self.OFFSET = self.WIDTH - self.HEIGHT
        self.TILE_SIZE = 40
        self.grid_list = [[x, y] for x in range(self.OFFSET, self.WIDTH, self.TILE_SIZE)
                            for y in range(0, self.HEIGHT, self.TILE_SIZE)]

        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('SnakeAI')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(600, 200)
        self.snake = [self.head]

        self.score = 0
        self.food = None
        self.place_food()
        self.frame_iteration = 0

    def place_food(self):
        # add snake body to set to know where not to place apple
        snake_set = {(rect.x, rect.y) for rect in self.snake}
        # keep choosing random choice for apple until not in snake body
        x, y = random.choice(self.grid_list)
        while (x, y) in snake_set:
            x, y = random.choice(self.grid_list)
        self.food = Point(x, y)

    # input: action
    # output: reward, game_over, score
    def play_step(self, action):
        self.frame_iteration += 1

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self.move(action) # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self.place_food()
        else:
            self.snake.pop()

        # 5. update ui and clock
        self.update_ui()
        self.clock.tick(40)
        # 6. return game over and score
        return reward, game_over, self.score

    def is_collision(self, pt = None):
        if pt == None:
            pt = self.head
        # hits boundary
        if pt.x > self.WIDTH - self.TILE_SIZE or pt.x < self.OFFSET or \
           pt.y > self.HEIGHT - self.TILE_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False

    # function that calculates which direction is the 'safest' by checking each square in each direction
    # returns[straight, right, left] and 1 means the direction that is the safest
    # ex: [1, 0, 0] means that right and left have closer dangers and snake should go straight
    def calculate_far_dangers(self):
        snake_set = {(rect.x, rect.y) for rect in self.snake}
        head = self.snake[0]
        direction = self.direction

        if direction == Direction.LEFT:
            straight_start, straight_end, straight_inc = head.x - self.TILE_SIZE, self.OFFSET, -self.TILE_SIZE
            right_start, right_end, right_inc = head.y - self.TILE_SIZE, 0, -self.TILE_SIZE
            left_start, left_end, left_inc = head.y + self.TILE_SIZE, self.HEIGHT, self.TILE_SIZE
        elif direction == Direction.RIGHT:
            straight_start, straight_end, straight_inc = head.x + self.TILE_SIZE, self.WIDTH, self.TILE_SIZE
            right_start, right_end, right_inc = head.y + self.TILE_SIZE, self.HEIGHT, self.TILE_SIZE
            left_start, left_end, left_inc = head.y - self.TILE_SIZE, 0, -self.TILE_SIZE
        elif direction == Direction.UP:
            straight_start, straight_end, straight_inc = head.y - self.TILE_SIZE, 0, -self.TILE_SIZE
            right_start, right_end, right_inc = head.x + self.TILE_SIZE, self.WIDTH, self.TILE_SIZE
            left_start, left_end, left_inc = head.x - self.TILE_SIZE, self.OFFSET, -self.TILE_SIZE
        else:
            straight_start, straight_end, straight_inc = head.y + self.TILE_SIZE, self.HEIGHT, self.TILE_SIZE
            right_start, right_end, right_inc = head.x - self.TILE_SIZE, self.OFFSET, -self.TILE_SIZE
            left_start, left_end, left_inc = head.x + self.TILE_SIZE, self.WIDTH, self.TILE_SIZE

        # check straight
        straight_count = 1
        for straight in range(straight_start, straight_end, straight_inc):
            # if we found a collision (body of snake) break and save count
            if (straight, head.y) in snake_set:
                break
            straight_count += 1
        # check right
        right_count = 1
        for right in range(right_start, right_end, right_inc):
            if (head.x, right) in snake_set:
                break
            right_count += 1
        # check left
        left_count = 1
        for left in range(left_start, left_end, left_inc):
            if (head.x, left) in snake_set:
                break
            left_count += 1
        divisor = max(straight_count, right_count, left_count)

        return straight_count // divisor, right_count // divisor, left_count // divisor

    def draw_grid(self):
        for x in range(self.OFFSET, self.WIDTH, self.TILE_SIZE):
            pygame.draw.line(self.win, (50, 50, 50), (x, 0), (x, self.HEIGHT))
            pygame.draw.line(self.win, (50, 50, 50), (self.OFFSET, x - self.OFFSET), (self.WIDTH, x - self.OFFSET))
        # draw first red line
        pygame.draw.line(self.win, (255, 0, 0), (self.OFFSET, 0), (self.OFFSET, self.HEIGHT))

    def draw_name(self):
        name_font = pygame.font.Font('Snake Chan.otf', 80)
        name_text = name_font.render("Snake", True, (0, 255, 0))
        self.win.blit(name_text, [40, 50])

    def draw_score(self):
        score_font = pygame.font.Font('Azonix.otf', 45)
        score_text = score_font.render(f"Score: {len(self.snake) - 1}", True, (255, 255, 255))
        self.win.blit(score_text, [70, 160])

    def update_ui(self):
        self.win.fill('black')

        # draw UI
        self.draw_name()
        self.draw_score()

        # draw snake
        for pt in self.snake:
            pygame.draw.rect(self.win, 'green', pygame.Rect(pt.x, pt.y, self.TILE_SIZE, self.TILE_SIZE))

        # draw food
        pygame.draw.rect(self.win, 'red', pygame.Rect(self.food.x, self.food.y, self.TILE_SIZE, self.TILE_SIZE))
        self.draw_grid()

        pygame.display.flip()

    def move(self, action):
        # [straight, right, left]

        clockwise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clockwise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clockwise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clockwise[next_idx]
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clockwise[next_idx]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += self.TILE_SIZE
        elif self.direction == Direction.LEFT:
            x -= self.TILE_SIZE
        elif self.direction == Direction.DOWN:
            y += self.TILE_SIZE
        elif self.direction == Direction.UP:
            y -= self.TILE_SIZE

        self.head = Point(x, y)