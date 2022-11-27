import pygame
import sys
import random

class Sprite():

    def __init__(self,
                 x=0,
                 y=0,
                 image='missing.png',
                 size=100,
                 hitbox_x=0,
                 hitbox_y=0,
                 hitbox_d=0,
                 text=[],
                 deleted=False):
        self.x = x
        self.y = y
        self.image = pygame.image.load('images/' + image).convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.smoothscale(self.image,(self.rect.width*size/100,self.rect.height*size/100))
        self.rect = self.image.get_rect()
        self.size = size
        self.hitbox_x = hitbox_x
        self.hitbox_y = hitbox_y
        self.hitbox_d = hitbox_d
        self.text = text
        self.tick = 0
        self.deleted = deleted

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def var_event(self):
        self.rect.topleft = (self.x, self.y)

    def game_event(self):
        pass

    def trash(self):
        self.deleted = True

    def update(self, screen):
        self.game_event()
        self.var_event()
        self.draw(screen)
        self.tick += 1


class Player(Sprite):

    def __init__(self):
        Sprite.__init__(self, 640, 640, 'player.png', 100, 30, 30, 5,
                        ['player'])
        self.shootcd = 0
        self.graze = 0
        self.respawn = 0

    def game_event(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT]:
            sp = 5
        else:
            sp = 10
        if keys[pygame.K_LEFT] and self.rect.left > -10:
            self.x -= sp
        if keys[pygame.K_RIGHT] and self.rect.right < 1350:
            self.x += sp
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.y -= sp
        if keys[pygame.K_DOWN] and self.rect.bottom < 760:
            self.y += sp

        if keys[pygame.K_z]:
            self.shoot()
        if self.shootcd > 0:
            self.shootcd -= 1
        elif self.shootcd < 0:
            self.shootcd = 0

        if self.graze > 0:
            self.graze -= 1
        elif self.graze < 0:
            self.graze = 0
        if self.respawn > 0:
            self.respawn -= 1
        elif self.respawn < 0:
            self.respawn = 0
        if self.respawn == 0:
            self.collide_event()

    def shoot(self):
        global game
        if self.shootcd == 0:
            game.group.append(PlayerBullet(self.x, self.y - 20))
            self.shootcd = 5

    def collide_event(self):
        global game

        def collide(target, eps=0):
            hx = self.x + self.hitbox_x
            hy = self.y + self.hitbox_y
            tx = target.x + target.hitbox_x
            ty = target.y + target.hitbox_y
            if (abs(tx - hx)**2 + abs(ty - hy)**
                    2)**0.5 <= self.hitbox_d + target.hitbox_d + eps:
                return True
            else:
                return False

        for i in game.group:
            if i.text[0] == 'enemy' or i.text[0] == 'bullet':
                if collide(i):
                    self.dead()
                elif collide(i, 20):
                    if self.graze == 0:
                        self.graze = 5
                        pygame.mixer.Sound('audio/graze.wav').play()
                        game.score += 5
                    else:
                        game.score += 1

    def dead(self):
        global game
        pygame.mixer.Sound('audio/dead.wav').play()
        game.life -= 1
        self.respawn = 60
        self.x = 640
        self.y = 640


class Enemy(Sprite):

    def __init__(self, x, y, hp=3):
        Sprite.__init__(self, x, y, 'enemy.png', 100, 30, 30, 30, ['enemy', 0])
        self.hp = hp

    def game_event(self):
        if self.rect.top > 768 or self.rect.bottom < 0 or self.rect.left > 1360 or self.rect.right < 0:
            self.trash()
        if self.hp <= 0:
            self.dead()
        if self.tick < 120:
            self.y += 2
        else:
            self.y += 4

    def dead(self):
        global game
        if random.randint(0,3) == 0:
            game.group.append(Point(self.x+random.randint(-10, 10), self.y+random.randint(-10, 10)))
        pygame.mixer.Sound('audio/kill.wav').play()
        self.trash()

