from stem.util.lru_cache import lru_cache
import sprite
import pygame
import time
import math
from threading import Thread
import random
from sys import argv
import phrases

def load_highscore():
    try:
        open("highscore.dat", 'x')
    except:
        pass
    finally:
        with open("highscore.dat") as F:
            return int(F.read() or 0)

def save_highscore():
    if highscore < score:
        with open("highscore.dat", 'w') as F:
            F.write(str(score))

DEATH_MSG = "They killed Twilight Sparkle. But do not give up! Don't let these bastards and perverts ruin your childhood. (Press Enter to exit)"

GFX_MODE = (1200, 800)

pygame.mixer.init()

#enemies_spawned_total = 0

@lru_cache(1000)
def sin(angle_deg):
    return math.sin(math.radians(angle_deg))

@lru_cache(1000)
def cos(angle_deg):
    return math.cos(math.radians(angle_deg))

def spawn_enemies():
    global entities, running
    t0 = time.time()
    k = 0
    while running:
        x = random.randint(int(5-k*0.05) if int(5-k*0.05)>2 else 2, int(20-k*0.1) if int(20-k*0.1)>8 else 8)
        if time.time()-t0>x:
            entities.append(random.choice([Avery, Arianne, Doomgay, Kosmodesantnik])())
            t0 = time.time()
            k+=1
        time.sleep(FPS)

def calculate_angle(sprite_pos, mouse_pos):
    dx = mouse_pos[0] - sprite_pos[0]
    dy = sprite_pos[1] - mouse_pos[1]
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    return angle_deg

class Kosmodesantnik(sprite.Enemy):
    def __init__(self):
        super().__init__(sprite.Animation(
            costumes=[pygame.image.load(f"kosmodesantnik-{i}.png") for i in range(1, 4 + 1)]
        ), 4)
        self.health = 25
        self.speed = -3
        self.t_last_attack = 0
        self.t_last_bullet = 0
        self.children[1] = sprite.Label(random.choice(phrases.phrases_kosmodesantnik_normal))
    def change_phrases(self, newstate = "PAIN"):
        if newstate == self.phrase_state[0]: return
        self.phrase_state = (newstate, time.time()+8)
        self.children[1] = sprite.Label(random.choice(eval(f"phrases.phrases_kosmodesantnik_{self.phrase_state[0].lower()}")))
    def attack(self):
        self.speed = 0
        self.pause_animation()
        self.t_last_attack = time.time()
    def stop_attack(self):
        self.speed = -3
        self.unpause_animation()

class Avery(sprite.Enemy):
    def __init__(self):
        super().__init__(sprite.Animation(
            costumes = [pygame.image.load(f"avery-{i}.png") for i in range(1, 4+1)]
        ), 0.4)
        self.health = 5
        self.speed = -2
        self.y-=40

class Doomgay(sprite.Enemy):
    def __init__(self):
        super().__init__(sprite.Animation(
            costumes = [pygame.image.load(f"doomgay-{i}.png") for i in range(1, 4+1)]
        ), 4)
        self.health = 15
        self.speed = -4
        self.y-=40

class Arianne(sprite.Enemy):
    def __init__(self):
        super().__init__("aryanne.png", 0.2)
        self.health = 5
        self.speed = -3
        self.t_last_attack = 0
        self.children[1] = sprite.Label(random.choice(phrases.phrases_aryanne_normal))
    def attack(self):
        self.speed = 0
        self.raw_image = pygame.image.load("aryanne-attack.png")
        self.t_last_attack = time.time()
    def stop_attack(self):
        self.speed = -3
        self.raw_image = pygame.image.load("aryanne.png")
    def change_phrases(self, newstate = "PAIN"):
        if newstate == self.phrase_state[0]: return
        self.phrase_state = (newstate, time.time()+8)
        self.children[1] = sprite.Label(random.choice(eval(f"phrases.phrases_aryanne_{self.phrase_state[0].lower()}")))

