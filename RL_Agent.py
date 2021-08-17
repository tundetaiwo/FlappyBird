import numpy as np
from collections import deque
from FlappyBirdGame import Pipe, Base, Bird, draw_window
import torch
import pygame
import random
from Model import Linear_QNet, QTrainer
from Helper import plot

pygame.font.init()
# Initialising dimensions of the game
WIN_WIDTH = 500
WIN_HEIGHT = 800

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # controls randomness
        self.gamma = 0.8  # discount rate between 0.8-0.9, has to be less than 1.
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(3, 5, 2)  # inputs are size of state, hidden, output
        self.trainer = QTrainer(self.model, lr=LR, gamma = self.gamma)


    def get_state(self, bird_y, pipe_height,pipe_bottom):
        s1 = bird_y  # height of bird
        s2 = abs(bird_y - pipe_height)  # distance from top
        s3 = abs(bird_y - pipe_bottom)  # distance from bottom
        return np.array([s1, s2, s3], dtype=float)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if max mem exceeded

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # Random moves: tradeoff between explorations/ exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0, 0]
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,1)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move = final_move[move] = 1  # predicted value should be a value between 0 and 1
        return final_move

def intialise_game():
    return Base(730), [Pipe(700)], Bird(230, 350), 0, 0  # two trailing zeros for score, done

def train():
    base, pipes, birds, score, done = intialise_game()
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # drawing flappy bird display based on dimensions set earlier
    clock = pygame.time.Clock() # defining pygame clock
    total_score = 0
    plot_scores = []
    plot_mean_scores = []
    record = 0
    agent = Agent()
    run = True

    while run:
        clock.tick(30)  # setting clock to be 30 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()



        pipe_ind = 0
        if len(pipes) > 1 and birds.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipes_ind = 1


        # aquire old state
        state_old = agent.get_state(birds.y, pipes[pipe_ind].height, pipes[pipe_ind].bottom)

        final_move = agent.get_action(state_old)
        #action
        if final_move > 0.5:
            birds.jump()
            action = 1
        else:
            action = 0
        # get new state
        state_new = agent.get_state(birds.y, pipes[pipe_ind].height, pipes[pipe_ind].bottom)

        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(birds):
                done = True
            if not pipe.passed and pipe.x < birds.x:
                pipe.passed = True
                add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:  # bird passing pipe
            score += 1
            reward = 5
            pipes.append(Pipe(700))

        for r in rem:
            pipes.remove(r)
        #  reward, done, score = game.play_step(final_move)
        if birds.y + birds.img.get_height() > 730 or birds.y < 0: # if bird hits the ground.
            reward = -1  # -1 rewards for hitting the ground.
            done = True

        # train short memory
        agent.train_short_memory(state_old, action, reward, state_new, done)

        #Remember
        agent.remember(state_old, action, reward, state_new, done)

        if done:  # train long memory also called replay memory, and also plot results.
            if score > record:
                record = score
                agent.model.save()

            print(f'Game: {agent.n_games}')
            print(f'Score that life: {record}')
            print(f'Current Record: {record}')

            # TODO: plot

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

            base, pipes, birds, score, done = intialise_game()
            agent.n_games += 1
            agent.train_long_memory()

        else:
            reward += 0.1





        # TODO: Need to think about how reards are going to work.

        base.move()
        draw_window(win, birds, pipes, base, score)
if __name__ == "__main__":
    train()


