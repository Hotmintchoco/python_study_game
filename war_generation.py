import pygame
import random
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
        self.sprite_id += self.ds               
        self.sprite_id %= len(self.sprites)

        self.image = self.sprites[int(self.sprite_id)]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x - bgx, self.y)

class Unit(MoveObject):
    def __init__(self, x, y, img_file, flipped=False, is_shot=False,
                  unit_vx=1.5, unit_ds=0.1):
        self.img_file = img_file
        self.attack = False
        self.target = None
        self.is_dead = False
        self.target_tree = False
        self.is_shot = is_shot
        self.flipped = flipped
        self.hp = 50
        self.hp_divide = 1
        if self.hp > 50:
            self.hp_divide = self.hp / 50
        self.created_time = pygame.time.get_ticks()  # 생성 시각 추가
        self.run_sprites = self.init_sprites()
        self.attack_sprites = self.get_sprites()
        super().__init__(x, y, vx=unit_vx, ds=unit_ds)

    def init_sprites(self):
        if not self.run_sprites:
            index = 0
            while True:
                try:
                    index += 1
                    img = pygame.image.load(
                        f"{self.img_file}_Run({index}).png"
                    ).convert_alpha()
                    if self.flipped:
                        img = pygame.transform.flip(img, True, False)
                    self.run_sprites.append(img)
                except:
                    break                
        return self.run_sprites
        
    def get_sprites(self):
        if not self.attack_sprites:
            index = 0
            while True:
                try:
                    index += 1
                    img = pygame.image.load(
                        f"{self.img_file}_attack({index}).png"
                    ).convert_alpha()
                    if self.flipped:
                        img = pygame.transform.flip(img, True, False)
                    self.attack_sprites.append(img)
                except:
                    break
        return self.attack_sprites
    
    def update(self, bgx):
        if self.attack:
            self.sprites = self.attack_sprites
        else:
            self.sprites = self.run_sprites
        super().update(bgx)
        self.hp_bar = pygame.Rect(self.x-25-bgx, self.y-40, self.hp // self.hp_divide, 5)
    
    def fight_motion(self, target):
        self.vx = 0
        self.attack = True
        if 3 < self.sprite_id < 3.1:
            target.hp -= self.damage
            print(target.hp)

    def fighting(self, enemy):
        if self.rect.colliderect(enemy.rect) and not self.is_shot and enemy.hp > 0:
            self.target = enemy
            self.fight_motion(enemy)
        if self.target:
            if self.target.hp <= 0 and not self.flipped:
                self.attack = False
                self.target = None
            elif self.target.hp <= 0 and self.flipped:
                self.attack = False
                self.target = None
    
    def attack_tree(self, tree):
        if self.rect.colliderect(tree.collide_rect) and not self.is_shot and not self.target:
            self.target_tree = True
            self.fight_motion(tree)

    def shot_motion(self, shot_complition):
        self.vx = 0
        self.attack = True
        if 12.01 < self.sprite_id < 12.2 and not shot_complition:
            new_arrow = Arrow(unit.x-5, unit.y-10)
            arrows.add(new_arrow)
            print(unit.sprite_id)

    def shot_tree(self, tree, shot_complition):
        if self.is_shot and self.x + 250 > tree.x and not self.target:
            self.target_tree = True
            self.shot_motion(shot_complition)

    def shot_arrow(self, enemy, shot_complition):
        if self.is_shot and self.x + 200 > enemy.x and enemy.hp > 0:
            self.target = enemy
            self.shot_motion(shot_complition)
            
        return True
        

    def unit_hp_draw(self, pos):
        if self.rect.collidepoint(pos):
            pygame.draw.rect(screen, (255, 0, 0), self.hp_bar)

class Dead_Skeleton(MoveObject):
    def __init__(self, unit):
        self.x = unit.x
        self.y = unit.y
        self.flipped = unit.flipped
        self.img_file = unit.img_file
        super().__init__(self.x, self.y, ds=0.2)
    
    def init_sprites(self):
        self.sprites = []
        index = 0
        while True:
            try:
                index += 1
                img = pygame.image.load(
                    f"{self.img_file}_Dead({index}).png"
                ).convert_alpha()
                if self.flipped:
                    img = pygame.transform.flip(img, True, False)
                self.sprites.append(img)
            except:
                break                
        return self.sprites
         
class Skeleton_Warrior(Unit):
    run_sprites = []
    attack_sprites = []

    def __init__(self, x, y, img_file="Unit/Skeleton_Warrior/Skeleton"):
        if Skeleton_Warrior.run_sprites:
            self.run_sprites = Skeleton_Warrior.run_sprites

        if Skeleton_Warrior.attack_sprites:
            self.attack_sprites = Skeleton_Warrior.attack_sprites
        super().__init__(x, y, img_file)
        self.damage = 10

class Skeleton_Archer(Unit):
    run_sprites = []
    attack_sprites = []

    def __init__(self, x, y, img_file="Unit/Skeleton_Archer/Skeleton"):
        if Skeleton_Archer.run_sprites:
            self.run_sprites = Skeleton_Archer.run_sprites

        if Skeleton_Archer.attack_sprites:
            self.attack_sprites = Skeleton_Archer.attack_sprites
        super().__init__(x, y, img_file, is_shot=True)
        self.shot_complition = False
        self.ds = 0.19

class Skeleton_Spear(Unit):
    run_sprites = []
    attack_sprites = []

    def __init__(self, x, y, img_file="Unit/Skeleton_Spearman/Skeleton"):
        if Skeleton_Spear.run_sprites:
            self.run_sprites = Skeleton_Spear.run_sprites

        if Skeleton_Spear.attack_sprites:
            self.attack_sprites = Skeleton_Spear.attack_sprites
        super().__init__(x, y, img_file)
        self.damage = 25

class Enemy_Skeleton_Warrior(Unit):
    run_sprites = []
    attack_sprites = []

    def __init__(self, x, y, img_file="Unit/Skeleton_Warrior/Skeleton"):
        if Enemy_Skeleton_Warrior.run_sprites:
            self.run_sprites = Enemy_Skeleton_Warrior.run_sprites

        if Enemy_Skeleton_Warrior.attack_sprites:
            self.attack_sprites = Enemy_Skeleton_Warrior.attack_sprites
        super().__init__(x, y, img_file, flipped=True, unit_vx=-1.5)
        self.damage = 10

class Arrow(MoveObject):
    source_sprites = []
    def __init__(self, x, y, **argx):
        super().__init__(x, y, vx=10.0, **argx)
        self.damage = 25
    def init_sprites(self):
        if not Arrow.source_sprites:
            img = pygame.image.load("Unit/Skeleton_Archer/Arrow.png").convert_alpha()
            Arrow.source_sprites = [img]
        return Arrow.source_sprites
    
class Menu:
    def __init__(self):
        super().__init__()
        self.menu = pygame.Rect(700, 0, 500, 150)
        self.main_menu()
        self.unit_menu = False

        self.first_img_rect = self.first_img.get_rect(topleft=(725, 60))  # Unit image position
        self.second_img_rect = self.second_img.get_rect(topleft=(800, 60))
        self.third_img_rect = self.third_img.get_rect(topleft=(875, 60))
        self.forth_img_rect = self.forth_img.get_rect(topleft=(950, 60))

        self.unit_price = 25
        self.menu_font = pygame.font.SysFont("system", 45)
        self.menu_text = menu_font.render(f"Unit_Price = {self.unit_price}", 1, (125, 125, 125))

    def load(self, filename):
        s = pygame.image.load(filename).convert_alpha()
        s = pygame.transform.scale(s, (48, 48))
        return s
    
    def update(self):
        self.menu_text = menu_font.render(f"Unit_Price = {self.unit_price}", 1, (125, 125, 125))

    # 메인 메뉴의 이미지들
    def main_menu(self):
        self.first_img = self.load("menu/unit.png")
        self.second_img = self.load("menu/turret.png")
        self.third_img = self.load("menu/turret_sell.png")
        self.forth_img = self.load("menu/upgrade.png")
        self.gold_img = self.load("menu/gold.png")

    def unit_click(self):
        self.first_img = self.load("menu/Skeleton_Warrior.png")
        self.second_img = self.load("menu/Skeleton_Archer.png")
        self.third_img = self.load("menu/Skeleton_Spear.png")
        self.forth_img = self.load("menu/Return.png")

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 220, 115), self.menu)
        screen.blit(self.first_img, self.first_img_rect.topleft)
        screen.blit(self.second_img, self.second_img_rect.topleft)
        screen.blit(self.third_img, self.third_img_rect.topleft)
        screen.blit(self.forth_img, self.forth_img_rect.topleft)

    def point_for_menu(self, pos):
        if self.unit_menu:
            if self.first_img_rect.collidepoint(pos):
                self.unit_price = 25
                screen.blit(self.menu_text, (350, 75))
            elif self.second_img_rect.collidepoint(pos):
                self.unit_price = 50
                screen.blit(self.menu_text, (350, 75))
            elif self.third_img_rect.collidepoint(pos):
                self.unit_price = 150
                screen.blit(self.menu_text, (350, 75))

    def handle_click(self, pos):
        if self.first_img_rect.collidepoint(pos):
            if self.unit_menu and Gold.now >= self.unit_price:
                Gold.now -= self.unit_price
                return Skeleton_Warrior(240, 680)
            self.unit_menu = True
            self.unit_click()
            return None
        elif self.second_img_rect.collidepoint(pos):
            if self.unit_menu and Gold.now >= self.unit_price:
                Gold.now -= self.unit_price
                return Skeleton_Archer(240, 675)
            return None
        elif self.third_img_rect.collidepoint(pos):
            if self.unit_menu and Gold.now >= self.unit_price:
                Gold.now -= self.unit_price
                return Skeleton_Spear(240, 680)
            return None
        elif self.forth_img_rect.collidepoint(pos):
            if self.unit_menu:
                self.main_menu()
                self.unit_menu = False
            return None