class Manhack(sprite.Enemy):
    def __init__(self):
        super().__init__("manhack.png")
        self.health = 2
        self.speed = 0
        self.xv = 0
        self.yv = -6
        self.scale = 0.1
    def update(self):
        if self.x - twilight.x > 300:
            self.xv-=0.05
            if self.yv < 0:
                self.yv+=0.1
        else:
            self.yv+=0.3
        self.x+=self.xv
        self.y+=self.yv

screen = pygame.display.set_mode(GFX_MODE)
import intro
pygame.mixer.music.load("07. She is Young, She is Beautiful, She is Next.mp3")
if "--nomusic" not in argv: pygame.mixer.music.play()
pygame.display.set_caption("MLP Haters killing time!")
pygame.display.set_icon(pygame.image.load("icon.png"))
intro.show()
twilight = sprite.Sprite("twilight.png", 0.05)
rifle = sprite.Sprite("rifle.png", 0.1)
rifle.set_pos((160, 710))
bg = pygame.image.load("bg.png")
twilight.set_pos((100, 700))
entities = []
#particles = []
FPS = 1/30
running = True
enemy_pain_sounds = [pygame.mixer.Sound(f"pain{i}.wav") for i in range(1, 7)]
shoot_snd = pygame.mixer.Sound("shoot.wav")
squadfire = pygame.mixer.Sound("squadfire.wav")
enemyfire = pygame.mixer.Sound("enemy_fire.wav")
pygame.mixer.music.load("mech-cathedral-fight.mp3")
if "--nomusic" not in argv: pygame.mixer.music.play(-1)
#blood_particle = pygame.image.load("blood.png")
pm = sprite.ParticleManager()
pygame.mouse.set_visible(False)
forcefield = sprite.Sprite("forcefield.png", 0.5)

score = 0
score_label = sprite.CustomFontLabel("", font=("Equestria.ttf", 30), color="#B58EBC")
score_label.x = GFX_MODE[0]/2
score_label.y = 70

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

