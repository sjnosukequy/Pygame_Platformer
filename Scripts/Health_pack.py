import pygame
class Health():
    def __init__(self, assets, pos, health):
        self.pos = list(pos)
        self.Health = health
        self.assets = assets
        self.animation = self.assets['Health'].copy()
        self.kill = False

    def update(self):
        self.animation.update()
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], 4, 4)
    
    def render(self, surf, offset = (0,0)):
        img = self.animation.IMG()
        surf.blit(img ,(self.pos[0] - offset[0] - img.get_width()// 2, self.pos[1] - offset[1] - img.get_height()// 2))