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
    
    def update(self, bgx):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        self.sprite_id += self.ds               
        self.sprite_id %= len(self.sprites)

        self.image = self.sprites[int(self.sprite_id)]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x - bgx, self.y)

    def draw_rect(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

class Unit(MoveObject):
    source_sprites = []
    def __init__(self, x, y):
        super().__init__(x, y, vx = 1, ds=0.1)
    def init_sprites(self):
        if not Unit.source_sprites:
            index = 0
            while True:
                try:
                    index += 1
                    img = pygame.image.load(
                        f"Unit/Skeleton_Spearman/Skeleton_Run({index}).png"
                    ).convert_alpha()
                    Unit.source_sprites.append(img)
                except:
                    return Unit.source_sprites
        return Unit.source_sprites
    def update(self, bgx):
        super().update(bgx)
        # ground collision
        if self.y >= 450 and self.vy > 0.0:
            self.y = 450
            self.vy = 0.0

class Menu:
    def __init__(self):
        super().__init__()
        self.menu = pygame.Rect(700, 0, 500, 150)
        self.unit_img = self.load("menu/unit.png")
        self.turret_img = self.load("menu/turret.png")
        self.turret_sell_img = self.load("menu/turret_sell.png")
        self.upgrade_img = self.load("menu/upgrade.png")
        self.gold_img = self.load("menu/gold.png")

        self.unit_img_rect = self.unit_img.get_rect(topleft=(725, 60))  # Unit image position
        self.turret_img_rect = self.turret_img.get_rect(topleft=(800, 60))
        self.turret_sell_img_rect = self.turret_sell_img.get_rect(topleft=(875, 60))
        self.upgrade_img_rect = self.upgrade_img.get_rect(topleft=(950, 60))

    def load(self, filename):
        s = pygame.image.load(filename).convert_alpha()
        s = pygame.transform.scale(s, (48, 48))
        return s

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 220, 115), self.menu)
        screen.blit(self.unit_img, self.unit_img_rect.topleft)
        screen.blit(self.turret_img, self.turret_img_rect.topleft)
        screen.blit(self.turret_sell_img, self.turret_sell_img_rect.topleft)
        screen.blit(self.upgrade_img, self.upgrade_img_rect.topleft)

    def handle_click(self, pos):
        if self.unit_img_rect.collidepoint(pos):
            return Unit(240, 680)
        elif self.turret_img_rect.collidepoint(pos):
            print("Turret clicked!")
            return None
        elif self.turret_sell_img_rect.collidepoint(pos):
            print("Turret Sell clicked!")
            return None
        elif self.upgrade_img_rect.collidepoint(pos):
            print("Upgrade clicked!")
            return None

class Gold:
    def __init__(self):
        super().__init__()
        self.gold_box = pygame.Rect(25, 10, 300, 100)
        self.gold_img = self.load("menu/gold.png")
        self.now = 200 
    def load(self, filename):
        s = pygame.image.load(filename).convert_alpha()
        return s
    
    def update(self, get_gold):
        self.now += get_gold

    def draw(self, font):
        pygame.draw.rect(screen, (134, 229, 127), self.gold_box)
        gold_text = font.render(str(self.now), True, (255, 255, 255)) # menu
        screen.blit(self.gold_img, (50, 30))
        screen.blit(gold_text, (200, 50))

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

class Tree:
    def __init__(self, x, y, flipped=False):
        super().__init__()
        self.img = self.load("background_tile/png/Objects/Tree.png")
        self.x = x
        self.y = y
        if flipped:
            self.img = pygame.transform.flip(self.img, True, False)

    def load(self, filename):
        s = pygame.image.load(filename).convert_alpha()
        return s

    def draw(self, screen, bgx):
        screen.blit(self.img, (self.x - bgx, self.y))

pygame.init()
mixer.init()
# https://freesound.org/people/MusicByMisterbates/sounds/608811/
mixer.music.load("608811__musicbymisterbates__uplifting-dramatic-soundtrack-war-around-us.mp3")
mixer.music.set_volume(0.2)
screen = pygame.display.set_mode((1024, 768))  # 윈도우 크기
menu_font = pygame.font.SysFont("system", 40) # menu 폰트
background = pygame.image.load("background_tile/png/BG.png").convert_alpha()
tree = Tree(-50, 450)
enemy_tree = Tree(screen.get_width() + 50, 450, flipped=True)
clock = pygame.time.Clock()
quit = False

while True:
    running = True
    bgx = 0  # background x
    ground = Ground()
    menu_bar = Menu()
    gold = Gold()
    unit_sprites = pygame.sprite.Group()
    menu_click = None
    mixer.music.play(-1)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button click
                menu_click = menu_bar.handle_click(event.pos)

        if type(menu_click) == Unit:
            unit_sprites.add(menu_click)
        """업데이트"""
        point = pygame.mouse.get_pos()
        lmousedown = pygame.mouse.get_pressed()[0]
        menu_text = menu_font.render("Menu", True, (128, 0, 0)) # menu

        if point[0] > 1019 and bgx < 249:
            bgx += GROUND_SPEED
        elif point[0] < 5 and bgx > 0:
            bgx -= GROUND_SPEED

        for unit in unit_sprites.copy():
            if unit.x > 1100:
                unit.vx = 0
        unit_sprites.update(bgx)

        """화면에 그리기"""
        screen.fill((255, 255, 255))
        screen.blit(background, dest=(-bgx, 0))
        ground.draw(screen, bgx)
        gold.draw(menu_font)
        menu_bar.draw(screen)
        screen.blit(menu_text, (725, 20))
        # 나의 나무
        tree.draw(screen, bgx)
        # 적의 나무
        enemy_tree.draw(screen, bgx)
        unit_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(30)
    if quit:
        break
pygame.quit()
