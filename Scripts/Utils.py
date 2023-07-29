import pygame
import os

Base_IMG_PATH = 'data/images/'

def Load_IMG(path):
    img = pygame.image.load(Base_IMG_PATH + path).convert()
    img.set_colorkey('black')
    return img

def Load_IMGS(path):
    images = []
    for img_name in sorted(os.listdir(Base_IMG_PATH + path)):
        images.append( Load_IMG(path + '/' + img_name) )
    return images

def Sprite_sheet_IMGS(path, pos, width, height, offset, frames):
    images = []
    sheet = pygame.image.load(Base_IMG_PATH + path).convert()
    for i in range(frames):
        surf = pygame.Surface((width, height)).convert()
        surf.blit(sheet, (0,0), (pos[0] + offset * i, pos[1], width, height))
        surf.set_colorkey('black')
        images.append(surf)
    return images
    


class Animation():
    def __init__(self, imgs,  dur = 5, loop = True):
        self.imgs = imgs
        self.Dur = dur
        self.Loop= loop
        self.done = False
        self.frame = 0
    
    def copy(self):
        return Animation(self.imgs, self.Dur, self.Loop)
    
    def update(self):
        if self.Loop:
            self.frame = (self.frame + 1) % (self.Dur * len(self.imgs))
        else:
            self.frame = min(self.frame + 1, self.Dur * len(self.imgs) - 1)
            if self.frame >= self.Dur * len(self.imgs) - 1:
                self.done = True

    def IMG(self):
        return self.imgs[int(self.frame/ self.Dur)]