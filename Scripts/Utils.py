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