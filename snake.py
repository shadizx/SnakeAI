import pygame as pygame
import sys
import random

vec2 = pygame.math.Vector2

class Snake:
    def __init__(self, game):
        self.game = game
        self.grid_list = game.grid_list
        self.size = game.TILE_SIZE
        # starting rectangle of head of snake
        self.rect = pygame.rect.Rect([0, 0, game.TILE_SIZE - 2, game.TILE_SIZE - 2])

        # select random x and y for starting head of snake
        self.rect.x, self.rect.y = [602, 202]
        self.direction = vec2(self.size, 0)

        self.step_delay = 100  # milliseconds
        self.time = 0
        self.length = 1
        # keep segments of snake in a list
        self.segments = []
        # using this dictionary so later when we move, we can check which directions we are able to go in
        self.directions = {pygame.K_UP: 1, pygame.K_DOWN: 1, pygame.K_LEFT: 1, pygame.K_RIGHT: 1}

    # take in user input to move the snake
    def control(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.directions[pygame.K_UP]:
                self.direction = vec2(0, -self.size)
                # if you are going up, then you can only go up, left, or right
                self.directions = {pygame.K_UP: 1, pygame.K_DOWN: 0, pygame.K_LEFT: 1, pygame.K_RIGHT: 1}

            if event.key == pygame.K_DOWN and self.directions[pygame.K_DOWN]:
                self.direction = vec2(0, self.size)
                self.directions = {pygame.K_UP: 0, pygame.K_DOWN: 1, pygame.K_LEFT: 1, pygame.K_RIGHT: 1}

            if event.key == pygame.K_LEFT and self.directions[pygame.K_LEFT]:
                self.direction = vec2(-self.size, 0)
                self.directions = {pygame.K_UP: 1, pygame.K_DOWN: 1, pygame.K_LEFT: 1, pygame.K_RIGHT: 0}

            if event.key == pygame.K_RIGHT and self.directions[pygame.K_RIGHT]:
                self.direction = vec2(self.size, 0)
                self.directions = {pygame.K_UP: 1, pygame.K_DOWN: 1, pygame.K_LEFT: 0, pygame.K_RIGHT: 1}

    # controls speed of game
    def delta_time(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.time > self.step_delay:
            self.time = time_now
            return True
        return False

    # gets random position for the snake
    def place(self):
        x, y =  random.choice(self.game.grid_list)
        return [x + 2, y + 2]

    # check if snake hits border of wall
    def check_borders(self):
        if self.rect.left < self.game.OFFSET or self.rect.right > self.game.WIDTH:
            self.game.new_game()
        if self.rect.top < 0 or self.rect.bottom > self.game.HEIGHT:
            self.game.new_game()

    # check if snake ate the food
    def check_food(self):
        if (self.rect.x, self.rect.y) == (self.game.food.rect.x, self.game.food.rect.y):
            self.game.food.rect.x, self.game.food.rect.y= self.game.food.place(self)
            self.length += 1

    # check if the snake ate itself
    def check_selfeating(self):
        if len(self.segments) != len(set(segment.center for segment in self.segments)):
            self.game.new_game()

    # mvove the snake
    def move(self):
        if self.delta_time():
            self.rect.move_ip(self.direction)
            self.segments.append(self.rect.copy())
            self.segments = self.segments[-self.length:]

    # update screen
    def update(self):
        self.check_selfeating()
        self.check_borders()
        self.check_food()
        self.move()

    # draw the snake
    def draw(self):
        [pygame.draw.rect(self.game.win, 'green', segment) for segment in self.segments]


class Food:
    def __init__(self, game, snake):
        self.game = game
        self.size = game.TILE_SIZE
        self.rect = pygame.rect.Rect([0, 0, game.TILE_SIZE - 2, game.TILE_SIZE - 2])
        self.rect.x, self.rect.y = self.place(snake)

    def draw(self):
        pygame.draw.rect(self.game.win, 'red', self.rect)

    # function place that places the apple in a random position
    # apple needs to be placed not inside of the snake
    # returns list: [x, y] coordinates for new food position
    def place(self, snake):
        # add snake body to set to know where not to place apple
        snake_set = {(rect.x, rect.y) for rect in snake.segments}
        print(snake_set)
        # keep choosing random choice for apple until not in snake body
        x, y = random.choice(self.game.grid_list)
        while (x + 2, y + 2) in snake_set:
            x, y = random.choice(self.game.grid_list)
        return [x + 2, y + 2]
# class Game
# handles pygame environment
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("SnakeAI")
        self.HEIGHT = 800
        self.WIDTH = 1200
        self.OFFSET = self.WIDTH - self.HEIGHT
        self.TILE_SIZE = 40
        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        self.clock = pygame.time.Clock()
        self.grid_list = [[x, y] for x in range(self.OFFSET, self.WIDTH, self.TILE_SIZE)
                            for y in range(0, self.HEIGHT, self.TILE_SIZE)]
        print(self.grid_list)
        self.new_game()
        self.score = 0

    def new_game(self):
        self.snake = Snake(self)
        self.food = Food(self, self.snake)

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
        score_text = score_font.render(f"Score: {self.snake.length}", True, (255, 255, 255))
        self.win.blit(score_text, [80, 160])

    def update(self):
        self.snake.update()
        pygame.display.flip()
        self.clock.tick(160)

    def draw(self):
        self.win.fill('black')
        self.draw_name()
        self.draw_grid()
        self.draw_score()
        self.food.draw()
        self.snake.draw()

    def check_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # snake control
            self.snake.control(event)

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()