class Gold:
    now = 10000
    def __init__(self):
        self.gold_box = pygame.Rect(25, 10, 300, 100)
        self.gold_img = self.load("menu/gold.png")
    def load(self, filename):
        s = pygame.image.load(filename).convert_alpha()
        return s
    
    def update(self, get_gold):
        Gold.now += get_gold

    def draw(self, font):
        pygame.draw.rect(screen, (134, 229, 127), self.gold_box)
        gold_text = font.render(str(Gold.now), True, (255, 255, 255)) # menu
        screen.blit(self.gold_img, (50, 30))
        screen.blit(gold_text, (200, 50))

class Ground:
    def __init__(self):
        self.tile = self.load("background_tile/png/Tile/2.png")
        self.x = 0

    def load(self, filename):
        s = pygame.image.load(filename).convert_alpha()
        s = pygame.transform.scale(s, (64, 64))
        return s

    def draw(self, screen, bgx):
        for i in range(-1, 17):
            screen.blit(self.tile, (i * 64 - bgx % 64, 64 * 11))

class Tree(MoveObject):
    def __init__(self, x, y, flipped=False):
        self.flipped = flipped
        super().__init__(x, y)
        self.collide_rect = pygame.Rect(
            self.x, self.y, 
            self.rect.width - 175, 
            self.rect.height
        )
        self.hp = 5000
    
    def init_sprites(self):
        self.sprites = []
        img = pygame.image.load("background_tile/png/Objects/Tree.png").convert_alpha()
        if self.flipped:
            img = pygame.transform.flip(img, True, False)
        self.sprites = [img]

        return self.sprites
    
    def update(self, bgx):
        super().update(bgx)
        self.collide_rect.center = self.rect.center