class BigEnemy(Sprite):

    def __init__(self, x, y, hp=10):
        Sprite.__init__(self, x, y, 's_enemy.png', 150, 45, 45, 40, ['enemy', 1])
        self.hp = hp

    def game_event(self):
        if self.rect.top > 768 or self.rect.bottom < 0 or self.rect.left > 1360 or self.rect.right < 0:
            self.trash()
        if self.hp <= 0:
            self.dead()
        if self.tick < 120:
            self.y += 1
        else:
            self.y += 2

    def dead(self):
        global game
        for i in range(2):
            if random.randint(0,3) == 0:
                game.group.append(Point(self.x+random.randint(-10, 10), self.y+random.randint(-10, 10)))
        pygame.mixer.Sound('audio/kill.wav').play()
        self.trash()

class Special_BigEnemy_1(Sprite):
    def __init__(self, x, y, hp=25, text=0):
        Sprite.__init__(self, x, y, 's_enemy.png', 200, 60, 60, 60, ['enemy', 2, text])
        self.hp = hp

    def game_event(self):
        if self.rect.top > 768 or self.rect.bottom < 0 or self.rect.left > 1360 or self.rect.right < 0:
            self.trash()
        if self.hp <= 0:
            self.dead()
        if self.tick < 120:
            self.y += 1

    def dead(self):
        global game
        for i in range(5):
            if random.randint(0,3) == 0:
                game.group.append(Point(self.x+random.randint(-10, 10), self.y+random.randint(-10, 10)))
        pygame.mixer.Sound('audio/kill.wav').play()
        self.trash()


class PlayerBullet(Sprite):

    def __init__(self, x, y):
        Sprite.__init__(self, x, y, 'player_bullet.png', 100, 30, 30, 20,
                        ['pbullet', 0])

    def game_event(self):
        if self.rect.top > 768 or self.rect.bottom < 0 or self.rect.left > 1360 or self.rect.right < 0:
            self.trash()
        self.y -= 12
        self.collide_event()

    def collide_event(self):
        global game

        def collide(target):
            hx = self.x + self.hitbox_x
            hy = self.y + self.hitbox_y
            tx = target.x + target.hitbox_x
            ty = target.y + target.hitbox_y
            if (abs(tx - hx)**2 +
                    abs(ty - hy)**2)**0.5 <= self.hitbox_d + target.hitbox_d:
                return True
            else:
                return False

        for i in game.group:
            if i.text[0] == 'enemy':
                if collide(i):
                    i.hp -= 1
                    self.trash()

class Point(Sprite):
    def __init__(self, x, y, p=100):
        Sprite.__init__(self, x, y, 'point.png', 50, 15, 15, 45, ['point', 0])
        self.p = p
        self.a=5

    def game_event(self):
        if self.rect.top > 768 or self.rect.bottom < 0 or self.rect.left > 1360 or self.rect.right < 0:
            self.trash()
        self.y+=self.a
        self.a+=0.1
        self.collide_event()

    def collide_event(self):
        global game

        def collide(target):
            hx = self.x + self.hitbox_x
            hy = self.y + self.hitbox_y
            tx = target.x + target.hitbox_x
            ty = target.y + target.hitbox_y
            if (abs(tx - hx)**2 +
                    abs(ty - hy)**2)**0.5 <= self.hitbox_d + target.hitbox_d:
                return True
            else:
                return False

        for i in game.group:
            if i.text[0] == 'player':
                if collide(i):
                    game.score+=self.p
                    self.trash()



