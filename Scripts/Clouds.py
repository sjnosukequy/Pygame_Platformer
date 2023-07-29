import random

class Cloud():
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos[0] += self.speed

    def render(self, surf, offset):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        surf.blit(self.img, (render_pos[0] % ( surf.get_width() + self.img.get_width() ) -self.img.get_width(), render_pos[1] % ( surf.get_height() + self.img.get_height() ) -self.img.get_height()))

class Clouds():
    def __init__(self, imgs, count = 16):
        self.cloud = []
        for i in range(count):
            self.cloud.append(Cloud((random.random() * 9999, random.random() * 9999), random.choice(imgs), random.random()*0.05 + 0.2, random.random()* 0.4 + 0.2))
        
        self.cloud.sort(key= lambda x: x.depth)

    def update(self):
        for cloud in self.cloud:
            cloud.update()
    
    def render(self, surf, offset = (0,0)):
        for clound in self.cloud:
            clound.render(surf, offset)
        