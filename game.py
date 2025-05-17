from stem.util.lru_cache import lru_cache
import sprite
import pygame
import time
import math
from threading import Thread
import random
from sys import argv

DEATH_MSG = "They killed Twilight Sparkle. But do not give up! Don't let these bastards and perverts ruin your childhood. (Press Enter to exit)"

pygame.mixer.init()

enemies_spawned_total = 0

@lru_cache(1000)
def sin(angle_deg):
    return math.sin(math.radians(angle_deg))

@lru_cache(1000)
def cos(angle_deg):
    return math.cos(math.radians(angle_deg))

def spawn_enemies():
    global entities, running
    t0 = time.time()
    while running:
        x = random.randint(5, 20)
        if time.time()-t0>x:
            entities.append(Bojack())
            t0 = time.time()
        time.sleep(FPS)

def calculate_angle(sprite_pos, mouse_pos):
    dx = mouse_pos[0] - sprite_pos[0]
    dy = sprite_pos[1] - mouse_pos[1]
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    return angle_deg

class Bojack(sprite.Enemy):
    def __init__(self):
        super().__init__("bojack.png", 0.2)
        self.health = 5
        self.speed = -2

class Arianne(sprite.Enemy):
    def __init__(self):
        super().__init__("aryanne.png", 0.2)
        self.health = 5
        self.speed = -3
        self.t_last_attack = 0
    def attack(self):
        self.speed = 0
        self.raw_image = pygame.image.load("aryanne-attack.png")


screen = pygame.display.set_mode((1200, 800))
twilight = sprite.Sprite("twilight.png", 0.05)
rifle = sprite.Sprite("rifle.png", 0.1)
rifle.set_pos((160, 710))
bg = pygame.image.load("bg.png")
twilight.set_pos((100, 700))
entities = []
particles = []
FPS = 1/30
running = True
enemy_pain_sounds = [pygame.mixer.Sound(f"pain{i}.wav") for i in range(1, 7)]
shoot_snd = pygame.mixer.Sound("shoot.wav")
pygame.mixer.music.load("05. Corrupted by Design.mp3")
if "--nomusic" not in argv: pygame.mixer.music.play()
blood_particle = pygame.image.load("blood.png")

pygame.display.set_caption("MLP Haters killing time!")
pygame.display.set_icon(pygame.image.load("icon.png"))

class Bullet(sprite.Sprite):
    def __init__(self):
        super().__init__("bullet.png", scale=0.17)
        self.deg = rifle.deg
        self.x = rifle.x-17*sin(self.deg)
        self.y = rifle.y-17*cos(self.deg)
        self.vel = 60
        self.update()
    def update(self):
        self.x+=self.vel*cos(self.deg)
        self.y-=self.vel*sin(self.deg)

def check_bullets():
    global entities, particles
    for a in entities:
        if not isinstance(a, Bullet): continue
            # if it is not a bullet, do nothing
        for b in entities:
            if type(b) in [Bojack] and a.collides(b):
                #For every bojack horse, normie or space marine
                b.health-=1
                particles.append(sprite.BloodParticle(b, a.x, a.y))
                entities.remove(a)
                random.choice(enemy_pain_sounds).play()
                if b.health <= 0:
                    entities.remove(b)
                    for p in particles[:]:
                        if p.parent == b:
                            particles.remove(p)
                else:
                    b.change_phrases()
                break

def die():
    print("Dying...")
    global running
    pygame.mixer.music.stop()
    pygame.mixer.music.load("death_screen.mp3")
    pygame.mixer.music.play()
    msg = sprite.Label("", font=("NotoSans", 22), color=(255, 255, 255))
    msg.wraplength = 1000
    msg.y = 400
    msg.x = 600
    t0 = time.time()
    shown = ""
    game_over = sprite.Label("GAME OVER", font=("NotoSerif", 150), color=(255, 255, 255))
    game_over.wraplength=1000
    game_over.y = 70
    game_over.x = 600
    while True:
        if time.time() - t0 > 0.1 and len(shown) < len(DEATH_MSG):
            shown+=DEATH_MSG[len(shown)]
            msg.text = shown
        screen.fill((0,0,0))
        msg.blit(scr=screen)
        game_over.blit(scr=screen)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                return
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    running = False
                    return
        time.sleep(FPS)

def check_death():
    for en in entities:
        #print(id(en), en.collides(twilight))
        if type(en) in [Bojack] and en.x < 200:
            die()

enemySpawner = Thread(target=spawn_enemies)
enemySpawner.start()
last_bullet_shot = 0
while running:
    t0 = time.time()
    twilight.blit(scr=screen)
    rifle.blit(scr=screen)
    rifle.rotate(calculate_angle((rifle.x, rifle.y), pygame.mouse.get_pos()))
    pygame.display.update()
    pygame.display.flip()
    screen.blit(bg, (0, 0))

    for e in entities[:]:
        e.update()
        e.blit(scr=screen)
        if e.check_out_of_bounds((1200, 800)):
            entities.remove(e)

    for p in particles:
        p.blit(scr=screen)

    check_bullets()

    if pygame.mouse.get_pressed()[0] and time.time()-last_bullet_shot>0.1:
        entities.append(Bullet())
        last_bullet_shot = time.time()
        shoot_snd.play()

    check_death()

    performance = 0
    while time.time()-t0<=FPS:
        time.sleep(0.005)
        performance+=1
    l = sprite.Label(f"Performance: {performance}")
    l.x = 100
    l.y = 10
    l.blit(scr=screen)

    t0 = time.time()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
            del enemySpawner
