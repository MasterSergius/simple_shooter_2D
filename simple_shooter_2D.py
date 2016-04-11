import math
import pygame
import sys

from constants import *
from random import randint, choice
from pygame.locals import *


class GameObject():
    def __init__(self, x, y):
        self._set_coords(x, y)

    def on(self):
        raise Exception('You should rewrite this method for child object')

    def off(self):
        raise Exception('You should rewrite this method for child object')

    def _set_coords(self, x, y):
        self._x = x
        self._y = y

    def get_coords(self):
        return self._x, self._y

    def get_round_coords(self):
        return int(round(self._x)), int(round(self._y))

    def get_size(self):
        return self._size


class Player(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self, x, y)
        self._move_directions = []
        self.shooting = False
        self._size = PLAYER_IMG.get_size()[0]

    def on(self):
        DISPLAYSURF.blit(PLAYER_IMG, (self.get_coords()))

    def off(self):
        pygame.draw.rect(DISPLAYSURF, WHITE, (self._x, self._y, PLAYERSIZE,
        PLAYERSIZE))

    def start_move(self, direction):
        self._move_directions.append(direction)

    def end_move(self, direction):
        self._move_directions.remove(direction)

    def move(self):
        self.off()
        x, y = self.get_coords()
        self._dx = 0
        self._dy = 0
        for direction in self._move_directions:
            if direction == 'up':
                self._dy = -PLAYERSPEED
            if direction == 'down':
                self._dy = PLAYERSPEED
            if direction == 'left':
                self._dx = -PLAYERSPEED
            if direction == 'right':
                self._dx = PLAYERSPEED
        self._set_coords(x + self._dx, y + self._dy)
        self.on()

    def set_shooting(self, status):
        self.shooting = status

    def get_shooting(self):
        return self.shooting


class Enemy(GameObject):
    def __init__(self, x, y, hp):
        GameObject.__init__(self, x, y)
        self._speed = ENEMYSPEED / FPS
        self._dx = 0
        self._dy = 0
        self._hit_target = False
        self._hp = hp
        self._size = ENEMY_IMG.get_size()[0]

    def on(self):
        DISPLAYSURF.blit(ENEMY_IMG, (self.get_round_coords()))

    def off(self):
        x, y = self.get_round_coords()
        pygame.draw.rect(DISPLAYSURF, WHITE, (x, y, self._size, self._size))

    def set_move_target(self, targetx, targety):
        """ Set coords of target, which move to """
        self._move_tx = targetx
        self._move_ty = targety

    def move(self):
        self.off()
        x, y = self.get_coords()
        if abs((self._move_tx - x) * (self._move_ty - y)) < self._size:
            self._hit_target = True
            self._dx = 0
            self._dy = 0
        else:
            self._hit_target = False
        if not self._hit_target:
            angle = math.atan2(self._move_ty - y, self._move_tx - x)
            self._dx = self._speed * math.cos(angle)
            self._dy = self._speed * math.sin(angle)
        self._set_coords(x + self._dx, y + self._dy)
        self.on()

    def take_damage(self, damage):
        self._hp -= damage


class Bullet(GameObject):
    def __init__(self, playerx, playery, targetx, targety, dmg):
        self._set_coords(playerx, playery)
        self._tx = targetx
        self._ty = targety
        self._speed = BULLETSPEED
        angle = math.atan2(self._ty - playery, self._tx - playerx)
        self._dx = int(round(self._speed * math.cos(angle)))
        self._dy = int(round(self._speed * math.sin(angle)))
        self._hit_target = False
        self.dmg = dmg
        self.on()

    def on(self):
        pygame.draw.circle(DISPLAYSURF, BLUE, (self._x, self._y), BULLETSIZE)

    def off(self):
        pygame.draw.circle(DISPLAYSURF, WHITE, (self._x, self._y), BULLETSIZE)

    def move(self):
        self.off()
        x, y = self.get_coords()
        if abs((self._tx - x) * (self._ty - y)) < BULLETSPEED * BULLETSPEED:
            self._hit_target = True
        if not self._hit_target:
            angle = math.atan2(self._ty - y, self._tx - x)
            self._dx = int(round(self._speed * math.cos(angle)))
            self._dy = int(round(self._speed * math.sin(angle)))
        self._set_coords(x + self._dx, y + self._dy)
        self.on()


def is_out_of_window(obj):
    """ Verifies if any object is out of game window """
    x, y = obj.get_coords()
    if x < 0 or x > WINDOWWIDTH or y < 0 or y > WINDOWHEIGHT:
        return True
    return False

def terminate():
    """ Stop game """
    pygame.quit()
    sys.exit()

