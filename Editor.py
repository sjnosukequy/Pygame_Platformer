import pygame
import time
import sys
from Settings import *

from Scripts.Utils import Load_IMG
from Scripts.Utils import Load_IMGS
from Scripts.Tilemap import Titlemap

RENDER_SCALE = 2.0

class Editor():
    def __init__(self):
        self.assets = {
            'Decor' : Load_IMGS('tiles/decor'),
            'Grass' : Load_IMGS('tiles/grass'),
            'Stone' : Load_IMGS('tiles/stone'),
            'Large_decor' : Load_IMGS('tiles/large_decor'),
            'Spawner' : Load_IMGS('tiles/spawners')
        }

        self.Tilemap = Titlemap(self.assets)
        self.scroll = [0, 0]

        self.Tile_list = list(self.assets)
        self.Tile_group = 0
        self.Tile_variant = 0

        try:
            self.Tilemap.load('map.json')
        except FileNotFoundError:
            pass

    def Run(self):

        self.scroll[0] += (Movement[1] - Movement[0]) * 2
        self.scroll[1] += (Movement[3] - Movement[2]) * 2

        Display.fill('purple')
        current_tile_img = self.assets[self.Tile_list[self.Tile_group]][self.Tile_variant].copy()
        current_tile_img.set_alpha(150)

        self.mpos = pygame.mouse.get_pos()
        self.mpos = (self.mpos[0]/ RENDER_SCALE, self.mpos[1] / RENDER_SCALE)
        tile_pos = (int(self.mpos[0] + self.scroll[0]) // self.Tilemap.title_size, int(self.mpos[1] + self.scroll[1]) // self.Tilemap.title_size)

        #GHOSTING
        if not On_grid:
            Display.blit(current_tile_img, self.mpos)
        else:
            Display.blit(current_tile_img, (tile_pos[0]* self.Tilemap.title_size - self.scroll[0], tile_pos[1]* self.Tilemap.title_size - self.scroll[1]))

        if clicking and On_grid:
            self.Tilemap.titlemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = { 'type' : self.Tile_list[self.Tile_group], 'variant' : self.Tile_variant, 'pos' : (tile_pos[0], tile_pos[1]) }
        if right_click:
            tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
            if tile_loc in self.Tilemap.titlemap:
                del self.Tilemap.titlemap[tile_loc]
            
            for tile in self.Tilemap.offgrid_map.copy():
                img = self.assets[tile['type']][tile['variant']]
                img_rect = pygame.Rect(tile['pos'][0] + self.scroll[0], tile['pos'][1] + self.scroll[1], img.get_width(), img.get_height())
                if img_rect.collidepoint(self.mpos[0], self.mpos[1]):
                    self.Tilemap.offgrid_map.remove(tile)

        Display.blit(current_tile_img, (5,5))
        render_scroll = (int(self.scroll[0]), int(self.scroll[1])) 

        self.Tilemap.render(Display, offset = render_scroll)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((screen_w, screen_h))
    clock = pygame.time.Clock()

    #FPS
    FPS = 60  #FRAMERATE LIMITER
    FPS_Target = 60
    Prev_Time = time.time()
    Dt = 0

    editor = Editor()

    Movement = [False, False, False, False]

    clicking = False
    right_click = False
    shift = False

    On_grid = True

    while True:
        #CALCULATING DELTA TIME
        clock.tick(FPS)
        now = time.time()
        Dt = (now - Prev_Time) * FPS_Target
        Prev_Time = now
        pygame.display.set_caption( str( round(clock.get_fps(), 1 ) ) )

        Display = pygame.Surface((320, 240))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicking = True
                    if not On_grid:
                        editor.Tilemap.offgrid_map.append({'type' : editor.Tile_list[editor.Tile_group], 'variant' : editor.Tile_variant, 'pos' : (editor.mpos[0] + editor.scroll[0], editor.mpos[1] + editor.scroll[1])})
                if event.button == 3:
                    right_click = True
                if shift == False:
                    if event.button == 4:
                        editor.Tile_group = (editor.Tile_group - 1) % len(editor.Tile_list)
                        if editor.Tile_variant >=  len(editor.assets[editor.Tile_list[editor.Tile_group]]):
                            editor.Tile_variant = 0
                    if event.button == 5:
                        editor.Tile_group = (editor.Tile_group + 1) % len(editor.Tile_list)
                        if editor.Tile_variant >=  len(editor.assets[editor.Tile_list[editor.Tile_group]]):
                            editor.Tile_variant = 0
                else:
                    if event.button == 4:
                        editor.Tile_variant = (editor.Tile_variant - 1) % len(editor.assets[editor.Tile_list[editor.Tile_group]])
                    if event.button == 5:
                        editor.Tile_variant = (editor.Tile_variant + 1) % len(editor.assets[editor.Tile_list[editor.Tile_group]])
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    clicking = False
                if event.button == 3:
                    right_click = False
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    Movement[2] = True
                if event.key == pygame.K_s:
                    Movement[3] = True
                if event.key == pygame.K_a:
                    Movement[0] = True
                if event.key == pygame.K_d:
                    Movement[1] = True
                if event.key == pygame.K_LSHIFT:
                    shift = True
                if event.key == pygame.K_g:
                    On_grid = not On_grid
                if event.key == pygame.K_o:
                    editor.Tilemap.save('map.json')
                if event.key == pygame.K_t:
                    editor.Tilemap.AutoTile()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    Movement[2] = False
                if event.key == pygame.K_s:
                    Movement[3] = False
                if event.key == pygame.K_a:
                    Movement[0] = False
                if event.key == pygame.K_d:
                    Movement[1] = False
                if event.key == pygame.K_LSHIFT:
                    shift = False

        editor.Run()
        screen.blit(pygame.transform.scale(Display, (screen_w, screen_h)), (0, 0))
        pygame.display.flip()