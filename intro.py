from __main__ import screen, GFX_MODE
import threading
import pygame
import time
from sprite import Label
intro = True

background = None
story_label = Label("", color=(255, 255, 255))
story_label.bgcolor = (0, 0, 0)
story_label.x = GFX_MODE[0]/2
story_label.y = GFX_MODE[1]/2+300
story_label.wraplength = GFX_MODE[0]-100
n = 0

STORY = [
    "There once was peace and harmony in equestria.",
    "But then 4chan users changed everything. ",
    "It first seemed to be normal, and more and more people became really into horses.",
    "But not everyone was happy with that. More and more people called ponyposters 'cancer' and 'cringe'.",
    "Soon ponyposting was banned. And bronies had to flee. (cartoons are for kids)",
    "And Warhammer 40k fans started to attack something that once was a prosperous fandom.",
    "The energy of /pol/ started to rush into equestria, resulting in deadly mutations which irreversibly changed ponies",
    "turning them into nazis.",
    "The gamma ray spikes caused by this energy outburst, were noticed by the God Emperor of Mankind.",
    "With the help of /wh/ users he quickly found the location of equestria planet.",
    "Ponies aren't humans => they're Xenos => ponies are bad.",
    "Also they use magic and this is prohibited by the emperor (because of course it is) => ponies are bad.",
    "Ponies are bad => They must all be exterminated.",
    "Very soon after the beginning of the invasion it became obvious that while friendship may be magic in this universe",
    "those who want to kill ponies can't be neither loved nor tolerated. "
]

def show_story():
    global background, story_label, intro, n
    background = pygame.transform.scale(
        pygame.image.load("intro/harmony.png"), GFX_MODE
    )
    n = 0
    for i in STORY[n]:
        story_label.text+=i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n+=1
    background = pygame.transform.scale(
        pygame.image.load("intro/iwtcird.png"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/iwtcird.png"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/cringe.jpg"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/heresy.png"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/exterminatus_2.jpg"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/mutation.jpg"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/nazi.png"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/godemperor.jpg"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/planet.png"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/xenos.png"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/prohibited.png"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/exterminatus.png"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/notolerate.png"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    background = pygame.transform.scale(
        pygame.image.load("intro/notolerate.png"), GFX_MODE
    )
    for i in STORY[n]:
        story_label.text += i
        time.sleep(0.1)
    time.sleep(2)
    story_label.text = ""
    n += 1
    story_label.text="Press [Enter]"


def show():
    global intro
    threading.Thread(target=show_story).start()
    time.sleep(0.5)
    while intro:
        pygame.display.flip()
        screen.blit(background, (0, 0))
        story_label.blit(scr=screen)
        pygame.display.update()
        time.sleep(1/30)
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                import os
                os._exit(0)
            elif e.type == pygame.KEYDOWN and (e.key == pygame.K_ESCAPE or (e.key == pygame.K_RETURN and n == 15)):
                intro = False