class Game():

    def __init__(self):
        self.screen = pygame.display.set_mode((1360, 768))
        pygame.display.set_caption('YS-STG')

        self.state = 0
        # 0:menu 1:startgame
        self.diff = 0
        self.ph = 0

        self.life = 3
        self.power = 0
        self.score = 0

        self.group = []
        self.clock = pygame.time.Clock()
        self.kb = pygame.key.get_pressed()
        self.tick = 0
        self.gt = 0

        self.sprite_load()

    def sprite_load(self):
        self.group.append(Sprite(image='bg.png', text=['bg']))
        self.group.append(Player())

    def update(self):
        if self.life >= 0:
            keys = pygame.key.get_pressed()
            self.screen.fill((255, 255, 255))
            self.tick += 1

            if self.state == 0:
                self.group[0].image = pygame.image.load(
                    'images/menu.png').convert_alpha()
                if keys[pygame.K_1]:
                    self.state = 1
                    self.diff = 0
                if keys[pygame.K_2]:
                    self.state = 1
                    self.diff = 1
            else:
                self.group[0].image = pygame.image.load(
                    'images/bg.png').convert_alpha()

            if self.state == 1:
                if self.diff == 0:
                    self.easy_game_start()
                elif self.diff == 1:
                    self.normal_game_start()

            for i in self.group:
                if i.deleted == True:
                    self.group.remove(i)
                else:
                    i.update(self.screen)

            hud_life = 'LIFE:{0}'.format(self.life)
            hud_life_surface = pygame.font.Font('C:/Windows/Fonts/simhei.ttf',
                                                24).render(
                                                    hud_life, True, (0, 0, 0))
            self.screen.blit(hud_life_surface, (0, 0))
            hud_power = 'POWER:{0}'.format(self.power)
            hud_power_surface = pygame.font.Font('C:/Windows/Fonts/simhei.ttf',
                                                 24).render(
                                                     hud_power, True,
                                                     (0, 0, 0))
            self.screen.blit(hud_power_surface, (0, 20))
            hud_score = 'SCORE:{0}'.format(self.score)
            hud_score_surface = pygame.font.Font('C:/Windows/Fonts/simhei.ttf',
                                                 24).render(
                                                     hud_score, True,
                                                     (0, 0, 0))
            self.screen.blit(hud_score_surface, (0, 40))
        else:
            keys = pygame.key.get_pressed()
            game_over = pygame.image.load(
                'images/game_over.png').convert_alpha()
            self.screen.blit(game_over, (0, 0))
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

    def enemy_spawn(self, ph, tick):
        if self.ph == ph:
            if self.gt >= tick:
                self.gt = 0
                self.ph += 1
                return True
            else:
                self.gt += 1
                return False

    def easy_game_start(self):
        if self.enemy_spawn(0, 120):
            self.group.append(Enemy(640, 0))
        if self.enemy_spawn(1, 120):
            self.group.append(Enemy(540, 0))
            self.group.append(Enemy(640, 0, 6))
            self.group.append(Enemy(740, 0))
        if self.enemy_spawn(2, 120):
            self.group.append(Enemy(390, 0))
            self.group.append(Enemy(540, 0))
            self.group.append(BigEnemy(625, 0))
            self.group.append(Enemy(740, 0))
            self.group.append(Enemy(890, 0))
    
    def normal_game_start(self):
        if self.enemy_spawn(0, 60):
            self.group.append(Enemy(540, 0))
            self.group.append(Enemy(640, 0, 6))
            self.group.append(Enemy(740, 0))
        if self.enemy_spawn(1, 60):
            self.group.append(Enemy(540, 0))
            self.group.append(Enemy(640, 0, 6))
            self.group.append(Enemy(740, 0))
        if self.enemy_spawn(2, 60):
            self.group.append(Enemy(390, 0))
            self.group.append(Enemy(540, 0))
            self.group.append(BigEnemy(625, 0))
            self.group.append(Enemy(740, 0))
            self.group.append(Enemy(890, 0))
        if self.enemy_spawn(3, 90):
            self.group.append(Enemy(390, 0))
            self.group.append(BigEnemy(525, 0))
            self.group.append(Special_BigEnemy_1(610, 0))
            self.group.append(BigEnemy(725, 0))
            self.group.append(Enemy(890, 0))
        f=False
        for i in self.group:
            if i.text==['enemy',2,0]:
                f=True
        if self.ph == 4:
            if self.gt >= 300 or f is False:
                self.gt = 0
                self.ph += 1
            else:
                self.gt += 1
        if self.enemy_spawn(5, 10):
            self.group.append(Enemy(140, 0))
            self.group.append(Enemy(240, 0))
            self.group.append(Enemy(340, 0))
            self.group.append(Enemy(440, 0))
            self.group.append(Enemy(540, 0))
            self.group.append(Enemy(640, 0))
            self.group.append(Enemy(740, 0))
            self.group.append(Enemy(840, 0))
            self.group.append(Enemy(940, 0))
            self.group.append(Enemy(1040, 0))
            self.group.append(Enemy(1140, 0))
            self.group.append(Enemy(1240, 0))
        # print(self.gt,self.ph,f)


def init():
    global game
    pygame.init()
    game = Game()


def handle_event():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


def game_event():
    global game
    game.update()
    pygame.display.update()
    game.clock.tick(60)


if __name__ == '__main__':
    init()
    while True:
        handle_event()
        game_event()