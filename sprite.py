import time
import math
import pygame
from functools import lru_cache
import random

import phrases

pygame.font.init()

@lru_cache(1000)
def sin(angle_deg):
    return math.sin(math.radians(angle_deg))

@lru_cache(1000)
def cos(angle_deg):
    return math.cos(math.radians(angle_deg))

class Animation:
    def __init__(self, costumes: list[pygame.Surface] = [], interval = 1):
        self.t0 = time.time()
        self.interval = interval
        self.now = 0
        self.costumes = costumes
        self.working = True
    def start(self):
        self.t0 = time.time()
        return self.costumes[0]
    def get(self):
        dt = time.time() - self.t0
        if dt > self.interval and self.working:
            self.now+=1
            self.now = self.now%len(self.costumes)
            self.t0 = time.time()
        return self.costumes[self.now]

@lru_cache(maxsize=128)
def render(raw_image, angle, alpha, scale, rwidth, rheight):
    """
    All this is made so that stuff works faster better use C++
    """
    image = raw_image
    image = pygame.transform.scale(image, (rwidth * scale, rheight * scale))
    image = pygame.transform.rotate(image, angle)
    image.set_alpha(alpha)
    return image

class Sprite:
    def __init__(self, image = None, scale = 1):
        if image:
            if type(image) == str:
                self.raw_image = pygame.image.load(image)
                self.rwidth, self.rheight = self.raw_image.get_size()
            elif type(image) == Animation:
                self.raw_image = image
                self.rwidth, self.rheight = self.raw_image.start().get_size()
        else:
            self.raw_image = pygame.image.load("icon.png")
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
        if type(self.raw_image) != Animation:
            image = render(self.raw_image, self.deg, self.alpha, self.scale, self.rwidth, self.rheight)
        else:
            r_img = self.raw_image.get()
            self.rwidth, self.rheight = r_img.get_size()
            image = render(r_img, self.deg, self.alpha, self.scale, self.rwidth, self.rheight)
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
    def pause_animation(self):
        if type(self.raw_image) != Animation:
            raise Exception(f"{self}'s raw image is not a Animation!")
        self.raw_image.working = False
    def unpause_animation(self):
        if type(self.raw_image) != Animation:
            raise Exception(f"{self}'s raw image is not a Animation!")
        self.raw_image.working = True

class Label:
    def __init__(self, text, font = ("Helvetica", 20), color = (0, 0, 0)):
        self.text = text
        self.x = 0
        self.y = 0
        self._font = pygame.font.SysFont(font[0], font[1])
        self._color = color
        self.wraplength = 150
        self.bgcolor = None
    def blit(self, scr):
        image = self._font.render(self.text, True, self._color, wraplength=self.wraplength, bgcolor=self.bgcolor)
        scr.blit(image, (self.x-image.get_size()[0]/2, self.y-image.get_size()[1]/2) )

class CustomFontLabel:
    def __init__(self, text, font: tuple, color = (0, 0, 0)):
        self.text = text
        self.x = 0
        self.y = 0
        self._font = pygame.font.Font(font[0], size=font[1])
        self._color = color
        self.wraplength = 150
        self.bgcolor = None
    def blit(self, scr):
        image = self._font.render(self.text, True, self._color, wraplength=self.wraplength, bgcolor=self.bgcolor)
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

class ParticleManager:
    def __init__(self):
        self.blood_particles = []
        self.explosion_particles = []
        self.gore_particles = []
        self.blood_images = [pygame.transform.scale(pygame.image.load(f"blood/{i}.png"), (100, 100)) for i in range(1, 30)]
        self.explosion_images = [pygame.transform.scale(pygame.image.load(f"explosion/{i}.gif"), (100, 100)) for i in range(0, 17)]
        #Gore images for stuff flying up and left
        self.gore_images_135 = [pygame.transform.scale(pygame.image.load(f"gore/gore-{i}.png"), (100, 100)) for i in range(1, 4)]
        # Gore images for stuff flying up and right
        self.gore_images_45 = [pygame.transform.rotate(i, -90) for i in self.gore_images_135]
        # Gore images for stuff flying down and right
        self.gore_images_315 = [pygame.transform.rotate(i, -180) for i in self.gore_images_135]
        # Gore images for stuff flying down and left
        self.gore_images_225 = [pygame.transform.rotate(i, -270) for i in self.gore_images_135]
    def create_gore(self, x0, y0, amount = 4, velocity = 40):
        for i in range(amount):
            angle = random.choice([45, 135, 225, 315])
            self.gore_particles.append({
                "angle": angle,
                "image": random.choice(eval(f"self.gore_images_{angle}")),
                "x": x0,
                "y": y0,
                "velocity": velocity,
                "exists": 0
            })
    def create_blood(self, x, y, parentXV=0):
        self.blood_particles.append( [x, y, 0, parentXV] )
    def create_explosion(self, x, y):
        self.explosion_particles.append([x, y, 0])
    def blit(self, scr):
        for p in self.blood_particles[:]:
            scr.blit(self.blood_images[p[2]], (p[0]-50, p[1]-50))
            p[2]+=1
            p[0]+=p[3]
            if p[2] == 29:
                self.blood_particles.remove(p)
        for p in self.explosion_particles[:]:
            scr.blit(self.explosion_images[p[2]], (p[0]-50, p[1]-50))
            p[2]+=1
            if p[2] == 16:
                self.explosion_particles.remove(p)
        for p in self.gore_particles:
            scr.blit(p["image"], (p["x"]-50, p["y"]-50))
            p["exists"]+=1
            p["image"].set_alpha(p["exists"]*16)
            match p["angle"]:
                case 45:
                    p["x"]+=p["velocity"]
                    p["y"]-=p["velocity"]
                case 135:
                    p["x"] -= p["velocity"]
                    p["y"] -= p["velocity"]
                case 225:
                    p["x"] -= p["velocity"]
                    p["y"] += p["velocity"]
                case 315:
                    p["x"] += p["velocity"]
                    p["y"] += p["velocity"]
        for p in self.gore_particles[:]:
            if p["exists"] == 16:
                self.gore_particles.remove(p)