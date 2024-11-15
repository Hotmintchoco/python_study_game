import pygame
from pygame import mixer

GROUND_SPEED = 7.5

class MoveObject(pygame.sprite.Sprite):
    def __init__(self, x, y, vx=0.0, vy=0.0, ds=0.0):
        super().__init__()
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ds = ds  # 스프라이트 변화 속도
        self.sprites = self.init_sprites()
        self.sprite_id = 0
        self.image = self.sprites[int(self.sprite_id)]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def init_sprites(self):
        raise NotImplementedError("init_sprites() not implemented")
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        self.sprite_id += self.ds
        self.sprite_id %= len(self.sprites)

        self.image = self.sprites[int(self.sprite_id)]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def draw_rect(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

class Ground:
    def __init__(self):
        super().__init__()
        self.tile = self.load("background_tile/png/Tile/2.png")
        self.x = 0

    def load(self, filename):
        s = pygame.image.load(filename).convert_alpha()
        s = pygame.transform.scale(s, (64, 64))
        return s

    def draw(self, screen, bgx):
        for i in range(-1, 17):
            screen.blit(self.tile, (i * 64 - bgx % 64, 64 * 11))

pygame.init()
mixer.init()
# https://freesound.org/people/MusicByMisterbates/sounds/608811/
mixer.music.load("608811__musicbymisterbates__uplifting-dramatic-soundtrack-war-around-us.mp3")
mixer.music.set_volume(0.2)
screen = pygame.display.set_mode((1024, 768))  # 윈도우 크기
background = pygame.image.load("background_tile/png/BG.png").convert_alpha()
clock = pygame.time.Clock()
quit = False

while True:
    running = True
    bgx = 0  # background x
    ground = Ground()
    mixer.music.play(-1)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                running = False

        """업데이트"""
        point = pygame.mouse.get_pos()

        if point[0] > 1019 and bgx < 249:
            bgx += GROUND_SPEED
        elif point[0] < 5 and bgx > 0:
            bgx -= GROUND_SPEED

        """화면에 그리기"""
        screen.fill((255, 255, 255))
        screen.blit(background, dest=(-bgx, 0))
        ground.draw(screen, bgx)

        pygame.display.flip()
        clock.tick(30)
    if quit:
        break
pygame.quit()
