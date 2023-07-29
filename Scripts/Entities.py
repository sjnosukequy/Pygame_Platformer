import pygame
import random
import math
from Scripts.Particles import Particles

pygame.init()

Dash_sound = pygame.mixer.Sound('data/sfx/dash.wav')
Jump_sound = pygame.mixer.Sound('data/sfx/jump.wav')
Dash_sound.set_volume(0.1)
Jump_sound.set_volume(0.5)

hit_sound = pygame.mixer.Sound('data/sfx/hit.wav')
hit_sound.set_volume(0.2)

class PhysicsEntity():
    def __init__(self, e_type ,pos, size, assets, part, Health = 100):
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.assets = assets
        self.Vel = pygame.math.Vector2()
        self.Dir = pygame.math.Vector2()
        self.Coll = {'left': False, 'right': False, "top": False, 'bottom': False}
        self.Particles = part

        self.action = ''
        self.animations_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

        self.jumps = 1
        self.Walljump = False
        self.Dasing = 0

        self.Dead = False
        self.Health = Health
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def DMG(self ,dmg):
        self.Health -= dmg
        if self.Health <= 0:
            self.Dead = True
    
    def FALL_DEAD(self):
        if self.pos[1] > 600:
            self.Dead = True
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.assets[self.type + '/' + self.action].copy()

    def Movement(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.jump()
        elif keys[pygame.K_s]:
            self.Dir.y = 1
        else:
            self.Dir.y = 0

        if keys[pygame.K_a]:
            self.Dir.x = -1
        elif keys[pygame.K_d]:
            self.Dir.x = 1
        else:
            self.Dir.x = 0
        
        if keys[pygame.K_l]:
            self.dash()
    
    def jump(self):
        if self.jumps:
            Jump_sound.play()
            self.Vel.y = -1 * 3
            self.jumps -= 1
        if self.Coll['right'] or self.Coll['left']:
            self.Walljump = True
    
    def dash(self):   
        if not self.Dasing:
            Dash_sound.play()
            if self.flip:
                self.Dasing = -60
            else:
                self.Dasing = 60

    def update(self, tilemap):
        self.Walljump = False

        if self.type == 'Player':
            self.Movement()
        
        # if self.Vel.x == 0 and self.Dasing:
        #     self.Dasing = not self.Dasing
        #     for i in range(50):
        #         angle = random.random() * math.pi * 2
        #         Pvel = [math.cos(angle) * 2, math.sin(angle) * 2]
        #         rect = self.rect()
        #         self.Particles.append(Particles(self.assets, 'particle', rect.center, velocity= Pvel, frame= random.randint(0, 30)))

        
        self.Coll = {'left': False, 'right': False, "top": False, 'bottom': False}
        frame_movement = self.Vel +  self.Dir

        self.pos[0] += frame_movement.x
        entity_rect = self.rect()
        for rect in tilemap.Physics_rect_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.Coll['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.Coll['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement.y
        entity_rect = self.rect()
        for rect in tilemap.Physics_rect_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.Coll['bottom'] = True
                    self.jumps = 1
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.Coll['top'] = True
                self.pos[1] = entity_rect.y

        if self.Dir.x > 0:
            self.flip = False
        elif self.Dir.x < 0:
            self.flip = True
    
        self.Vel.y = min(5, self.Vel.y + 0.1)
        if self.Coll['bottom'] or self.Coll['top']:
            self.Vel.y = 0

        if self.Vel.x < 0:
            self.Vel.x = min(self.Vel.x + 0.1, 0)
        else:
            self.Vel.x = max(self.Vel.x - 0.1, 0)
        
        if self.Dasing > 0:
            self.Dasing = max(self.Dasing - 1, 0)
        if self.Dasing < 0:
            self.Dasing = min(self.Dasing + 1, 0)
        if abs(self.Dasing) > 50:
            self.Vel[0] = abs(self.Dasing)/self.Dasing * 10
            if abs(self.Dasing) == 51:
                self.Vel[0] *= 0.1
            Pvel = [0,0]
            Pvel[0] = abs(self.Dasing)/self.Dasing * 0.3 #type: ignore 
            Pvel[1] = random.randrange(-10, 11) / 10 * 0.3 # type: ignore
            rect = self.rect()
            self.Particles.append(Particles(self.assets, 'particle', rect.center, velocity= Pvel, frame= random.randint(0, 30)))
        
        if abs(self.Dasing) in {59, 50}:
            for i in range(50):
                angle = random.random() * math.pi * 2
                Pvel = [math.cos(angle) * 1, math.sin(angle) * 1]
                rect = self.rect()
                self.Particles.append(Particles(self.assets, 'particle', rect.center, velocity= Pvel, frame= random.randint(0, 30)))

        self.animation.update()
        self.FALL_DEAD()

    def render(self, surf, offset = (0,0)):
        surf.blit(pygame.transform.flip(self.animation.IMG(), self.flip, False), (self.pos[0] - offset[0] + self.animations_offset[0], self.pos[1] - offset[1] + self.animations_offset[1]))


class Player(PhysicsEntity):
    def __init__(self, pos, size, assets, part, Health = 400):
        super().__init__('Player', pos, size, assets, part , Health)
        self.Air_time = 0
        self.Wall_slide = False
        self.reload_time = 800
        self.reloading = 0
        self.invs = 1000

    def update(self, tilemap):
        super().update(tilemap)
        self.Air_time += 1

        if self.Coll['bottom']:
            self.Air_time = 0

        self.Wall_slide = False
        if self.Coll['right'] or self.Coll['left'] and self.Air_time > 4:
            self.Wall_slide = True
            self.Vel.y = min(self.Vel.y, 0.5)
            if self.Coll['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

        if self.Walljump and self.Air_time > 45:
            Jump_sound.play()
            self.Air_time = 4
            self.Vel.y = -2.5
            if self.Coll['right']:
                self.Vel.x = -2.5
            else:
                self.Vel.x = 2.5

        if not self.Wall_slide:
            if self.Air_time > 4:
                self.set_action('jump')
            elif self.Dir.x != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_j]:
            return self.attack()
        
        return False

    def render(self, surf, offset=(0, 0)):
        if abs(self.Dasing) <= 50:
            super().render(surf, offset)
            #RENDER THE GUN
            # if self.action != 'wall_slide':
            #     rect = self.rect()
            #     rect.x -= offset[0]
            #     rect.y -= offset[1]
            #     if self.flip:
            #         surf.blit(pygame.transform.flip(self.assets['Gun'], self.flip, False), (rect.centerx - 10, rect.centery - 2))
            #     else:
            #         surf.blit(pygame.transform.flip(self.assets['Gun'], self.flip, False), (rect.centerx + 5, rect.centery - 2 ))
    
    def attack(self):
        now = pygame.time.get_ticks()
        if now - self.reloading >= self.reload_time:
            self.reloading = pygame.time.get_ticks()
            return True
        return False

class Enemy(PhysicsEntity):
    def __init__(self, pos, size, assets, part, player):
        super().__init__('Enemy', pos, size, assets, part)
        self.walking = 0
        self.Player = player

        self.reload_time = 1000
        self.reloading = 0

    def update(self, tilemap):

        if self.rect().colliderect(self.Player.rect()) and abs(self.Player.Dasing) >= 50:
            hit_sound.play()
            self.DMG(self.Health)

        self.Dir.x = 0
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-10 if self.flip else 10), self.pos[1] + 16)):
                if self.Coll['left'] or self.Coll['right']:
                    self.flip = not self.flip
                self.Dir.x = ( -0.8 if self.flip else 0.8)
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
        elif random.random() < 0.01:
            self.walking = random.randint(30,120)

        super().update(tilemap)

        if self.Dir.x != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        
        return self.attack()
    
    def attack(self):
        now = pygame.time.get_ticks()
        if now - self.reloading >= self.reload_time:
            self.reloading = pygame.time.get_ticks()
            if abs(self.pos[1] - self.Player.pos[1]) <= 30:
                if abs(self.pos[0] - self.Player.pos[0]) <= 100:
                    if self.flip and self.pos[0] >= self.Player.pos[0]:
                        return True
                    elif not self.flip and self.pos[0] <= self.Player.pos[0]:
                        return True
        return False  


    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)
        rect = self.rect()
        rect.x -= offset[0]
        rect.y -= offset[1]
        if self.flip:
            surf.blit(pygame.transform.flip(self.assets['Gun'], self.flip, False), (rect.centerx - 12, rect.centery - 2))
        else:
            surf.blit(pygame.transform.flip(self.assets['Gun'], self.flip, False), (rect.centerx + 4, rect.centery - 2 ))
