import pygame
from pygame.locals import *
import random
import os

class Bullet(pygame.sprite.Sprite):
    img_src = None

    def __init__(self, x, y):
        super().__init__()
        if Bullet.img_src is None:
            Bullet.img_src = pygame.image.load("챕터09_게임프로그래밍/present-gift-box-reward-full.png").convert_alpha()
            w, h = Bullet.img_src.get_size()
            Bullet.img_src = pygame.transform.scale(Bullet.img_src, (w // 10, h // 10))
        self.image = Bullet.img_src
        self.vx = 20.0  # 총알 속도
        self.vy = 0.0
        self.x = x
        self.y = y
        self.angle = 0.0
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        self.angle -= 20.0
        self.image = pygame.transform.rotate(Bullet.img_src, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Obstacle(pygame.sprite.Sprite):
    img_src = None

    def __init__(self, x, y, vx=0.0, vy=0.0, av=0.0, scale=1):
        super().__init__()
        if Obstacle.img_src is None:
            Obstacle.img_src = pygame.image.load("챕터09_게임프로그래밍/wintertileset/png/Object/IceBox.png").convert_alpha()
            w, h = Obstacle.img_src.get_size()
            Obstacle.img_src = pygame.transform.scale(Obstacle.img_src, (w // scale, h // scale))
        self.image = Obstacle.img_src
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.av = av  # 각 속도 (angular velocity)
        self.angle = 0.0
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        self.angle -= self.av
        self.image = pygame.transform.rotate(Obstacle.img_src, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Candy(pygame.sprite.Sprite):
    img_src = []

    def __init__(self, x, y, vx=0.0, vy=0.0, av=0.0, scale=1):
        super().__init__()
        if not Candy.img_src:
            self.load_candy_images()
        self.image = random.choice(Candy.img_src)
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.av = av  # 각 속도 (angular velocity)
        self.angle = 0.0
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def load_candy_images(self):
        candy_folder = "챕터09_게임프로그래밍/yaycandies/size1/"
        for file_name in os.listdir(candy_folder):
            if file_name.endswith(".png"):
                img_path = os.path.join(candy_folder, file_name)
                img = pygame.image.load(img_path).convert_alpha()
                Candy.img_src.append(img)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        self.angle -= self.av
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Santa(pygame.sprite.Sprite):
    img_src = []

    def __init__(self, x, y):
        super().__init__()
        if not Santa.img_src:
            for i in range(1, 12):
                img = pygame.image.load(f"챕터09_게임프로그래밍/santasprites/png/Run ({i}).png")
                img = img.convert_alpha()
                w, h = img.get_size()
                img = pygame.transform.scale(img, (w // 4, h // 4))
                img = img.subsurface((25, 0, 130, 140))
                Santa.img_src.append(img)
        self.image = Santa.img_src[0]
        self.santa_vx = x
        self.santa_vy = 0.0
        self.santa_sprites_id = 0
        self.santa_rect = self.image.get_rect().move(x, y)
        # 산타 피격 범위 / collid_santa 사각형을 산타 이미지의 중앙에 배치.
        self.collid_santa = pygame.Rect(
            x, y, 
            self.santa_rect.width - 75, 
            self.santa_rect.height
        )
        self.dt = 1.0 / 30.0  # 시간 간격 (게임에서는 가급적 생략)
        self.gravity = 1000  # 중력 가속도 (적당한 숫자로 조절)
        
    def update(self):
        self.santa_sprites_id += 0.3
        self.santa_sprites_id %= len(Santa.img_src)
        self.image = Santa.img_src[int(self.santa_sprites_id)]
        self.santa_vy += self.gravity * self.dt  # 속도 증가 = 가속도 * 시간 간격
        self.santa_rect.y += self.santa_vy * self.dt  # 위치 이동 = 속도 * 시간 간격
        self.collid_santa.center = self.santa_rect.center  # 충돌 감지 사각형 위치 업데이트

        # 바닥 충돌 반응
        if self.santa_vy > 0 and self.santa_rect.bottom > ground_y:
            self.santa_vy = 0  # 낙하 중지
            self.santa_rect.bottom = ground_y
            self.collid_santa.bottom = ground_y

    def jump(self):
        self.santa_vy -= 800

    def draw_rect(self):
        screen.blit(self.image, self.santa_rect)


pygame.init()

screen = pygame.display.set_mode((1024, 768))  # 윈도우 크기
clock = pygame.time.Clock()

# 배경 이미지
background = pygame.image.load("챕터09_게임프로그래밍/wintertileset/png/BG/BG.png").convert()
bgx = 0

# 타일 이미지
tile2 = pygame.image.load("챕터09_게임프로그래밍/wintertileset/png/Tiles/2.png").convert_alpha()
tile2 = pygame.transform.scale(tile2, (64, 64))  # 적당한 크기로 조정
tile5 = pygame.image.load("챕터09_게임프로그래밍/wintertileset/png/Tiles/5.png").convert_alpha()
tile5 = pygame.transform.scale(tile5, (64, 64))
gx = 0

# santa sprites
santa = Santa(240, 440)
santa_dead_sprites = []

for i in range(1, 18):
    dead_img = pygame.image.load(f"챕터09_게임프로그래밍/santasprites/png/Dead ({i}).png")
    dead_img = dead_img.convert_alpha()
    w, h = dead_img.get_size()
    dead_img = pygame.transform.scale(dead_img, (w // 4, h // 4))
    santa_dead_sprites.append(dead_img)

santa_dead_sprites_id = 0

bullet_group = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
candies = pygame.sprite.Group()

ground_y = 580  # 바닥 위치

# Game Over or Cleared
game_point = pygame.font.SysFont("system", 55)
point = 0
MAX_POINT = 50
game_font = pygame.font.SysFont("system", 180)
gametext = game_font.render("", 1, (0, 0, 0))

running = True
game_over = False

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
            running = False
        elif event.type == KEYUP and event.key == K_LCTRL and not game_over:
            bullet_group.add(Bullet(santa.santa_rect.right, santa.santa_rect.centery))

        elif event.type == KEYUP and event.key == K_SPACE and not game_over:
            santa.jump()

    if not game_over:
        """업데이트"""
        # 배경 및 산타 업데이트
        bgx += 1
        bgx %= background.get_width()

        gx += 5
        gx %= tile2.get_width()

        santa.update()

        # 장애물 및 총알 업데이트
        bullet_group.update()
        obstacles.update()
        candies.update()

        # 장애물 확률.
        rand = random.random()
        if  rand > 0.985:  # 프레임당 2%의 확률로 장애물 생성
            obstacles.add(Obstacle(1000, 530, vx=-5))
        # 캔디 확률
        # rand -> 0.9501 ~ 0.9999 - 0.95
        # => 0.0001 ~ 0.0499 * 10000 => int(1.xx ~ 499.xx) % 100 -> 1 ~ 99
        if rand > 0.95:
            candy_y = int((rand - 0.95) * 10000) % 200 + 250
            candies.add(Candy(1000, candy_y, vx=-5))

        if point >= MAX_POINT:
            gametext = game_font.render("Cleared", 1, (0, 0, 255))
            game_over = True

        for c in candies.copy():
            if c.rect.right < 0:
                candies.remove(c)

            elif c.rect.colliderect(santa.santa_rect):
                point += 1
                candies.remove(c)

        for o in obstacles.copy():  # copy 주의
            if o.rect.right < 0:
                obstacles.remove(o)

            elif o.rect.colliderect(santa.collid_santa):
                gametext = game_font.render("Game Over", 1, (255, 0, 0))
                game_over = True

            for b in bullet_group.copy():  # copy 주의
                if b.rect.left > 1024:
                    bullet_group.remove(b)

                elif o.rect.colliderect(b.rect):
                    obstacles.remove(o)
                    bullet_group.remove(b)
    # game over
    else:
        santa_dead_sprites_id += 0.3
        if santa_dead_sprites_id >= len(santa_dead_sprites):
            santa_dead_sprites_id = len(santa_dead_sprites) - 1

    """화면에 그리기"""
    screen.fill((255, 255, 255))
    # 배경 그리기
    screen.blit(background, dest=(-bgx, 0))
    screen.blit(background, dest=(-bgx + background.get_width(), 0))

    # 바닥 타일 그리기
    for i in range(-1, 17):
        screen.blit(tile2, (-gx + i * 64, 64 * 9))
        screen.blit(tile5, (-gx + i * 64, 64 * 10))
        screen.blit(tile5, (-gx + i * 64, 64 * 11))

    # 상자, 장애물 그리기
    bullet_group.draw(screen)
    obstacles.draw(screen)
    candies.draw(screen)
    
    # 산타 그리기
    if not game_over:
        santa.draw_rect()
    else:
        if point >= MAX_POINT:
            santa.draw_rect()
        else:
            screen.blit(santa_dead_sprites[int(santa_dead_sprites_id)], santa.santa_rect)

    # 게임폰트 그리기
    point_text = game_point.render(f"point = {point}", 1, (120, 120, 120))
    screen.blit(point_text, (750, 10))
    if game_over:
        screen.blit(gametext, (200, int(screen.get_height() / 2 - 90)))

    pygame.display.flip()
    clock.tick(40)

pygame.quit()
