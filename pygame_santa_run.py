import pygame
from pygame.locals import *
import random

class Bullet(pygame.sprite.Sprite):
    img_src = None

    def __init__(self, x, y):
        super().__init__()
        if Bullet.img_src == None:
            Bullet.img_src = pygame.image.load("챕터09_게임프로그래밍/present-gift-box-reward-full.png").convert_alpha()
            w, h = Bullet.img_src.get_size()
            Bullet.img_src = pygame.transform.scale(Bullet.img_src, (w // 10, h // 10))
        self.image = Bullet.img_src # 첫 프레임은 회전이 없음
        self.vx = 20.0 # 총알 속도
        self.vy = 0.0
        self.x = x
        self.y = y
        self.angle = 0.0
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self):
        self.x += self.vx # dt 곱하기를 생략 (작은 속도값 사용)
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        self.angle -= 20.0
        self.image = pygame.transform.rotate(Bullet.img_src, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    # 디버깅용
    def draw_rect(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

class Obstacle(pygame.sprite.Sprite): # class Bullet과 비슷합니다.
    img_src = None

    def __init__(self, x, y, vx=0.0, vy=0.0, av=0.0, scale=1):
        super().__init__()
        if Obstacle.img_src == None:
            Obstacle.img_src = pygame.image.load("챕터09_게임프로그래밍/wintertileset/png/Object/IceBox.png").convert_alpha()
            w, h = Obstacle.img_src.get_size()
            Obstacle.img_src = pygame.transform.scale(Obstacle.img_src, (w // scale, h // scale))
        self.image = Obstacle.img_src # 첫 프레임은 회전이 없음
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.av = av # 각 속도 (angular velocity)
        self.angle = 0.0
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self):
        self.x += self.vx # dt 곱하기 생략
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        self.angle -= self.av
        self.image = pygame.transform.rotate(Obstacle.img_src, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


pygame.init()

screen = pygame.display.set_mode((1024, 768))  # 윈도우 크기
clock = pygame.time.Clock()

bullet_group = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

ground_y = 512 # 바닥 위치

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
            running = False
        elif event.type == KEYUP and event.key == K_LCTRL:
            bullet_group.add(Bullet(240, 400))

    """업데이트"""
    bullet_group.update()
    obstacles.update()
    
    # 확률을 바꿔보세요.
    if random.random() > 0.98:  # 프레임당 2%의 확률로 장애물 생성
        obstacles.add(Obstacle(1000, 480, vx=-5))

    for o in obstacles.copy(): # copy 주의
        if o.rect.right < 0:
            obstacles.remove(o)

        for b in bullet_group.copy(): # copy 주의
            if b.rect.left > 1024:
                bullet_group.remove(b)

            elif o.rect.colliderect(b.rect):
                obstacles.remove(o)
                bullet_group.remove(b)


    """화면에 그리기"""

    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, color=(128, 128, 128), rect=pygame.Rect(0, 64*8, 1024, 64*4))

    bullet_group.draw(screen)
    obstacles.draw(screen)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()