# 이벤트 발생이후 실행사항 
def handle_timer_events():
    for unit in unit_sprites:
        if unit.vx == 0:
            unit.vx = 1.5  # 다시 이동
    
    for enemy in enemy_units:
        if enemy.vx == 0:
            enemy.vx = -1.5  # 다시 이동
           
def unit_collide_check(unit_sprites, unit):
    """유닛들이 겹치지 않게 체크"""
    collided_sprites = pygame.sprite.spritecollide(unit, unit_sprites, False)
    for collided_unit in collided_sprites:
        if collided_unit.created_time > unit.created_time:
            collided_unit.vx = 0
            if not collided_unit.attack:
                 collided_unit.sprite_id = 0
        # 일정 시간이 지나면 다시 이동하도록 타이머 설정
        pygame.time.set_timer(pygame.USEREVENT + 1, 10, True)
    
pygame.init()
mixer.init()
# https://freesound.org/people/MusicByMisterbates/sounds/608811/
mixer.music.load("608811__musicbymisterbates__uplifting-dramatic-soundtrack-war-around-us.mp3")
mixer.music.set_volume(0.2)
screen = pygame.display.set_mode((1024, 768))  # 윈도우 크기
menu_font = pygame.font.SysFont("system", 40) # menu 폰트
background = pygame.image.load("background_tile/png/BG.png").convert_alpha()
clock = pygame.time.Clock()
tree = Tree(50, 575)
enemy_tree = Tree(screen.get_width() + 225, 575, flipped=True)
quit = False

