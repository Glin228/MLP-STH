import time

import pygame
from functools import lru_cache
import random
import phrases

pygame.font.init()

@lru_cache(maxsize=512)
def render(raw_image, angle, alpha, scale, rwidth, rheight):
    """
    All this is made so that stuff works faster better use C++
    """
    image = raw_image
    image = pygame.transform.smoothscale(image, (rwidth * scale, rheight * scale))
    image = pygame.transform.rotate(image, angle)
    image.set_alpha(alpha)
    return image

class Sprite:
    def __init__(self, image = None, scale = 1):
        if image:
            self.raw_image = pygame.image.load(image)
        else:
            self.raw_image = pygame.image.load("icon.png")
        self.rwidth,self.rheight = self.raw_image.get_size()
        self.scale = scale
        self.alpha = 255
        self.x = 0
        self.y = 0
        self.deg = 0
        self.children = []
        self.blit_children = True
    def set_pos(self, np):
        self.x,self.y=np
    def rotate(self, deg):
        self.deg = deg
    def blit(self, scr):
        image = render(self.raw_image, self.deg, self.alpha, self.scale, self.rwidth, self.rheight)
        scr.blit(image, (self.x-image.get_size()[0]/2, self.y-image.get_size()[1]/2))
        if self.children and self.blit_children:
            for s in self.children:
                s.blit(scr=scr)
    def check_out_of_bounds(self, gfx_mode):
        if self.x<0 or self.x>gfx_mode[0] or self.y<0 or self.y>gfx_mode[1]: return True
        return False
    def collides(self, other):
        #God please forgive me for what i am about to do
        return (other.x-other.rwidth*other.scale/2 < self.x-self.rwidth*self.scale/2 < other.x+other.rwidth*other.scale/2 or
            other.x-other.rwidth*other.scale/2 < self.x+self.rwidth*self.scale/2 < other.x+other.rwidth*other.scale/2
        ) and (other.y-other.rheight*other.scale/2 < self.y-self.rheight*self.scale/2 < other.y+other.rheight*other.scale/2 or
            other.y-other.rheight*other.scale/2 < self.y+self.rheight*self.scale/2 < other.y+other.rheight*other.scale/2
        )
    def set_image(self, new):
        self.raw_image = pygame.image.load(new)
        self.rwidth, self.rheight = self.raw_image.get_size()

class Label:
    def __init__(self, text, font = ("Helvetica", 20), color = (0, 0, 0)):
        self.text = text
        self.x = 0
        self.y = 0
        self._font = pygame.font.SysFont(font[0], font[1])
        self._color = color
        self.wraplength = 150
    def blit(self, scr):
        image = self._font.render(self.text, True, self._color, wraplength=self.wraplength)
        scr.blit(image, (self.x-image.get_size()[0]/2, self.y-image.get_size()[1]/2) )

class Enemy(Sprite):
    def __init__(self, *args):
        print(f"Initializing enemy with *args: {args}")
        super().__init__(*args)
        self.x = 1200
        self.y = 710
        self.health = 2
        self.children.append(Sprite("bubble.png", 0.85))
        self.children[0].alpha = 127
        self.children.append(Label(random.choice(phrases.phrases_enemy_normal)))
        self.speed = -10
        self.phrase_state = ("NORMAL", 0) #(STATE, time last bullet hit) STATE: "NORMAL", "PAIN"
    def update(self):
        self.x+=self.speed
        self.children[0].x = self.x
        self.children[0].y = self.y - self.rheight*self.scale
        self.children[1].x = self.x
        self.children[1].y = self.y - self.rheight*self.scale - 40
        if self.phrase_state[0] == "PAIN" and self.phrase_state[1] < time.time():
            self.change_phrases(newstate="NORMAL")
    def change_phrases(self, newstate = "PAIN"):
        if newstate == self.phrase_state[0]: return
        self.phrase_state = (newstate, time.time()+8)
        self.children[1] = Label(random.choice(eval(f"phrases.phrases_enemy_{self.phrase_state[0].lower()}")))

class BloodParticle:
    def __init__(self, parent: Sprite, x, y):
        self.parent = parent
        self.dx = parent.x - x
        self.dy = parent.y - y
        self.image = pygame.transform.scale(pygame.image.load("blood.png"), (10, 20))
        self.ADJUST_X = 10
        self.ADJUST_Y = -10
    def blit(self, scr):
        scr.blit(self.image, (self.parent.x-self.dx+self.ADJUST_X, self.parent.y-self.dy+self.ADJUST_Y))