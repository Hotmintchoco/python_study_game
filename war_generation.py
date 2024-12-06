import pygame
import random
from pygame import mixer

GROUND_SPEED = 7.5

class GameObject(pygame.sprite.Sprite):
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

class Unit(GameObject):
    def __init__(self, x, y, img_file, flipped=False, is_shot=False,
                  unit_vx=1.5, unit_ds=0.1, level=1, hp=50):
        self.img_file = img_file
        self.level = level
        self.attack = False
        self.target = None
        self.is_dead = False
        self.target_tree = False
        self.shot_complition = False
        self.now_shot = False
        self.collided_unit = False
        self.is_change_motion = False
        self.is_shot = is_shot
        self.flipped = flipped
        self.hp = hp
        self.hp_divide = 1
        if self.hp > 50:
            self.hp_divide = self.hp / 50
        self.created_time = pygame.time.get_ticks()  # 생성 시각 추가
        self.run_sprites = self.init_sprites()
        self.attack_sprites = self.get_sprites()
        super().__init__(x, y, vx=unit_vx, ds=unit_ds)
        self.collide_rect = self.rect

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
        if not self.is_shot:
            if self.attack:
                self.sprites = self.attack_sprites
                self.change_motion()
            else:
                self.is_change_motion = False
                self.sprites = self.run_sprites
        super().update(bgx)
        self.collide_rect.center = self.rect.center
        self.hp_bar = pygame.Rect(self.x-25-bgx, self.y-40, self.hp // self.hp_divide, 5)
    
    def change_motion(self):
        if not self.is_change_motion:
            self.is_change_motion = True
            self.sprite_id = 0
    
    def attack_motion(self, target):
        self.vx = 0
        self.attack = True
        if len(self.sprites)-1< self.sprite_id < len(self.sprites)-(1-self.ds) and not self.is_shot:
            print(len(self.sprites))
            target.hp -= self.damage
        elif len(self.sprites)-1< self.sprite_id < len(self.sprites)-(1-self.ds) and self.is_shot:
            target.hp -= self.damage

    def fighting(self, enemy):
        if not self.is_shot and self.rect.colliderect(enemy.rect) and enemy.hp > 0:
            self.target_tree = False
            self.target = enemy
            self.attack_motion(enemy)
        elif self.is_shot and self.collide_rect.colliderect(enemy.rect) and enemy.hp > 0:
            self.target_tree = False
            self.target = enemy
            self.attack_motion(enemy)
       
        if self.target:
            if self.target.hp <= 0 and not self.flipped:
                self.attack = False
                self.now_shot = False
                self.collided_unit = False
                self.target = None
            elif self.target.hp <= 0 and self.flipped:
                self.attack = False
                self.now_shot = False
                self.target = None
    
    def attack_tree(self, tree):
        if self.target:
            if self.rect.colliderect(tree.collide_rect) and self.target.hp <= 0:
                self.target_tree = True
                self.vx = 0
                self.attack_motion(tree)
        else:
            if self.rect.colliderect(tree.collide_rect):
                self.target_tree = True
                self.vx = 0
                self.attack_motion(tree)
        
    def unit_hp_draw(self, pos):
        if self.rect.collidepoint(pos):
            pygame.draw.rect(screen, (255, 0, 0), self.hp_bar)

class Dead_Unit(GameObject):
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
         
class Warrior_Unit(Unit):
    run_sprites = []
    attack_sprites = []

    def __init__(self, x, y, unit_level=1):
        if unit_level == 1:
            img_file="Unit/Skeleton_Warrior/Skeleton"
            self.damage = 10
            unit_hp = 100
            ds = 0.1
        elif unit_level == 2:
            img_file = "Unit/Samurai/Samurai"
            self.damage = 35
            unit_hp = 200
            ds = 0.1
        elif unit_level == 3:
            img_file = "Unit/Wizard_Fire vizard/Wizard"
            self.damage = 100
            unit_hp = 500
            ds = 0.15
        super().__init__(x, y, img_file, level=unit_level, hp=unit_hp, unit_ds=ds)

class Archer_Unit(Unit):
    run_sprites = []
    attack_sprites = []
    shot_sprites = []

    def __init__(self, x, y, unit_level=1):
        if unit_level == 1:
            self.img_file="Unit/Skeleton_Archer/Skeleton"
            self.damage = 10
            add_collide_rect = 20
            unit_hp = 50
            unit_ds = 0.19
        elif unit_level == 2:
            self.img_file = "Unit/Samurai_Archer/Samurai"
            self.damage = 20
            add_collide_rect = 5
            unit_hp = 100
            unit_ds = 0.19
        elif unit_level == 3:
            self.img_file = "Unit/Wizard_Lightning Mage/Wizard"
            self.damage = 75
            add_collide_rect = 10
            unit_hp = 250
            unit_ds = 0.1

        super().__init__(x, y, self.img_file, level=unit_level, is_shot=True, hp=unit_hp)
        self.shot_sprites = self.shot_motion_sprites()
        self.ds = unit_ds
        self.collide_rect = pygame.Rect(
            self.x, self.y, 
            self.rect.width + add_collide_rect, 
            self.rect.height
        )
    
    def shot_motion_sprites(self):
        if not self.shot_sprites:
            index = 0
            while True:
                try:
                    index += 1
                    img = pygame.image.load(
                        f"{self.img_file}_Shot({index}).png"
                    ).convert_alpha()
                    self.shot_sprites.append(img)
                except:
                    break
        return self.shot_sprites

    def update(self, bgx):
        super().update(bgx)
        self.collide_rect.center = self.rect.center
        if self.now_shot:
            self.sprites = self.shot_sprites
            self.change_motion()
        elif self.attack:
            self.sprites = self.attack_sprites
            self.change_motion()
        else:
            self.is_change_motion = False
            self.sprites = self.run_sprites
        
    def shot_motion(self, shot_complition):
        arrow_y = self.y
        if self.level == 1:
            arrow_y = self.y-10
            new_arrow = Arrow(self.x-5, arrow_y)
        elif self.level == 2:
            arrow_y = self.y+5
            new_arrow = Samurai_Arrow(self.x-5, arrow_y)
        elif self.level == 3:
            arrow_y = self.y - 20
            new_arrow = Light_Ball(self.x + 20, arrow_y)

        if 12.01 < self.sprite_id < 12.2 and not shot_complition and self.now_shot and self.level < 3:
            arrows.add(new_arrow)
        elif 3.9 < self.sprite_id < 4 and not shot_complition and self.now_shot and self.level == 3:
            arrows.add(new_arrow)

    def shot_tree(self, tree, shot_complition):
        if self.target:
            if not self.rect.colliderect(tree.collide_rect) and self.x + 225 > tree.x and self.target.hp <= 0:
                self.now_shot = True
                self.target_tree = True
                self.shot_motion(shot_complition)
            else:
                self.now_shot = False
        else:
            if not self.rect.colliderect(tree.collide_rect) and self.x + 225 > tree.x:
                self.now_shot = True
                self.target_tree = True
                self.shot_motion(shot_complition)
            
    def shot_arrow(self, enemy, shot_complition):
        if unit.collide_rect.colliderect(enemy.rect):
            self.collided_unit = True
            self.now_shot = False
            self.target = enemy
        elif self.x + 200 > enemy.x and enemy.hp > 0 and not self.collided_unit:
            self.now_shot = True
            self.target = enemy
            self.shot_motion(shot_complition)

            return True
        return False

class Commander_Unit(Unit):
    run_sprites = []
    attack_sprites = []

    def __init__(self, x, y, unit_level=1):
        if unit_level == 1:
            img_file="Unit/Skeleton_Spearman/Skeleton"
            self.damage = 25
            unit_hp = 150
            ds = 0.1
        elif unit_level == 2:
            img_file = "Unit/Samurai_Commander/Samurai"
            self.damage = 50
            unit_hp = 300
            ds = 0.15
        elif unit_level == 3:
            img_file = "Unit/Wizard_Wanderer Magican/Wizard"
            self.damage = 150
            unit_hp = 750
            ds = 0.19
        super().__init__(x, y, img_file, level=unit_level, hp=unit_hp, unit_ds=ds)

class Enemy_Warrior_Unit(Unit):
    run_sprites = []
    attack_sprites = []

    def __init__(self, x, y, img_file="Unit/Skeleton_Warrior/Skeleton"):
        if Enemy_Warrior_Unit.run_sprites:
            self.run_sprites = Enemy_Warrior_Unit.run_sprites

        if Enemy_Warrior_Unit.attack_sprites:
            self.attack_sprites = Enemy_Warrior_Unit.attack_sprites
        super().__init__(x, y, img_file, flipped=True, unit_vx=-1.5, hp=100)
        self.damage = 10
        self.price = 32

class Enemy_Archer_Unit(Unit):
    run_sprites = []
    attack_sprites = []
    shot_sprites = []

    def __init__(self, x, y, unit_level=1):
        if unit_level == 1:
            self.img_file="Unit/Skeleton_Archer/Skeleton"
            self.damage = 10
            self.shot_distance = 200
        elif unit_level == 2:
            self.img_file = "Unit/Samurai_Archer/Samurai"
            self.damage = 35
            self.shot_distance = 250
        
        super().__init__(x, y, self.img_file, is_shot=True, flipped=True, unit_vx=-1.5)
        self.shot_sprites = self.shot_motion_sprites()
        self.ds = 0.19
        self.price = 65
    
    def shot_motion_sprites(self):
        if not self.shot_sprites:
            index = 0
            while True:
                try:
                    index += 1
                    img = pygame.image.load(
                        f"{self.img_file}_Shot({index}).png"
                    ).convert_alpha()
                    img = pygame.transform.flip(img, True, False)
                    self.shot_sprites.append(img)
                except:
                    break
        return self.shot_sprites
    
    def update(self, bgx):
        super().update(bgx)
        if self.now_shot:
            self.sprites = self.shot_sprites
        elif self.attack:
            self.sprites = self.attack_sprites
        else:
            self.sprites = self.run_sprites
        
    def shot_motion(self, shot_complition):
        if 12.01 < self.sprite_id < 12.2 and not shot_complition:
            new_arrow = Enemy_Arrow(self.x+5, self.y-10)
            enemy_arrows.add(new_arrow)
            print(self.sprite_id)

    def shot_tree(self, tree, shot_complition):
        if not self.rect.colliderect(tree.collide_rect):
            if self.flipped and self.x - (self.shot_distance + 25) < tree.x and not self.target:
                self.now_shot = True
                self.target_tree = True
                self.shot_motion(shot_complition)
        else:
            self.now_shot = False

    def shot_arrow(self, enemy, shot_complition):
        if not self.rect.colliderect(enemy.rect):
            if self.flipped and self.x - self.shot_distance < enemy.x and enemy.hp > 0:
                self.now_shot = True
                self.target = enemy
                self.shot_motion(shot_complition)
            return True
        return False

class Enemy_Commander_Unit(Unit):
    run_sprites = []
    attack_sprites = []

    def __init__(self, x, y, img_file="Unit/Skeleton_Spearman/Skeleton"):
        if Enemy_Commander_Unit.run_sprites:
            self.run_sprites = Enemy_Commander_Unit.run_sprites

        if Enemy_Commander_Unit.attack_sprites:
            self.attack_sprites = Enemy_Commander_Unit.attack_sprites
        super().__init__(x, y, img_file, flipped=True, unit_vx=-1.5)
        self.damage = 25
        self.price = 175

class Turret(GameObject):
    def __init__(self, x, y, flipped=False):
        self.flipped = flipped
        self.is_shot = False
        self.target = None
        self.shot_time = 0
        self.turret_speed = 25 # 낮을수록 빠름
        super().__init__(x, y)
    
    def init_sprites(self):
        self.sprites = []
        img = pygame.image.load("Turret/Turret1Top.png").convert_alpha()
        img = pygame.transform.scale(img, (80, 40))
        if self.flipped:
            img = pygame.transform.flip(img, True, False)
        self.sprites = [img]

        return self.sprites
    
    def set_target(self, enemy):
        if menu_bar.turret.x + 400 > enemy.x:
            if not self.target:
                self.target = enemy
                self.shot_time = 0

    def shot_turret(self):
        if self.target:
            if self.shot_time < 50:
                self.shot_time += 1
            else:
                target_x_distance = self.target.x - self.x
                target_y_distance = self.target.y - self.y
                new_shell = Shell(self.x+35, self.y, vx=target_x_distance/self.turret_speed, vy=target_y_distance/self.turret_speed)
                shells.add(new_shell)
                self.shot_time = 0

            if self.target.hp <= 0:
                self.target = None

class Shell(GameObject):
    source_sprites = []
    def __init__(self, x, y, vx=10, vy= 4.22):
        self.damage = 30
        super().__init__(x, y, vx=vx, vy=vy)
    
    def init_sprites(self):
        if not Shell.source_sprites:
            img = pygame.image.load("Turret/shell.png").convert_alpha()
            img = pygame.transform.scale(img, (20, 20))
            Shell.source_sprites = [img]
        return Shell.source_sprites
    
class Arrow(GameObject):
    source_sprites = []
    def __init__(self, x, y):
        super().__init__(x, y, vx=10.0)
        self.damage = 25
    def init_sprites(self):
        if not Arrow.source_sprites:
            img = pygame.image.load("Unit/Skeleton_Archer/Arrow.png").convert_alpha()
            Arrow.source_sprites = [img]
        return Arrow.source_sprites

class Samurai_Arrow(GameObject):
    source_sprites = []
    def __init__(self, x, y):
        super().__init__(x, y, vx=10.0)
        self.damage = 50
    def init_sprites(self):
        if not Samurai_Arrow.source_sprites:
            img = pygame.image.load("Unit/Samurai_Archer/Arrow.png").convert_alpha()
            Samurai_Arrow.source_sprites = [img]
        return Samurai_Arrow.source_sprites

class Light_Ball(GameObject):
    source_sprites = []
    def __init__(self, x, y):
        super().__init__(x, y, vx=8.0)
        self.damage = 150
    def init_sprites(self):
        if not Arrow.source_sprites:
            img = pygame.image.load("Unit/Wizard_Lightning Mage/Light_ball.png").convert_alpha()
            img = pygame.transform.scale(img, (48, 48))
            Arrow.source_sprites = [img]
        return Arrow.source_sprites

class Enemy_Arrow(GameObject):
    source_sprites = []
    def __init__(self, x, y):
        super().__init__(x, y, vx=-10.0)
        self.damage = 25
    def init_sprites(self):
        if not Arrow.source_sprites:
            img = pygame.image.load("Unit/Skeleton_Archer/Arrow.png").convert_alpha()
            img = pygame.transform.flip(img, True, False)
            Arrow.source_sprites = [img]
        return Arrow.source_sprites

class Menu:
    MAX_GAUGE = 325
    def __init__(self):
        super().__init__()
        self.menu = pygame.Rect(700, 0, 500, 150)
        self.main_menu()
        self.menu_index = 0
        self.unit_menu = False
        self.is_unit_create = False # 유닛이 생성 시간이 다 채워지면 True
        self.is_unit_create_time = False # 유닛 생성 시간 이미지
        self.bool_add_unit = True
        self.upgrade_stand = False
        self.turret = None
        self.upgrade_level = 1
        
        self.first_img_rect = self.first_img.get_rect(topleft=(725, 60))  # Unit image position
        self.second_img_rect = self.second_img.get_rect(topleft=(800, 60))
        self.third_img_rect = self.third_img.get_rect(topleft=(875, 60))
        self.forth_img_rect = self.forth_img.get_rect(topleft=(950, 60))
        self.unit_create_time_rect = pygame.Rect(350, 15, 10, 35)

        self.unit_price = 0
        self.menu_price = 200
        self.upgrade_price = 0
        self.dict_unit_price = {
            25 : Warrior_Unit,
            50 : Archer_Unit,
            150 : Commander_Unit
        }
        self.list_unit_price = list(self.dict_unit_price.keys())
        self.menu_font = pygame.font.SysFont("system", 45)
        self.menu_point_text = ""
        self.unit_create_gauge = 0
        self.list_unit_create_gauge = [7.5, 6, 4]

    def load(self, filename):
        s = pygame.image.load(filename).convert_alpha()
        s = pygame.transform.scale(s, (48, 48))
        return s
    
    def update(self):
        if self.unit_menu:
            self.menu_text = menu_font.render(f"Unit_Price = {self.unit_price}", 1, (125, 125, 125))
        else:
            self.menu_text = menu_font.render(f"{self.menu_point_text} = {self.menu_price}", 1, (125, 125, 125))

        if self.is_unit_create_time and self.unit_create_gauge <= Menu.MAX_GAUGE:
            self.unit_create_gauge += self.list_unit_create_gauge[self.menu_index]
            self.unit_create_time_rect = pygame.Rect(350, 15, self.unit_create_gauge, 25)
        elif self.unit_create_gauge > Menu.MAX_GAUGE:
            self.is_unit_create = True 
            self.is_unit_create_time = False
            self.unit_create_gauge = 0

        # 유닛 생성이 완료된 후 업그레이드
        if self.upgrade_stand and self.bool_add_unit:
            self.upgrade_click()
            self.upgrade_stand = False
      
    # 메인 메뉴의 이미지들
    def main_menu(self):
        self.first_img = self.load("menu/unit.png")
        self.second_img = self.load("menu/turret.png")
        self.third_img = self.load("menu/turret_sell.png")
        self.forth_img = self.load("menu/upgrade.png")
        self.gold_img = self.load("menu/gold.png")

    def unit_click(self):
        if self.upgrade_level == 1:
            self.first_img = self.load("menu/Skeleton_Warrior.png")
            self.second_img = self.load("menu/Skeleton_Archer.png")
            self.third_img = self.load("menu/Skeleton_Spear.png")
        elif self.upgrade_level == 2:
            self.first_img = self.load("menu/Samurai.png")
            self.second_img = self.load("menu/Samurai_Archer.png")
            self.third_img = self.load("menu/Samurai_Commander.png")
        
        self.forth_img = self.load("menu/Return.png")

    def create_unit(self):
        self.is_unit_create = False
        if self.upgrade_level > 1:
            return self.dict_unit_price[self.buy_unit_price](150, 670, self.upgrade_level)
        return self.dict_unit_price[self.buy_unit_price](150, 680, self.upgrade_level)

    def buy_unit(self, unit_price):
        self.bool_add_unit = False
        Gold.now -= unit_price

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 220, 115), self.menu)
        screen.blit(self.first_img, self.first_img_rect.topleft)
        screen.blit(self.second_img, self.second_img_rect.topleft)
        screen.blit(self.third_img, self.third_img_rect.topleft)
        screen.blit(self.forth_img, self.forth_img_rect.topleft)

        if self.is_unit_create_time:
            pygame.draw.rect(screen, (125, 125, 125), self.unit_create_time_rect)
    
    def point_for_menu_draw(self, pos):
        if self.unit_menu:
            if self.first_img_rect.collidepoint(pos):
                self.unit_price = self.list_unit_price[0]
                screen.blit(self.menu_text, (350, 75))
            elif self.second_img_rect.collidepoint(pos):
                self.unit_price = self.list_unit_price[1]
                screen.blit(self.menu_text, (350, 75))
            elif self.third_img_rect.collidepoint(pos):
                self.unit_price = self.list_unit_price[2]
                screen.blit(self.menu_text, (350, 75))
        
        else:
            if self.second_img_rect.collidepoint(pos):
                self.menu_point_text = "Turret Price"
                self.menu_price = 200
                screen.blit(self.menu_text, (350, 75))

            elif self.third_img_rect.collidepoint(pos) and self.turret:
                self.menu_point_text = "Refund turret"
                self.menu_price = 100
                screen.blit(self.menu_text, (350, 75))
            
            elif self.forth_img_rect.collidepoint(pos):
                self.menu_point_text = "Upgrade Price"
                if self.upgrade_level == 1:
                    self.menu_price = 4000
                elif self.upgrade_level == 2:
                    self.menu_price = 15000
                screen.blit(self.menu_text, (350, 75))

    def upgrade_click(self):
        self.upgrade_level += 1
        self.dict_unit_price = {
            100 : Warrior_Unit,
            125 : Archer_Unit,
            500 : Commander_Unit
        }
        self.list_unit_price = list(self.dict_unit_price.keys())
        self.list_unit_create_gauge = [5, 4, 2]
        print(f"현재 level = {self.upgrade_level}")
        Warrior_Unit.run_sprites = []
        Warrior_Unit.attack_sprites = []
        Archer_Unit.run_sprites = []
        Archer_Unit.attack_sprites = []
        Archer_Unit.shot_sprites = []
        Commander_Unit.run_sprites = []
        Commander_Unit.attack_sprites = []

    def handle_click(self, pos):
        if self.first_img_rect.collidepoint(pos):
            if self.unit_menu and Gold.now >= self.unit_price and not self.is_unit_create_time:
                self.menu_index = 0
                self.is_unit_create_time = True
                self.buy_unit_price = self.unit_price
                self.buy_unit(self.buy_unit_price)
            self.unit_menu = True
            self.unit_click()

        elif self.second_img_rect.collidepoint(pos):
            if self.unit_menu and Gold.now >= self.unit_price and not self.is_unit_create_time:
                self.menu_index = 1
                self.is_unit_create_time = True
                self.buy_unit_price = self.unit_price
                self.buy_unit(self.buy_unit_price)
            elif not self.turret and Gold.now >= self.menu_price:
                self.turret = Turret(125, 550, flipped=True)
                turrets.add(self.turret)
                Gold.now -= self.menu_price

        elif self.third_img_rect.collidepoint(pos):
            if self.unit_menu and Gold.now >= self.unit_price and not self.is_unit_create_time:
                self.menu_index = 2
                self.is_unit_create_time = True
                self.buy_unit_price = self.unit_price
                self.buy_unit(self.buy_unit_price)
            elif self.turret:
                turrets.remove(self.turret)
                self.turret = None
                Gold.now += self.menu_price

        elif self.forth_img_rect.collidepoint(pos):
            if self.unit_menu:
                self.main_menu()
                self.unit_menu = False
            elif Gold.now >= self.menu_price:
                self.upgrade_stand = True
                Gold.now -= self.menu_price