while True:
    running = True
    bgx = 0  # background x
    ground = Ground()
    menu_bar = Menu()
    gold = Gold()
    trees = pygame.sprite.Group()
    unit_sprites = pygame.sprite.Group()
    dead_unit_sprites = pygame.sprite.Group()
    enemy_units = pygame.sprite.Group()
    arrows = pygame.sprite.Group()
    trees.add(tree)
    trees.add(enemy_tree)
    menu_click = None
    mixer.music.play(-1)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Left mouse button click
                menu_click = menu_bar.handle_click(event.pos)
            elif event.type == pygame.USEREVENT + 1:
                handle_timer_events()
                

        # 적 유닛(enemy) 등장 확률 및 양 조절
        if random.random() > 0.995 and len(enemy_units) < 5:
            enemy_unit = Enemy_Skeleton_Warrior(1150, 680)
            enemy_units.add(enemy_unit)
            pass

        if isinstance(menu_click, Unit):
            unit_sprites.add(menu_click)

        """업데이트"""
        
        point = pygame.mouse.get_pos()
        lmousedown = pygame.mouse.get_pressed()[0]
        menu_text = menu_font.render("Menu", True, (128, 0, 0)) # menu

        if point[0] > 1000 and bgx < 249:
            bgx += GROUND_SPEED
        elif point[0] < 25 and bgx > 0:
            bgx -= GROUND_SPEED

        for enemy in enemy_units.copy():
            unit_collide_check(enemy_units, enemy)
            enemy.attack_tree(tree)
            if not unit_sprites and not enemy.target_tree:
                enemy.attack = False
            if enemy.is_dead:
                enemy_units.remove(enemy)
            
            for arrow in arrows.copy():
                if arrow.x > enemy.x - 10:
                    enemy.hp -= arrow.damage
                    arrows.remove(arrow)
                    print(enemy.hp)
            
        for unit in unit_sprites.copy():
            unit_collide_check(unit_sprites, unit)
            unit.shot_complition = False
            unit.attack_tree(enemy_tree)
            if not enemy_units and not unit.target_tree:
                unit.attack = False
            if unit.is_dead:
                unit_sprites.remove(unit)

        for arrow in arrows.copy():
            if arrow.rect.colliderect(enemy_tree.collide_rect):
                enemy_tree.hp -= arrow.damage
                arrows.remove(arrow)
                print(enemy_tree.hp)    
    
        # unit -> dead_sprites 완료 후 삭제처리
        for dead_unit in dead_unit_sprites.copy():
            if dead_unit.sprite_id >= len(dead_unit.sprites) - 1:
                dead_unit_sprites.remove(dead_unit)

        for unit in unit_sprites.copy():
            unit.shot_tree(enemy_tree, unit.shot_complition)
            for enemy in enemy_units.copy():
                unit.fighting(enemy)
                unit.shot_complition = unit.shot_arrow(enemy, unit.shot_complition)
                enemy.fighting(unit)

                if unit.hp <= 0 and not unit.is_dead:
                    unit.is_dead = True
                    dead_unit_sprites.add(Dead_Skeleton(unit))
                if enemy.hp <= 0 and not enemy.is_dead:
                    enemy.is_dead = True
                    dead_unit_sprites.add(Dead_Skeleton(enemy))

        menu_bar.update()
        unit_sprites.update(bgx)
        enemy_units.update(bgx)
        arrows.update(bgx)
        dead_unit_sprites.update(bgx)
        trees.update(bgx)

        """화면에 그리기"""
        screen.fill((255, 255, 255))
        screen.blit(background, dest=(-bgx, 0))
        ground.draw(screen, bgx)
        gold.draw(menu_font)
        menu_bar.draw(screen)
        screen.blit(menu_text, (725, 20))
        # 나무
        trees.draw(screen)
        menu_bar.point_for_menu(point)

        dead_unit_sprites.draw(screen)
        unit_sprites.draw(screen)
        for unit in unit_sprites.copy(): 
            unit.unit_hp_draw(point) # 유닛 체력바
        enemy_units.draw(screen)
        for enemy in enemy_units.copy():
            enemy.unit_hp_draw(point)
        arrows.draw(screen)

        pygame.display.flip()
        clock.tick(50)
    if quit:
        break
pygame.quit()