def enemy_placing():
    """ Place each new enemy into random part of game field.

        Possible places:
        | topleft | topmid | topright |
        ------------------------------
        | midleft |        | midright |
        ------------------------------
        | botleft | botmid | botright |
    """
    places = ('topleft', 'topmid', 'topright',
              'midleft', 'midright',
              'bottomleft', 'bottommid', 'bottomright')
    place = choice(places)
    if place == 'topleft':
        x = randint(0, WINDOWWIDTH / 3)
        y = randint(0, WINDOWHEIGHT / 3)
    if place == 'topmid':
        x = randint(WINDOWWIDTH / 3, 2 * WINDOWWIDTH / 3)
        y = randint(0, WINDOWHEIGHT / 3)
    if place == 'topright':
        x = randint(2 * WINDOWWIDTH / 3, WINDOWWIDTH)
        y = randint(0, WINDOWHEIGHT / 3)
    if place == 'midleft':
        x = randint(0, WINDOWWIDTH / 3)
        y = randint(WINDOWHEIGHT / 3, 2 * WINDOWHEIGHT / 3)
    if place == 'midright':
        x = randint(2 * WINDOWWIDTH / 3, WINDOWWIDTH)
        y = randint(WINDOWHEIGHT / 3, 2 * WINDOWHEIGHT / 3)
    if place == 'bottomleft':
        x = randint(0, WINDOWWIDTH / 3)
        y = randint(2 * WINDOWHEIGHT / 3, WINDOWHEIGHT)
    if place == 'bottommid':
        x = randint(WINDOWWIDTH / 3, 2 * WINDOWWIDTH / 3)
        y = randint(2 * WINDOWHEIGHT / 3, WINDOWHEIGHT)
    if place == 'bottomright':
        x = randint(2 * WINDOWWIDTH / 3, WINDOWWIDTH)
        y = randint(2 * WINDOWHEIGHT / 3, WINDOWHEIGHT)
    enemy = Enemy(x, y, ENEMYHITPOINTS)
    return enemy

def check_hits(bullets, enemies):
    """ Verifies if any bullet hit any enemy.
        Destroys corresponding bullet and enemy on collision.
    """
    for bullet in bullets:
        for enemy in enemies:
            bx, by = bullet.get_coords()
            ex, ey = enemy.get_coords()
            es = enemy.get_size()
            if bx >= ex and bx <= ex + es and by >= ey and by <= ey + es:
                enemy.take_damage(bullet.dmg)
                bullets.remove(bullet)
                bullet.off()
                if enemy._hp <= 0:
                    enemies.remove(enemy)
                    enemy.off()

def main():
    global DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Simple shooting')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # temporary replacement of enemies with "magic numbers"
    enemies = [enemy_placing() for i in range(20)]
    bullets = []
    player = Player(PLAYERSTARTPOSITION[0], PLAYERSTARTPOSITION[1])
    clock_enemies_spawn = 0
    while True:
        # Spawn a new enemy after set time periods
        clock_enemies_spawn += 1
        if clock_enemies_spawn >= ENEMY_SPAWN_TIME:
            clock_enemies_spawn = 0
            enemies.append(enemy_placing())
        DISPLAYSURF.fill(WHITE)
        player.on()
        playerx, playery = player.get_coords()
        # get and handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    player.start_move('up')
                if event.key in (K_DOWN, K_s):
                    player.start_move('down')
                if event.key in (K_LEFT, K_a):
                    player.start_move('left')
                if event.key in (K_RIGHT, K_d):
                    player.start_move('right')
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
                if event.key in (K_UP, K_w):
                    player.end_move('up')
                if event.key in (K_DOWN, K_s):
                    player.end_move('down')
                if event.key in (K_LEFT, K_a):
                    player.end_move('left')
                if event.key in (K_RIGHT, K_d):
                    player.end_move('right')
            elif event.type == MOUSEBUTTONDOWN:
                player.set_shooting(True)
                mousex, mousey = event.pos
                bullets.append(Bullet(playerx, playery, mousex, mousey, BULLETDAMAGE))
            elif event.type == MOUSEBUTTONUP:
                player.set_shooting(False)
        # actions per frame
        if player.get_shooting():
            mousex, mousey = pygame.mouse.get_pos()
            bullets.append(Bullet(playerx, playery, mousex, mousey, BULLETDAMAGE))
        for bullet in bullets:
            bullet.move()
            # remove bullet from list, if bullet is out of window
            bullet.on()
            if is_out_of_window(bullet):
                bullets.remove(bullet)
                bullet.off()
        player.move()
        for enemy in enemies:
            enemy.set_move_target(playerx, playery)
            enemy.move()
        check_hits(bullets, enemies)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

if __name__ == '__main__':
    main()
