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
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)

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

# 배경 이미지
background = pygame.image.load("챕터09_게임프로그래밍/wintertileset/png/BG/BG.png").convert()
bgx = 0

# 타일 이미지
tile2 = pygame.image.load("챕터09_게임프로그래밍/wintertileset/png/Tiles/2.png").convert_alpha()
tile2 = pygame.transform.scale(tile2, (64, 64)) # 적당한 크기로 조정
tile5 = pygame.image.load("챕터09_게임프로그래밍/wintertileset/png/Tiles/5.png").convert_alpha()
tile5 = pygame.transform.scale(tile5, (64, 64))
gx = 0

# santa sprites
santa_sprites = []

for i in range(1, 12):
    img = pygame.image.load(f"챕터09_게임프로그래밍/santasprites/png/Run ({i}).png")
    img = img.convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (w // 4, h // 4))
    img = img.subsurface((25,0,130,140))
    santa_sprites.append(img)

santa_sprites_id = 0

bullet_group = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

# 산타 점프 변수
santa_vy = 0.0 # y 방향 속도
dt = 1.0 / 30.0 # 시간 간격 (게임에서는 가급적 생략)
gravity = 1000 # 중력 가속도 (적당한 숫자로 조절)

ground_y = 580 # 바닥 위치

running = True

santa_rect = img.get_rect().move(240, 440)
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
            running = False
        elif event.type == KEYUP and event.key == K_LCTRL:
            print(santa_rect.right)
            bullet_group.add(Bullet(santa_rect.right, santa_rect.centery))

        elif event.type == KEYUP and event.key == K_SPACE:
            santa_vy -= 800

    """업데이트"""
    # 배경 및 산타 업데이트
    bgx += 1
    bgx %= background.get_width()

    gx += 5
    gx %= tile2.get_width()

    santa_sprites_id += 0.3
    santa_sprites_id %= len(santa_sprites)

    # 산타 점프 update
    santa_vy += gravity * dt # 속도 증가 = 가속도 * 시간 간격
    santa_rect.y += santa_vy * dt # 위치 이동 = 속도 * 시간 간격

    # 바닥 충돌 반응
    if santa_vy > 0 and santa_rect.bottom > ground_y:
        santa_vy = 0 # 낙하 중지
        santa_rect.bottom = ground_y

    # 장애물 및 총알 업데이트
    bullet_group.update()
    obstacles.update()
    
    # 확률을 바꿔보세요.
    if random.random() > 0.98:  # 프레임당 2%의 확률로 장애물 생성
        obstacles.add(Obstacle(1000, 530, vx=-5))

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
    # 배경 그리기
    screen.blit(background, dest = (-bgx, 0))
    screen.blit(background, dest = (-bgx + background.get_width(), 0))

    # 바닥 타일 그리기
    for i in range(-1, 17):
        screen.blit(tile2,(-gx + i * 64, 64 * 9))
        screen.blit(tile5, (-gx + i * 64, 64 * 10))
        screen.blit(tile5, (-gx + i * 64, 64 * 11))
    
    # 산타 그리기
    screen.blit(santa_sprites[int(santa_sprites_id)], santa_rect)

    bullet_group.draw(screen)
    obstacles.draw(screen)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()