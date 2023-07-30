import pygame
import time
import sys
import math
from Settings import *
from Scripts.Entities import PhysicsEntity, Player, Enemy
from Scripts.Utils import Load_IMG
from Scripts.Utils import Load_IMGS, Animation, Sprite_sheet_IMGS
from Scripts.Tilemap import Titlemap
from Scripts.Clouds import Clouds
from Scripts.Particles import Particles
from Scripts.Projectiles import En_Pro, Pl_Pro
from Scripts.Health_pack import Health
import Scripts.Boss
import random
import os, os.path


class Game():
    def __init__(self):
        global level
        self.assets = {
            'Decor' : Load_IMGS('tiles/decor'),
            'Grass' : Load_IMGS('tiles/grass'),
            'Stone' : Load_IMGS('tiles/stone'),
            'Large_decor' : Load_IMGS('tiles/large_decor'),
            'Player' : Load_IMG('entities/player.png'),
            'Background' : Load_IMG('background.png'),
            'Clouds' : Load_IMGS('clouds'),
            'Health' : Animation(Load_IMGS('tiles/health'), dur = 6),
            'Player/idle' : Animation(Load_IMGS('entities/player/idle'), dur= 6),
            'Player/run' : Animation(Load_IMGS('entities/player/run'), dur= 4),
            'Player/slide' : Animation(Load_IMGS('entities/player/slide')),
            'Player/jump' : Animation(Load_IMGS('entities/player/jump')),
            'Player/wall_slide' : Animation(Load_IMGS('entities/player/wall_slide')),
            'Particles/leaf' : Animation(Load_IMGS('particles/leaf'), dur= 20, loop = False),
            'Particles/particle' : Animation(Load_IMGS('particles/particle'), dur = 10, loop= False),
            'Particles/blood' : Animation(Load_IMGS('particles/blood'), dur = 10, loop= False),
            'Enemy/idle' : Animation(Load_IMGS('entities/enemy/idle'), dur = 6),
            'Enemy/run' : Animation(Load_IMGS('entities/enemy/run'), dur = 4),
            'Gun' : Load_IMG('gun.png'),
            'Projectile': Load_IMG('projectile.png'),
            'Shuriken' : Load_IMG('shuriken.png'),
            'Boss_1/attack1' : Animation(Sprite_sheet_IMGS('entities/boss1/Attack.png', (59, 51), 81, 50, 150, 8), dur = 10),
            'Boss_1/idle' : Animation(Sprite_sheet_IMGS('entities/boss1/Idle.png', (53,45), 36, 57, 150, 8 ), dur= 8),
            'Boss_1/move' : Animation(Sprite_sheet_IMGS('entities/boss1/Move.png', (50, 35), 49, 66, 150, 8), dur= 8),
            'Boss_1/death' : Animation(Sprite_sheet_IMGS('entities/boss1/Death.png', (53,51), 51, 56, 150, 5), dur= 8, loop= False),
            'Boss_1/hit' : Animation(Sprite_sheet_IMGS('entities/boss1/Take Hit.png', (54, 45), 37, 55, 150, 4), dur= 8),
        }

        self.Particles = []
        self.Health = []
        

        self.Player = Player((50,50), (8, 15), self.assets, self.Particles)
        self.Tilemap = Titlemap(self.assets)
        self.scroll = [0, 0]
        self.Clouds = Clouds(self.assets['Clouds'])


        dest = 'data/maps/' + str(level) + '.json'
        try:
            self.Tilemap.load(dest)
        except FileNotFoundError:
            pass
        
        self.Boss = []
        for boss in self.Tilemap.extract([('Boss', 0)]):
            if boss['variant'] == 0:
                self.Boss.append(Scripts.Boss.Boss_1(self, (boss['pos'][0], boss['pos'][1]), 'Boss_1', 'Evil Wizard'))

        self.Leaf_spawner = []
        for tree in self.Tilemap.extract([('Large_decor', 2)], True):
            self.Leaf_spawner.append(pygame.Rect(tree['pos'][0] + 4, tree['pos'][1] + 4, 23, 13))
        
        self.enemies = []
        self.Projectiles = []
        
        for spawner in self.Tilemap.extract([('Spawner', 0), ('Spawner', 1)]):
            if spawner['variant'] == 0:
                self.Player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(spawner['pos'], (8,16), self.assets, self.Particles, self.Player))
        
        self.End = False

        self.transition = -30

        if len(self.Boss):
            self.target = self.Boss[0]

    def Boss_health_name(self, screen, boss):
        surf = Font.render(boss.name, True, "white")
        screen.blit(surf, (280, 410))
        Health_bar = 600 * boss.health / boss.health_max
        Health_bar_rect = pygame.Rect(20, 440, Health_bar, 25)
        pygame.draw.rect(screen, 'aquamarine3', Health_bar_rect)
        
    def Run(self):

        if not len(self.enemies) and not len(self.Boss):
            self.transition += 1
        if self.transition < 0:
            self.transition += 1
        

        Display.fill( (0,0,0,0) )
        Display2.blit(self.assets['Background'], (0,0))
        self.scroll[0] += (self.Player.rect().centerx - Display.get_width()/2 - self.scroll[0]) / 30 # type: ignore
        self.scroll[1] += (self.Player.rect().centery - Display.get_height()/2 - self.scroll[1]) / 20 # type: ignore
        render_scroll = (int(self.scroll[0]), int(self.scroll[1])) 


        for rect in self.Leaf_spawner:
            if random.random() * 20000 < rect.width * rect.height:
                pos = (rect.x + random.random()* rect.width, rect.y + random.random() * rect.height)
                self.Particles.append(Particles(self.assets, 'leaf', pos, velocity=[-0.1, 0.3], frame= random.randint(0 , 20)))

        self.Clouds.render(Display, offset= render_scroll)
        self.Clouds.update()

        self.Tilemap.render(Display, offset = render_scroll)

        for boss in self.Boss.copy():
            boss.update()
            boss.render(Display, offset= render_scroll)
            if boss.Dead:
                self.Boss.remove(boss)

        for enemy in self.enemies.copy():
            if enemy.update(self.Tilemap):
                if enemy.flip:
                    self.Projectiles.append(En_Pro(self, 'Projectile', (enemy.rect().centerx - 2, enemy.rect().centery -9 ), Vel= [-2,0] ))
                else:
                    self.Projectiles.append(En_Pro(self, 'Projectile', (enemy.rect().centerx + 2, enemy.rect().centery -9 ), Vel= [2, 0] ))
            if enemy.Dead:
                if random.randint(0, 100) <= 10:
                    self.Health.append(Health(self.assets, (enemy.pos[0], enemy.pos[1] + 10), random.choice([100, 150, 50])))
                self.enemies.remove(enemy)
                for i in range(100):
                    angle = random.random() * math.pi * 2
                    Pvel = [ math.cos(angle) * 1, math.sin(angle) * 1]
                    self.Particles.append(Particles(self.assets, 'blood', enemy.rect().center, velocity= Pvel, frame= random.randint(0, 30)))
            enemy.render(Display, offset = render_scroll)

        for pro in self.Projectiles.copy():
            pro.update(self.Tilemap)
            if pro.kill:
                if pro.count > pro.limit:
                    self.Projectiles.remove(pro)
            else:
                pro.render(Display, offset = render_scroll)

        if self.Player.update(self.Tilemap):
            if self.Player.flip:
                self.Projectiles.append(Pl_Pro(self, 'Shuriken', (self.Player.rect().centerx - 2, self.Player.rect().centery - 9), Vel= [-2,0], flip= self.Player.flip))
            else:
                self.Projectiles.append(Pl_Pro(self, 'Shuriken', (self.Player.rect().centerx + 2, self.Player.rect().centery - 9), Vel= [2, 0], flip= self.Player.flip ))

        if self.Player.Dead:
            self.End = True

        self.Player.render(Display, offset = render_scroll)

        for health in self.Health.copy():
            if self.Player.rect().colliderect(health.rect()):
                Healing_sound.play()
                self.Player.Health += health.Health
                health.kill = True
            if health.kill:
                self.Health.remove(health)
            health.update()
            health.render(Display, offset = render_scroll)

        Display_mask = pygame.mask.from_surface(Display)
        Display_sillouehette = Display_mask.to_surface(setcolor=(0,0,0,180), unsetcolor=(0,0,0,0))
        Display2.blit(Display_sillouehette, (2, 1))
        # for offset in [(1,0), (0,1), (-1, 0), (0, -1)]:
        #     Display2.blit(Display_sillouehette, offset)


        for Particle in self.Particles.copy():
            kill = Particle.update()
            if Particle.type == 'leaf':
                Particle.pos[0] += math.sin(Particle.animation.frame * (math.pi / 360)) * 0.3
            Particle.render(Display, offset = render_scroll)
            if kill:
                self.Particles.remove(Particle)

        if not len(self.enemies) and not len(self.Boss):
            global level
            global max_level
            level = min(level + 1, max_level)
            self.End = True
        
        if self.transition:
            trans_surf = pygame.Surface(Display.get_size())
            pygame.draw.circle(trans_surf, "white", (Display.get_width() /2, Display.get_height() /2), (30 - abs(self.transition)) * 8 )
            trans_surf.set_colorkey("white")
            Display.blit(trans_surf, (0,0))