class Gold:
    now = 30000
    total_earn = 0
    def __init__(self):
        self.gold_box = pygame.Rect(25, 10, 300, 100)
        self.gold_img = self.load("menu/gold.png")
    def load(self, filename):
        s = pygame.image.load(filename).convert_alpha()
        return s
    
    def update(self, get_gold):
        Gold.now += get_gold
        Gold.total_earn += get_gold

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

class Tree(GameObject):
    def __init__(self, x, y, flipped=False):
        self.flipped = flipped
        super().__init__(x, y)
        self.collide_rect = pygame.Rect(
            self.x, self.y, 
            self.rect.width - 175, 
            self.rect.height
        )
        self.hp = 5000
        self.hp_divide = self.hp / 450
    
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
        hp_height = self.hp // self.hp_divide
        if self.flipped:
            self.hp_bar = pygame.Rect(self.x - (bgx - 5), 200 + (450 - hp_height), 15, hp_height)
        else:
            self.hp_bar = pygame.Rect(self.x - (bgx + 40), 200 + (450 - hp_height), 15, hp_height)

    def tree_hp_draw(self):
        pygame.draw.rect(screen, (225, 94, 0), self.hp_bar)

# 이벤트 발생이후 실행사항 / 유닛 이동속도 처리
def handle_timer_events():
    for unit in unit_sprites:
        if unit.vx < 1:
            unit.vx = 1.5  # 다시 이동

        if unit.is_shot:
            if unit.now_shot:
                unit.vx = 0.3
    
    for enemy in enemy_units:
        if enemy.vx > -1:
            enemy.vx = -1.5  # 다시 이동

        if enemy.is_shot:
            if enemy.now_shot:
                enemy.vx = -0.3
           