class EnemyBullet(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__("bullet.png", scale=0.17)
        self.deg = 180
        self.x = x
        self.y = y
        self.vel = 60
        self.update()
    def update(self):
        self.x+=self.vel*cos(self.deg)
        self.y-=self.vel*sin(self.deg)

def add_corpse(original):
    x = type(original)
    if x == Avery:
        bg.blit(
            pygame.transform.scale(
                pygame.image.load("corpse/avery-1.png"),
                    (250, 100)
                    ),
            (original.x, original.y+random.randint(10, 50))
        )
    elif x == Doomgay:
        bg.blit(
            pygame.transform.scale(
                pygame.image.load("corpse/doomgay-1.png"),
                    (original.rheight*original.scale, original.rwidth*original.scale)
                    ),
            (original.x, original.y)
        )
    elif x == Kosmodesantnik:
        bg.blit(
            pygame.transform.scale(
                pygame.image.load("corpse/kosmodesantnik-1.png"),
                (original.rheight * original.scale, original.rwidth * original.scale)
            ),
            (original.x, original.y)
        )
    elif x == Arianne:
        bg.blit(
            pygame.transform.scale(
                pygame.image.load("corpse/arianne.png"),
                (original.rwidth * original.scale, original.rheight/2 * original.scale)
            ),
            (original.x, original.y)
        )

def check_bullets():
    global entities, score
    for a in entities:
        if not isinstance(a, Bullet): continue
            # if it is not a bullet, do nothing
        for b in entities:
            if type(b) in [Avery, Arianne, Manhack, Doomgay, Kosmodesantnik] and a.collides(b):
                #For every Avery horse, normie or space marine
                b.health-=1
                if type(b) in [Avery, Arianne, Doomgay, Kosmodesantnik]:
                    pm.create_blood(a.x, a.y, b.speed)
                    random.choice(enemy_pain_sounds).play()
                else:
                    pm.create_explosion(a.x, a.y)
                entities.remove(a)
                score+=10
                if b.health <= 0:
                    entities.remove(b)
                    add_corpse(b)
                    score+=100
                    if not type(b) == Manhack:
                        pm.create_gore(b.x, b.y)
                else:
                    b.change_phrases()
                break
    for a in entities[:]:
        if not isinstance(a, EnemyBullet): continue
        if a.collides(twilight):
            if forcefield_activated:
                entities.remove(a)
            else:
                die()

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
        if time.time() - t0 > 0.01 and len(shown) < len(DEATH_MSG):
            shown+=DEATH_MSG[len(shown)]
            msg.text = shown
            t0 = time.time()
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
        if type(en) in [Avery, Arianne, Doomgay, Kosmodesantnik] and en.collides(twilight):
            die()
        elif type(en) == Manhack:
            if en.collides(twilight):
                die()

def update_aryannes():
    global entities
    for a in entities:
        if type(a) == Arianne and time.time() - a.t_last_attack > 2 and a.speed == 0:
            entities.append(Manhack())
            entities[-1].x = a.x
            entities[-1].y = a.y
            a.stop_attack()
        elif type(a) == Manhack:
            a.update()

def update_kosmodesantniki():
    global entities, running
    while running:
        #print("Govno")
        for e in entities:
            if type(e) != Kosmodesantnik:
                continue
            if e.speed < 0:
                #Those who don't attack do this
                if time.time() - e.t_last_attack > 6 and random.randint(1, 3) == 2:
                    squadfire.play()
                    time.sleep(3)
                    e.attack()
            else:
                if time.time() - e.t_last_bullet > 0.4:
                    e.t_last_bullet = time.time()
                    entities.append(EnemyBullet(e.x, e.y-10))
                    enemyfire.play()
                if time.time() - e.t_last_attack > 3:
                    e.stop_attack()
        time.sleep(1)
        if not running: return

enemySpawner = Thread(target=spawn_enemies)
enemySpawner.start()
last_bullet_shot = 0
highscore = load_highscore()
space_marine_handler = Thread(target=update_kosmodesantniki)
space_marine_handler.start()

forcefield.x = twilight.x
forcefield.y = twilight.y
forcefield_activated = False
while running:
    t0 = time.time()
    twilight.blit(scr=screen)
    rifle.blit(scr=screen)
    rifle.rotate(calculate_angle((rifle.x, rifle.y), pygame.mouse.get_pos()))
    if forcefield_activated: forcefield.blit(scr=screen)
    pygame.display.update()
    pygame.display.flip()
    screen.blit(bg, (0, 0))

    for e in entities[:]:
        if type(e) == Arianne and random.randint(1, 100) == 42: #Ariannes randomly attack
            e.attack()
        e.update()
        e.blit(scr=screen)
        if e.check_out_of_bounds(GFX_MODE):
            entities.remove(e)

    pm.blit(scr = screen)

    if pygame.mouse.get_pressed()[0] and time.time()-last_bullet_shot>0.1 and not forcefield_activated:
        entities.append(Bullet())
        last_bullet_shot = time.time()
        shoot_snd.play()

    check_bullets()
    check_death()
    update_aryannes()

    performance = 0
    while time.time()-t0<=FPS:
        time.sleep(0.005)

        performance+=1
    l = sprite.Label(f"Performance: {performance}")
    l.x = 100
    l.y = 10
    l.blit(scr=screen)
    #print(len(entities))

    score_label.blit(scr=screen)
    score_label.text = str(score).zfill(6) + f"\n({highscore})"
    t0 = time.time()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
            del enemySpawner
            del space_marine_handler
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_z:
            forcefield_activated = True
        elif ev.type == pygame.KEYUP and ev.key == pygame.K_z:
            forcefield_activated = False

save_highscore()
import os
os._exit(0)
