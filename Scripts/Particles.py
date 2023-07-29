class Particles:
    def __init__(self, assets, p_ytpe, pos, velocity = [0,0], frame = 0):
        self.assets = assets
        self.type = p_ytpe
        self.pos = list(pos)
        self.Vel = list(velocity)
        self.animation = self.assets['Particles' + '/' + self.type].copy()
        self.animation.frame = frame
    def update(self):
        kill = False
        if self.animation.done:
            kill = True

        self.pos[0] += self.Vel[0]
        self.pos[1] += self.Vel[1]

        self.animation.update()

        return kill
    def render(self, surf, offset = (0,0)):
        img = self.animation.IMG()
        surf.blit(img ,(self.pos[0] - offset[0] - img.get_width()// 2, self.pos[1] - offset[1] - img.get_height()// 2))

class Blood(Particles):
    def __init__(self, assets, p_ytpe, pos, velocity, frame):
        super().__init__(assets, p_ytpe, pos, velocity, frame)

