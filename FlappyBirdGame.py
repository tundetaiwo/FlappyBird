import pygame
import os
import random

pygame.font.init()
# Initialising dimensions of the game
WIN_WIDTH = 500
WIN_HEIGHT = 800
# Loading in different images of the bird that we alternate through to give 'flap' effect.
#Following function loads image and makes it 2x bigger.
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","background-black.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 # How much bird will tilt i.e. when bird moves up it will need to tilt up and vice versa for when it dives
    ROT_VEL = 20 #How much the bird will rotate on each frame
    ANIMATION_TIME = 5 #How long each bird animation is

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5 #needs to be negative as (0,0) is the top left of the image.
        self.tick_count = 0 # keeps track of the last jump
        self.height = self.y

    def move(self): ## figures out how much bird needs to move.
        self.tick_count += 1 #i.e. a frame went by, and allows us to keep track of how many frames went by since last jump.

        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d =  16
        if d < 0:
            d -= 2

        self.y = self.y + d

        if d <0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                    self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self,win):
        self.img_count += 1
        # Checking what image we should show based on current image count
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
        #Up till now the image is being rotated along top left we want to rotate along center
        rotated_image = pygame.transform.rotate(self.img,self. tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image,new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5 ## Bird doens't move everything else does.
    def __init__(self,x): #reason not using y is because height is random.
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #need a pipe that faces down.
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False # if bird is past pipe
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird): #uses masks to check whether pixels are actually colliding instead of boxes
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))  #how far corners are from each other.
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset) #if no collision returns None.
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False
#Creating a class for the top and bottom base images that need to be moving.
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win): #Drawing top and bottom onto window.
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMG,(0,0)) #drawing background to display
    for pipe in pipes:
        pipe.draw(win) #drawing pipe
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(win) #drawing base

    for bird in birds:
        bird.draw(win) #drawing bird
    pygame.display.update() #display update