def unit_collide_check(unit_sprites, unit):
    """유닛들이 겹치지 않게 체크"""
    collided_sprites = pygame.sprite.spritecollide(unit, unit_sprites, False)
    for collided_unit in collided_sprites:
        if collided_unit.created_time > unit.created_time:
            collided_unit.vx = 0

            if not collided_unit.attack and not collided_unit.now_shot:
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
    enemy_rand = 0
    max_rand = 8
    game_difficult = 0
    bgx = 0  # background x
    ground = Ground()
    menu_bar = Menu()
    gold = Gold()
    trees = pygame.sprite.Group()
    unit_sprites = pygame.sprite.Group()
    dead_unit_sprites = pygame.sprite.Group()
    enemy_units = pygame.sprite.Group()
    turrets = pygame.sprite.Group()
    shells = pygame.sprite.Group()
    arrows = pygame.sprite.Group()
    enemy_arrows = pygame.sprite.Group()
    trees.add(tree)
    trees.add(enemy_tree)
    mixer.music.play(-1)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Left mouse button click
                menu_bar.handle_click(event.pos)
            elif event.type == pygame.USEREVENT + 1:
                handle_timer_events()
                
        # 적 유닛(enemy) 등장 확률 및 양 조절
        rand = random.random()
        if 1400 > Gold.total_earn >= 1000:
            game_difficult = 3
        elif Gold.total_earn > 2400:
            game_difficult = 5
        if rand > 0.992 and len(enemy_units) < 5:
            enemy_rand = round(rand * 1000 - 992) # 0 ~ 8 까지

            if game_difficult < 4:
                if enemy_rand >= game_difficult:
                    print(f"적 등장 확률 : {enemy_rand} / 현재 난이도: {game_difficult}")
                    enemy_unit = Enemy_Warrior_Unit(1150, 680)
                    enemy_units.add(enemy_unit)
                else:
                    print(f"적 등장 확률 : {enemy_rand} / 현재 난이도: {game_difficult}")
                    enemy_unit = Enemy_Archer_Unit(1150, 680)
                    enemy_units.add(enemy_unit)
            
            else:
                if enemy_rand > game_difficult:
                    print(f"적 등장 확률 : {enemy_rand} / 현재 난이도: {game_difficult}")
                    enemy_unit = Enemy_Commander_Unit(1150, 680)
                    enemy_units.add(enemy_unit)
                elif game_difficult >= enemy_rand > max_rand - game_difficult:
                    print(f"적 등장 확률 : {enemy_rand} / 현재 난이도: {game_difficult}")
                    enemy_unit = Enemy_Archer_Unit(1150, 680)
                    enemy_units.add(enemy_unit)
                else:
                    print(f"적 등장 확률 : {enemy_rand} / 현재 난이도: {game_difficult}")
                    enemy_unit = Enemy_Warrior_Unit(1150, 680)
                    enemy_units.add(enemy_unit)
                    
        if menu_bar.is_unit_create:
            unit_sprites.add(menu_bar.create_unit())
            menu_bar.bool_add_unit = True

        if menu_bar.turret:
            menu_bar.turret.shot_turret()
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
            enemy.shot_complition = False
            enemy.attack_tree(tree)
            if enemy.hp <= 0 and not enemy.is_dead:
                    enemy.is_dead = True
                    dead_unit_sprites.add(Dead_Unit(enemy))

            if not unit_sprites and not enemy.target_tree:
                enemy.attack = False
            if enemy.is_dead:
                enemy_units.remove(enemy)
                gold.update(enemy.price)
            
            if menu_bar.turret:
                menu_bar.turret.set_target(enemy)

            for shell in shells.copy():
                if shell.rect.colliderect(enemy.rect):
                    enemy.hp -= shell.damage
                    shells.remove(shell)

            for arrow in arrows.copy():
                if arrow.x > enemy.x - 10:
                    enemy.hp -= arrow.damage
                    arrows.remove(arrow)
        
        for enemy in enemy_units.copy():
            if enemy.is_shot:
                enemy.shot_tree(tree, enemy.shot_complition)
            
        for unit in unit_sprites.copy():
            unit_collide_check(unit_sprites, unit)
            unit.shot_complition = False
            unit.attack_tree(enemy_tree)
            if unit.hp <= 0 and not unit.is_dead:
                    unit.is_dead = True
                    dead_unit_sprites.add(Dead_Unit(unit))
            if not enemy_units and not unit.target_tree:
                unit.attack = False
            if unit.is_dead:
                unit_sprites.remove(unit)

            for arrow in enemy_arrows.copy():
                if arrow.x < unit.x + 10:
                    unit.hp -= arrow.damage
                    enemy_arrows.remove(arrow)
                    print(unit.hp)

        for arrow in arrows.copy():
            if arrow.rect.colliderect(enemy_tree.collide_rect):
                enemy_tree.hp -= arrow.damage
                arrows.remove(arrow)
                print("화살피격/ enemy_tree.hp: ", enemy_tree.hp)

        for arrow in enemy_arrows.copy():
            if arrow.rect.colliderect(tree.collide_rect):
                tree.hp -= arrow.damage
                enemy_arrows.remove(arrow)
                print(tree.hp)

        # unit -> dead_sprites 완료 후 삭제처리
        for dead_unit in dead_unit_sprites.copy():
            if dead_unit.sprite_id >= len(dead_unit.sprites) - 1:
                dead_unit_sprites.remove(dead_unit)

        for unit in unit_sprites.copy():
            if unit.is_shot:
                unit.shot_tree(enemy_tree, unit.shot_complition)
            for enemy in enemy_units.copy():
                unit.fighting(enemy)
                enemy.fighting(unit)
                if unit.is_shot:
                    unit.shot_complition = unit.shot_arrow(enemy, unit.shot_complition)
                else:
                    unit.now_shot = False
                if enemy.is_shot:
                    enemy.shot_complition = enemy.shot_arrow(unit, enemy.shot_complition)

        menu_bar.update()
        unit_sprites.update(bgx)
        enemy_units.update(bgx)
        turrets.update(bgx)
        arrows.update(bgx)
        enemy_arrows.update(bgx)
        shells.update(bgx)
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
        menu_bar.point_for_menu_draw(point)

        dead_unit_sprites.draw(screen)
        unit_sprites.draw(screen)
        for unit in unit_sprites.copy(): 
            unit.unit_hp_draw(point) # 유닛 체력바
        enemy_units.draw(screen)
        for enemy in enemy_units.copy():
            enemy.unit_hp_draw(point)
        turrets.draw(screen)
        arrows.draw(screen)
        enemy_arrows.draw(screen)
        shells.draw(screen)
        tree.tree_hp_draw()
        enemy_tree.tree_hp_draw()

        pygame.display.flip()
        clock.tick(40)
    if quit:
        break
pygame.quit()