if __name__ == '__main__':
    pygame.init()
    Font = pygame.font.Font('data/Pixeltype.ttf', 35)
    screen = pygame.display.set_mode((screen_w, screen_h))
    clock = pygame.time.Clock()

    pygame.mixer.music.load("data/music.wav")
    pygame.mixer.music.set_volume(0.5)

    Ambience = pygame.mixer.Sound('data/sfx/ambience.wav')
    Ambience.set_volume(0.5)
    pygame.mixer.music.play(-1)
    Ambience.play(-1)

    Healing_sound = pygame.mixer.Sound('data/sfx/heal.wav')
    Healing_sound.set_volume(0.5)


    #FPS
    FPS = 60  #FRAMERATE LIMITER
    FPS_Target = 60
    Prev_Time = time.time()
    Dt = 0
    max_level = len(os.listdir('data/maps'))
    level = 0

    Display = pygame.Surface((320, 240), pygame.SRCALPHA)
    Display2 = pygame.Surface((320, 240))
    Display3 = pygame.Surface((320, 240))

    Pause = False

    game = Game()

    while True:
        #CALCULATING DELTA TIME
        clock.tick(FPS)
        now = time.time()
        Dt = (now - Prev_Time) * FPS_Target
        Prev_Time = now
        pygame.display.set_caption( str( round(clock.get_fps(), 1 ) ) )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Pause = not Pause
        
        if game.End:
            game = Game()

        if not Pause:
            game.Run()
            Display2.blit(Display, (0,0))
            screen.blit(pygame.transform.scale(Display2, (screen_w, screen_h)), (0, 0))
            Health_display(game.Player.Health, screen)
            try:
                if game.target:
                    game.Boss_health_name(screen, game.target)
            except:
                pass
        else:
            text = Font.render('PAUSE',  True, 'white')
            screen.blit(text, (screen_w/2 - 10, screen_h/2 - 10))
        pygame.display.flip()