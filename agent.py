import torch
import random
import numpy as np
from collections import deque
from SnakeAI import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

class Agent:

    def __init__(self):
        self.number_of_games = 0
        # parameter to control randomness
        self.epsilon = 0
        # discount rate
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        # model takes 11 states, one hidden layer, and 3 for output because 3 different numbers in action
        self.model = Linear_QNet(14, 256, 3)
        self.trainer = QTrainer(self.model, learning_rate= LEARNING_RATE, gamma=self.gamma)

    # storing 11 states
    '''
    danger straight, right, left
    current direction up, left, right, down
    food left, right, up, down
    '''
    def get_state(self, game):
        # grab head of snake
        head = game.snake[0]

        # check points around head
        point_l = Point(head.x - game.TILE_SIZE, head.y)
        point_r = Point(head.x + game.TILE_SIZE, head.y)
        point_u = Point(head.x, head.y - game.TILE_SIZE)
        point_d = Point(head.x, head.y + game.TILE_SIZE)

        # check which direction the snake is going in
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        # calculate far dangers
        far_danger_straight, far_danger_right, far_danger_left = game.calculate_far_dangers()

        # create list for 11 states to then return the 14 sized array

        state = [
            # Danger Straight
            (dir_l and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_r)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_l and game.is_collision(point_u)) or
            (dir_r and game.is_collision(point_d)) or
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)),

            # Danger left
            (dir_l and game.is_collision(point_d)) or
            (dir_r and game.is_collision(point_u)) or
            (dir_u and game.is_collision(point_l)) or
            (dir_d and game.is_collision(point_r)),

            # Far Dangers
            far_danger_straight, far_danger_right, far_danger_left,

            # Move Direction
            dir_l, dir_r, dir_u, dir_d,

            # Food location
            # food left:
            game.head.x > game.food.x,
            # food right:
            game.head.x < game.food.x,
            # food up
            game.head.y > game.food.y,
            # food down
            game.head.y < game.food.y
        ]

        # turn list to array since there are true or false inside, will be converted to int
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, state_new, game_over):
        self.memory.append((state, action, reward, state_new, game_over)) # popleft if more than max mem

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        # put all categories together
        states, actions, rewards, states_new, games_over = zip(*mini_sample)

        self.trainer.train_step(states, actions, rewards, states_new, games_over)

    def train_short_memory(self, state, action, reward, state_new, game_over):
        self.trainer.train_step(state, action, reward, state_new, game_over)

    def get_action(self, state):
        # do some random moves - tradeoff between exploration and exploitation
        # when model gets better, we will do less random moves

        # more games = smaller epsilon
        self.epsilon = 80 - self.number_of_games
        final_move = [0, 0, 0]

        # get random move
        # when epsilon gets smaller, less chance of going into this if statement
        # ex: starting with 80/200 chance then going to 10/200 chance
        # can even become become negative, then no random moves
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            # exploitation move
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0) # this can be floating point array: [5.0, 2.7, 0.3]

            move = torch.argmax(prediction).item() # take highest index in array
            final_move[move] = 1 # set highest index to 1, in this case would be [1, 0, 0]

        return final_move
def train():
    score_list = []
    mean_scores_list = []
    total_score = 0
    highscore = 0
    agent = Agent()
    game = SnakeGameAI()

    # training loop
    while True:
        # get old/current state
        state_old = agent.get_state(game)

        # get move based on current state
        action = agent.get_action(state_old)

        # make move and get new state
        reward, done, score = game.play_step(action)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, action, reward, state_new, done)

        # remember
        agent.remember(state_old, action, reward, state_new, done)

        if done:
            # train long memory/replay memory
            #       trains on all the previous moves played to improve
            game.reset()
            agent.number_of_games += 1
            agent.train_long_memory()

            if score > highscore:
                highscore = score
                agent.model.save()

            print(f'Game #{agent.number_of_games} Score: {score} Highscore: {highscore}')
            score_list.append(score)
            total_score += score
            mean_score = total_score / agent.number_of_games
            mean_scores_list.append(mean_score)
            plot(score_list, mean_scores_list)
if __name__ == '__main__':
    train()