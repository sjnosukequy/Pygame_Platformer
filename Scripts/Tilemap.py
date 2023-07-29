import pygame
import json

AUTO_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(1, 0), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

NEIGHBOR_OFFSET = [ (-1, 0), (-1,-1), (-1, 1), (0, 0), (0, -1), (0, 1), (1, 0), (1, -1), (1, 1) ]
PHYSICS_TILES = {'Grass', 'Stone'}
AUTO_TILES = {'Grass', 'Stone'}

class Titlemap:
    def __init__(self, assets, tile_size = 16):
        self.assets = assets
        self.title_size = tile_size
        self.titlemap = {}
        self.offgrid_map = []
    
    def Tile_around(self, pos):
        Tiles = []
        Title_loc = (int(pos[0] // self.title_size), int(pos[1] // self.title_size))
        for offset in NEIGHBOR_OFFSET:
            check_loc = str(Title_loc[0] + offset[0]) + ';' + str(Title_loc[1] + offset[1])
            if check_loc in self.titlemap:
                Tiles.append(self.titlemap[check_loc])
        return Tiles
    
    def extract(self, id_pair, keep = False):
        matches= []
        for tile in self.offgrid_map.copy():
            if (tile['type'], tile['variant']) in id_pair:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_map.remove(tile)
        
        for loc in self.titlemap.copy():
             tile = self.titlemap[loc]
             if (tile['type'], tile['variant']) in id_pair:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.title_size
                matches[-1]['pos'][1] *= self.title_size
                if not keep:
                    del self.titlemap[loc]
        return matches

    
    def Physics_rect_around(self, pos):
        rects = []
        for tile in self.Tile_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.title_size, tile['pos'][1] * self.title_size, self.title_size, self.title_size))
        return rects
    
    def solid_check(self, pos):
        tile_loc = str(int(pos[0]// self.title_size)) +';'+ str(int(pos[1]//self.title_size))
        if tile_loc in self.titlemap:
            if self.titlemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.titlemap[tile_loc]

    def render(self, surf, offset = (0,0)):
        for tile in self.offgrid_map:
            surf.blit(self.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1] ))
        
        for x in range(offset[0]//self.title_size, (offset[0] + surf.get_width()) // self.title_size + 1):
            for y in range(offset[1]//self.title_size, (offset[1] + surf.get_height()) // self.title_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.titlemap:
                    tile = self.titlemap[loc]
                    surf.blit(self.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.title_size - offset[0], tile['pos'][1] * self.title_size - offset[1]) )

        # for loc in self.titlemap:
        #     tile = self.titlemap[loc]
        #     surf.blit(self.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.title_size - offset[0], tile['pos'][1] * self.title_size - offset[1]) )

    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.titlemap, 'tile_size': self.title_size, 'offgrid': self.offgrid_map}, f)
        f.close()
    
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.titlemap = map_data['tilemap']
        self.title_size = map_data['tile_size']
        self.offgrid_map = map_data['offgrid']
    
    def AutoTile(self):
        for loc in self.titlemap:
            tile = self.titlemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.titlemap:
                    if self.titlemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            
            neighbors = tuple(sorted(neighbors))
            if tile['type'] in AUTO_TILES and neighbors in AUTO_MAP:
                tile['variant'] = AUTO_MAP[neighbors]



