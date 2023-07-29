import pygame
import random
import math
from Scripts.Particles import Particles
from Scripts.Health_pack import Health

hit_sound = pygame.mixer.Sound('data/sfx/hit.wav')
hit_sound.set_volume(0.2)

Dash_sound = pygame.mixer.Sound('data/sfx/dash.wav')
Dash_sound.set_volume(0.1)

Fire_sound = pygame.mixer.Sound('data/sfx/fire.mp3')
Fire_sound.set_volume(0.3)

class Boss:
    def __init__(self, game, pos, type, name,  Health = 10000, dmg = 50 ):
        self.name = name
        self.game = game
        self.type = type
        self.health = Health
        self.health_max = Health
        self.pos = list(pos)
        self.bound = [0,0,0,0]
        self.bound[0] = self.pos[0] + 250
        self.bound[1] = self.pos[0] - 250
        self.bound[2] = self.pos[1] + 250
        self.bound[3] = self.pos[1] - 250
        self.flip = False

        self.action = ''
        self.set_action('idle')

        self.Dir = pygame.math.Vector2()
        self.Dead = False
        self.attack_frame = 0
        self.dmg = dmg

        self.Dest = self.pos.copy()

        self.invs = 1000
        self.hurt_frame = 0

        self.cool_down = 2000
        self.cool_frame = 0

        self.Recover_cooldown = 500
        self.Recover_frame = 0

        self.attack_delay = 2000
        self.attack_frame = 0

        self.Burn_delay = 100
        self.Burn_frame = 0

        self.Death_delay = 2500
        self.Death_frame = 0
    
    def DMG(self, health):
        self.health -= health
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self):
        now = pygame.time.get_ticks()
        if self.rect().colliderect(self.game.Player.rect()):
            if abs(self.game.Player.Dasing) >= 40:
                if self.action != 'death':
                    if now - self.hurt_frame >= self.invs:

                        if random.randint(0, 100) <= 10:
                            self.game.Health.append(Health(self.game.assets, self.game.Player.rect().center, random.choice([100, 150, 50])))
                        
                        self.game.target = self

                        self.set_action('hit')
                        self.DMG(100)
                        self.hurt_frame = pygame.time.get_ticks()
                        self.Recover_frame = pygame.time.get_ticks()
                        for i in range(100):
                            angle = random.random() * math.pi * 2
                            Pvel = [ math.cos(angle) * 1, math.sin(angle) * 1]
                            self.game.Particles.append(Particles(self.game.assets, 'blood', self.rect().center, velocity= Pvel, frame= random.randint(0, 30)))
            elif self.action == 'hit' or self.action == 'death':
                pass
            else:
                if self.action == 'attack':
                    if now - self.Burn_frame >= self.Burn_delay:
                        hit_sound.play()
                        self.game.Player.DMG(10)
                        self.Burn_frame = pygame.time.get_ticks()
                else:
                    if now -self.attack_frame >= self.game.Player.invs:
                        hit_sound.play()
                        self.attack_frame = pygame.time.get_ticks()
                        self.game.Player.DMG(self.dmg)

        self.pos[0] += self.Dir.x
        self.pos[1] += self.Dir.y

        if self.health <= 0:
            if self.Death_frame == 0:
                self.Death_frame = pygame.time.get_ticks()
            self.set_action('death')
            if now - self.Death_frame >= self.Death_delay:
                self.Dead = True

        if self.action == 'hit':
            if now - self.Recover_frame >= self.Recover_cooldown:
                self.set_action('idle')

        if abs(int(self.pos[0] - self.Dest[0])) <= 5:
            self.Dir.x = 0
        else:
            self.Dir.x = (self.Dest[0] - self.pos[0]) / 10

        if abs(int(self.pos[1] - self.Dest[1])) <= 5:
            self.Dir.y = 0
        else:
            self.Dir.y = (self.Dest[1] - self.pos[1]) / 10
        
        if self.Dir.x > 0:
            self.flip = False
        elif self.Dir.x < 0:
            self.flip = True
        
        if self.action != 'hit' and self.action != 'death':
            if self.action == 'attack':
                if self.Dir.x == 0 and self.Dir.y == 0:
                    if now - self.attack_frame >= self.attack_delay:
                        self.set_action('idle')
            else:
                if self.Dir.x == 0 and self.Dir.y == 0:
                    self.set_action('idle')

        # if self.Dir.x > 0:
        #     self.flip = False
        #     self.Dir.x = max(self.Dir.x - 1, 0)
        # if self.Dir.x < 0:
        #     self.flip = True
        #     self.Dir.x = min(self.Dir.x + 1, 0 )
        # if self.Dir.x == 0:
        #     self.set_action('idle')

        self.animation.update()
    
    def render(self, surf, offset = (0,0)):
        surf.blit(pygame.transform.flip(self.animation.IMG(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))
    
    def rect(self):
        img = self.animation.IMG()
        return pygame.Rect(self.pos[0], self.pos[1], img.get_width(), img.get_height())

class Boss_1(Boss):
    def __init__(self, game, pos, type, name, Health = 10000):
        super().__init__(game, pos, type, name, Health)

    def update(self):
        super().update()
        self.Move()    
        
    def Move(self):
        now = pygame.time.get_ticks()
        if self.action == 'idle':
            if now - self.cool_frame >= self.cool_down:
                self.cool_frame = pygame.time.get_ticks()
                chance = random.randint(0, 100)
                if chance <= 50:
                    self.attack_frame = pygame.time.get_ticks()
                    self.set_action('attack')
                    Dash_sound.play()
                    Fire_sound.play()
                    #X AXIS
                    self.Dest[0] = self.game.Player.pos[0]
                    #Y AXIS
                    self.Dest[1] = self.game.Player.pos[1] - 20
                elif chance <= 85:
                    self.set_action('move')
                    Dash_sound.play()
                    #X AXIS
                    if self.pos[0] + 200 >= self.bound[0]:
                        self.Dest[0] = self.pos[0] + random.randrange(-200, -50, 10)
                    elif self.pos[0] - 200 <= self.bound[1]:
                        self.Dest[0] = self.pos[0] + random.randrange(50, 200, 10)
                    else:
                        step = random.randrange(-200, 200, 10)
                        if step >= 0 and step < 50:
                            step = 50
                        elif step < 0 and step > -50:
                            step = -50
                        self.Dest[0] = self.pos[0] + step

                    #Y AXIS
                    if self.pos[1] + 100 >= self.bound[2]:
                        self.Dest[1] = self.pos[1] + random.randrange(-100, -50, 10)
                    elif self.pos[1] - 100 <= self.bound[3]:
                        self.Dest[1] = self.pos[1] + random.randrange(50, 100, 10)
                    else:
                        step = random.randrange(-100, 100, 10)
                        if step >= 0 and step < 50:
                            step = 50
                        elif step < 0 and step > -70:
                            step = -70
                        self.Dest[1] = self.pos[1] + step
    
