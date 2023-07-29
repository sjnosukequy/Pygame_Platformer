import pygame
import random, math
from Scripts.Particles import Particles
from Scripts.Health_pack import Health

pygame.init()

shoot = pygame.mixer.Sound('data/sfx/shoot.wav')
shoot.set_volume(0.2)
hit_sound = pygame.mixer.Sound('data/sfx/hit.wav')
hit_sound.set_volume(0.2)

class Projectiles():
    def __init__(self, game, type, pos, Vel = [0,0], flip = False):
        self.game = game
        self.type = type
        self.pos = list(pos)
        self.Vel = Vel
        self.img = self.game.assets[self.type]
        self.flip = flip
        self.Timer = 0
        shoot.play()
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1] + 5, 4, 4)

    def update(self, tilemap):
        self.Timer += 1
        self.pos[0] += self.Vel[0]    
    
    def render(self, surf, offset = (0,0)):
         surf.blit(pygame.transform.flip(self.img, self.flip, False) ,(self.pos[0] - offset[0], self.pos[1] - offset[1] + 5))

class En_Pro(Projectiles):
    def __init__(self, game, type, pos, Vel):
        super().__init__(game, type, pos, Vel)
        self.limit = 7
        self.count = 0
        self.kill = False
        self.Rect = any
        self.Part_type = 0

    def update(self, tilemap):
        if not self.kill:
            super().update(tilemap)
            rects = tilemap.Physics_rect_around(self.pos)
            for rect in rects:
                if self.rect().colliderect(rect):
                    self.kill = True
                    self.Rect = self.rect()
                    return

            if self.Timer >= 200:
                self.kill = True
                self.Rect = self.rect()
                return   

            if self.rect().colliderect(self.game.Player.rect()) and abs(self.game.Player.Dasing) <= 50:
                hit_sound.play()
                self.game.Player.DMG(50)
                self.kill = True
                self.Part_type = 1
                self.Rect = self.rect()
                return
                 
            return
        else:
            if self.Part_type == 1:
                angle = random.random() * math.pi * 2
                Pvel = [- abs(self.Vel[0])/self.Vel[0], math.sin(angle) * 0.5]
                self.game.Particles.append(Particles(self.game.assets, 'blood', self.Rect.center, velocity= Pvel, frame= random.randint(0, 30)))
                self.count += 1
            else:
                angle = random.random() * math.pi * 2
                Pvel = [- abs(self.Vel[0])/self.Vel[0], math.sin(angle) * 0.5]
                self.game.Particles.append(Particles(self.game.assets, 'particle', self.Rect.center, velocity= Pvel, frame= random.randint(0, 30)))
                self.count += 1

class Pl_Pro(Projectiles):
    def __init__(self, game, type, pos, Vel, flip):
        super().__init__(game, type, pos, Vel, flip)
        self.limit = 7
        self.count = 0
        self.kill = False
        self.Rect = any
        self.Part_type = 0

    def update(self, tilemap):
        if not self.kill:
            super().update(tilemap)
            rects = tilemap.Physics_rect_around(self.pos)
            for rect in rects:
                if self.rect().colliderect(rect):
                    self.kill = True
                    self.Rect = self.rect()
                    return

            if self.Timer >= 200:
                self.kill = True
                self.Rect = self.rect()
                return 
            
            for boss in self.game.Boss:
                if self.rect().colliderect(boss.rect()):
                    self.game.target = boss
                    if boss.action != 'death':
                        if random.randint(0, 100) <= 10:
                            self.game.Health.append(Health(self.game.assets, self.rect().center, random.choice([100, 150, 50])))
                            
                        boss.set_action('hit')
                        boss.Recover_frame = pygame.time.get_ticks()
                        boss.DMG(50)
                    hit_sound.play()
                    self.kill = True
                    self.Part_type = 1
                    self.Rect = self.rect()
                    return
            
            for en in self.game.enemies:
                if self.rect().colliderect(en.rect()):
                    hit_sound.play()
                    en.DMG(50)
                    self.kill = True
                    self.Part_type = 1
                    self.Rect = self.rect()
                    return
            return
        else:
            if self.Part_type == 1:
                angle = random.random() * math.pi * 2
                Pvel = [- abs(self.Vel[0])/self.Vel[0], math.sin(angle) * 0.5]
                self.game.Particles.append(Particles(self.game.assets, 'blood', self.Rect.center, velocity= Pvel, frame= random.randint(0, 30)))
                self.count += 1
            else:
                angle = random.random() * math.pi * 2
                Pvel = [- abs(self.Vel[0])/self.Vel[0], math.sin(angle) * 0.5]
                self.game.Particles.append(Particles(self.game.assets, 'particle', self.Rect.center, velocity= Pvel, frame= random.randint(0, 30)))
                self.count += 1