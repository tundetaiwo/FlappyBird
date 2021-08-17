from FlappyBirdGame import Pipe, Base, Bird, draw_window
import neat
import time
import os
import pygame
pygame.font.init()
# Initialising dimensions of the game
WIN_WIDTH = 500
WIN_HEIGHT = 800

def fitness(genomes, config):
    nets = []  # keeping track of neural net for each bird
    ge = []  # Keeping track of genome
    # bird = Bird(230, 350) # Initialising bird class
    birds = []
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)  # setting nn for genome
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)


    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # drawing flappy bird display based on dimensions set earlier
    clock = pygame.time.Clock() # defining pygame clock
    score = 0
    run = True
    while run:
        clock.tick(30) # setting clock to be 30 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            print(len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width())
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipes_ind = 1
        else:
            run = False
            break

        for i, bird in enumerate(birds):
            bird.move()
            ge[i].fitness += 0.1  # for each tick bird stays alive gives 0.1 reward encourages bird to not fly above or into ground.
            #Ouputs is a list but in this case only has len 1
            output = nets[i].activate((bird.y,abs(bird.y - pipes[pipe_ind].height),abs(bird.y - pipes[pipe_ind].bottom))) # passing input to nn

            if output[0] > 0.5:
                bird.jump()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[i].fitness -= 1  # every time bird hits pipe take 1 off fitness score.
                    birds.pop(i)
                    nets.pop(i)
                    ge.pop(i)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe: # bird passing pipe
            score += 1

            for g in ge:
                g.fitness += 5 # fitness is essentially reward function.
            pipes.append(Pipe(700))

        for r in rem:
            pipes.remove(r)

        for i, bird in enumerate(birds):
            if bird.y + bird.img.get_height() > 730 or bird.y < 0: # if bird hits the ground.
                ge[i].fitness -= 1  # every time bird hits pipe take 1 off fitness score.
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)

        base.move()
        draw_window(win, birds, pipes, base, score)






def run(config_path):
    # Parameters are the sub-headings(encapsulated in []) used in config file.
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    winner = p.run(fitness,50)



if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config-flappybird.txt")
    run(config_path)