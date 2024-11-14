import pygame
import random
from PIL import Image
from pygame.locals import *
from pygame import mixer
GROUND_SPEED = 10.0


class MovingObject(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0.0, vx=0.0, vy=0.0, av=0.0, ds=0.0):
        super().__init__()
        self.x = x
        self.y = y
        self.angle = angle  # 회전
        self.vx = vx
        self.vy = vy
        self.av = av  # angular velocity (각속도)
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
        self.angle += self.av
        self.rect.center = (self.x, self.y)
        self.sprite_id += self.ds
        self.sprite_id %= len(self.sprites)
        if self.angle != 0:
            self.image = pygame.transform.rotate(
                self.sprites[int(self.sprite_id)], self.angle
            )
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.image = self.sprites[int(self.sprite_id)]
            self.rect = self.image.get_rect()
            self.rect.center = (self.x, self.y)
    def draw_rect(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


class Bullet(MovingObject):
    source_sprites = []
    def __init__(self, x, y, **argx):
        super().__init__(x, y, vx=20.0, av=-20.0, **argx)
    def init_sprites(self):
        if not Bullet.source_sprites:
            img = pygame.image.load("챕터09_게임프로그래밍/present-gift-box-reward-full.png").convert_alpha()
            w, h = img.get_size()
            img = pygame.transform.scale(img, (w // 10, h // 10))
            Bullet.source_sprites = [img]
        return Bullet.source_sprites


class Item(MovingObject):
    source_sprites = []
    IMAGE_FILENAMES = [
        "챕터09_게임프로그래밍/yaycandies/size1/bean_blue.png",
        "챕터09_게임프로그래밍/yaycandies/size1/candycane.png",
        "챕터09_게임프로그래밍/yaycandies/size1/bean_green.png",
        "챕터09_게임프로그래밍/yaycandies/size1/bean_orange.png",
        "챕터09_게임프로그래밍/yaycandies/size1/candycorn.png",
        "챕터09_게임프로그래밍/yaycandies/size1/jelly_green.png",
        "챕터09_게임프로그래밍/yaycandies/size1/jelly_orange.png",
        "챕터09_게임프로그래밍/yaycandies/size1/candyhumbug.png",
        "챕터09_게임프로그래밍/yaycandies/size1/jellybig_yellow.png",
        "챕터09_게임프로그래밍/yaycandies/size1/lollipop_blue.png",
        "챕터09_게임프로그래밍/yaycandies/size1/lollipop_pink.png",
        "챕터09_게임프로그래밍/yaycandies/size1/swirl_red.png",
        "챕터09_게임프로그래밍/yaycandies/size1/wrappedsolid_purple.png",
        "챕터09_게임프로그래밍/yaycandies/size1/wrappedsolid_green.png",
        "챕터09_게임프로그래밍/yaycandies/size1/wrappedtrans_yellow.png",
    ]
    def __init__(self, x, y):
        super().__init__(x, y, vx=-GROUND_SPEED)
    def init_sprites(self):
        if not Item.source_sprites:
            for f in Item.IMAGE_FILENAMES:
                i = pygame.image.load(f).convert_alpha()
                Item.source_sprites.append(i)
        return [random.choice(Item.source_sprites)]


class Obstacle(MovingObject):
    source_sprites = []
    def __init__(self, x, y):
        super().__init__(x, y, vx=-GROUND_SPEED)
    def init_sprites(self):
        if not Obstacle.source_sprites:
            Obstacle.source_sprites = [
                pygame.image.load(
                    "챕터09_게임프로그래밍/wintertileset/png/Object/IceBox.png",
                ).convert_alpha()
            ]
        return Obstacle.source_sprites


class Explosion(MovingObject):
    source_sprites = []
    def __init__(self, x, y, vx=-GROUND_SPEED):
        super().__init__(x, y, ds=1.0)
        self.count = 0
    def init_sprites(self):
        if not Explosion.source_sprites:
            for i in range(1, 6):
                img = pygame.image.load(
                    f"챕터09_게임프로그래밍/yaycandies/size1_explosion/explosionred{str(i).zfill(2)}.png"
                ).convert_alpha()
                w, h = img.get_size()
                img = pygame.transform.scale(img, (w, h))
                Explosion.source_sprites.append(img)
        return Explosion.source_sprites
    def update(self):
        super().update()
        self.count += 1


class Player(MovingObject):
    source_sprites = []
    def __init__(self):
        super().__init__(240, 520, ds=1.0)
    def init_sprites(self):
        if not Player.source_sprites:
            for i in range(1, 12):
                img = pygame.image.load(
                    f"챕터09_게임프로그래밍/santasprites/png/Run ({i}).png"
                ).convert_alpha()
                w, h = img.get_size()
                img = pygame.transform.scale(img, (w // 4, h // 4))
                rect = img.get_rect()
                rect.width = 140
                img = img.subsurface(rect)  # 이미지 여백이 너무 커서 축소
                Player.source_sprites.append(img)
        return Player.source_sprites
    def update(self):
        self.vy += 0.8  # 중력
        super().update()
        # ground collision
        if self.y >= 520 and self.vy > 0.0:
            self.y = 520
            self.vy = 0.0
    def jump(self):
        self.vy = -15  # screen space


class Ground:
    def __init__(self):
        super().__init__()
        self.sprites = [
            self.load(f"챕터09_게임프로그래밍/wintertileset/png/Tiles/{i}.png", 2) for i in range(1, 19)
        ]
        self.x = 0
    def load(self, filename, scale):
        s = pygame.image.load(filename).convert_alpha()
        w, h = s.get_size()
        s = pygame.transform.scale(s, (w // scale, h // scale))
        return s
    def draw(self, screen):
        for i in range(-1, 16):
            screen.blit(self.sprites[1], (self.x + i * 64, 64 * 9))
            screen.blit(self.sprites[4], (self.x + i * 64, 64 * 10))
            screen.blit(self.sprites[4], (self.x + i * 64, 64 * 11))
    def update(self):
        self.x -= GROUND_SPEED
        self.x %= 64


pygame.init()
screen = pygame.display.set_mode((1024, 768))  # 윈도우 크기
background = pygame.image.load("챕터09_게임프로그래밍/wintertileset/png/BG/BG.png").convert_alpha()
mixer.init()
mixer.music.load("챕터09_게임프로그래밍/jingle-bells-violin-loop-8645.mp3")
mixer.music.set_volume(0.1)
title_snd = mixer.Sound(
    "챕터09_게임프로그래밍/454786__carloscarty__silent-night-intro-pan-flute-glissando.wav"
)
# https://freesound.org/people/sounds-mp3/sounds/551326/
hoho_snd = mixer.Sound("챕터09_게임프로그래밍/551326__sounds-mp3__santa-claus-laughing.mp3")
item_snd = mixer.Sound("챕터09_게임프로그래밍/676402__cjspellsfish__score-2.mp3")
item_snd.set_volume(0.5)
break_snd = mixer.Sound("챕터09_게임프로그래밍/422669__lynx_5969__ice-break-with-hand.wav")
die_snd = mixer.Sound("챕터09_게임프로그래밍/186876__soundmatch24__dead-walking.mp3")
clear_snd = mixer.Sound("챕터09_게임프로그래밍/270402__littlerobotsoundfactory__jingle_win_00.wav")
scorefont = pygame.font.SysFont("system", 48)
titlefont = pygame.font.SysFont("system", 200)
clock = pygame.time.Clock()
quit = False
while True:
    running = True
    bgx = 0
    draw_rect = False
    score = 0
    pygame.event.clear()
    santa = Player()
    ground = Ground()
    """ 시작 메뉴 보여주기 """
    title_text = titlefont.render("Santa Run!", 1, (255, 255, 255))
    comment_text = scorefont.render(
        "Press any key to play",
        1,
        (255, 255, 255),
    )
    show_title = True
    frame_count = 0
    while show_title:
        for event in pygame.event.get():
            if event.type == KEYUP:
                show_title = False
        title_snd.set_volume(0.1)
        title_snd.play()
        screen.blit(background, (bgx, 0))
        ground.draw(screen)
        screen_width, screen_height = screen.get_size()
        screen.blit(
            title_text,
            title_text.get_rect(center=(screen_width / 2, screen_height / 2 - 50)),
        )
        # 글자가 깜빡거리는 효과
        if frame_count // 15 % 2 == 0:
            screen.blit(
                comment_text,
                comment_text.get_rect(
                    center=(screen_width / 2, screen_height / 2 + 100)
                ),
            )
        pygame.display.flip()
        clock.tick(30)
        frame_count += 1
    title_snd.stop()
    """ 게임 """
    items = pygame.sprite.Group()  # Candy
    bullets = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    moving_sprites = pygame.sprite.Group()
    moving_sprites.add(santa)
    mixer.music.play()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                running = False
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    # hoho_snd.play(maxtime=2200)
                    santa.jump()
                elif event.key == K_LCTRL:
                    new_bullet = Bullet(santa.x - 20, santa.y)
                    bullets.add(new_bullet)
        ground.update()
        moving_sprites.update()
        items.update()
        obstacles.update()
        bullets.update()
        explosions.update()
        if random.random() > 0.92:  # 아이템 생성
            new_item = Item(1024, random.randint(150, 450))
            items.add(new_item)
        if random.random() > 0.96:  # 장애물 생성
            new_obstacle = Obstacle(1024, 520)
            obstacles.add(new_obstacle)
        for i in items.copy():
            if santa.rect.colliderect(i.rect):  # 산타와 아이템 충돌
                score += 1
                item_snd.play()
                items.remove(i)
            elif i.rect.right < 0:  # 화면을 벗어난 아이템 삭제
                items.remove(i)
        for e in explosions.copy():
            if e.count >= 5:
                explosions.remove(e)
        for b in bullets.copy():
            if b.rect.left > 1024:
                bullets.remove(b)
        for b in bullets.copy():
            for o in obstacles.copy():
                if b.rect.colliderect(o.rect):
                    score += 1
                    break_snd.play()
                    exp = Explosion(b.x + 50, b.y)
                    explosions.add(exp)
                    bullets.remove(b)
                    obstacles.remove(o)
        # Rendering
        screen.blit(background, (bgx, 0))
        screen.blit(background, (bgx - background.get_width(), 0))
        bgx -= 0.01
        bgx %= background.get_width()
        ground.draw(screen)
        moving_sprites.draw(screen)
        items.draw(screen)
        obstacles.draw(screen)
        bullets.draw(screen)
        explosions.draw(screen)
        if draw_rect:
            santa.draw_rect(screen)
            for i in items:
                i.draw_rect(screen)
            for i in bullets:
                i.draw_rect(screen)
        scoretext = scorefont.render("Score: " + str(score), 1, (255, 255, 255))
        screen.blit(scoretext, (700, 10))
        # 게임 종료 조건
        if score >= 100:  # 클리어
            mixer.music.stop()
            clear_snd.play()
            clear_text = titlefont.render("Cleared!", 1, (255, 255, 255))
            screen.blit(clear_text, (220, 220))
            pygame.display.flip()
            pygame.time.wait(int(clear_snd.get_length() * 1000))
            running = False
        else:  # 장애물에 부딪혀서 사망
            for o in obstacles.copy():
                if santa.rect.colliderect(o.rect):  # 산타와 장애물 충돌
                    mixer.music.stop()
                    die_snd.play()
                    gameover_text = titlefont.render("Game Over", 1, (255, 0, 0))
                    screen.blit(gameover_text, (120, 320))
                    pygame.display.flip()
                    pygame.time.wait(int(die_snd.get_length() * 1000))
                    running = False
                    break
        pygame.display.flip()
        clock.tick(30)
    if quit:
        break


pygame.quit()