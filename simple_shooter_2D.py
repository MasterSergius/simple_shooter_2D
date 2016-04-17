#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import pygame
import sys

from constants import *
from random import randint, choice
from pygame.locals import *


class GameObject(object):
    def __init__(self, x, y):
        self._set_coords(x, y)
        self._width = 0
        self._height = 0

    def _set_coords(self, x, y):
        self._x = x
        self._y = y

    def get_coords(self):
        return self._x, self._y

    def get_round_coords(self):
        return int(round(self._x)), int(round(self._y))

    def get_size(self):
        return self._width, self._height


class Player(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self, x, y)
        self._move_directions = []
        self.shooting = False
        self._width, self._height = PLAYER_IMG.get_size()

    def start_move(self, direction):
        self._move_directions.append(direction)

    def end_move(self, direction):
        self._move_directions.remove(direction)

    def move(self):
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
        self._width, self._height = ENEMY_IMG.get_size()

    def set_move_target(self, targetx, targety):
        """ Set coords of target, which move to """
        self._move_tx = targetx
        self._move_ty = targety

    def move(self):
        x, y = self.get_coords()
        if abs((self._move_tx - x) * (self._move_ty - y)) < self._width:
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

    def take_damage(self, damage):
        self._hp -= damage


class Bullet(GameObject):
    def __init__(self, playerx, playery, targetx, targety, dmg):
        self._set_coords(playerx, playery)
        self._width, self._height = BULLETSIZE, BULLETSIZE
        self._tx = targetx
        self._ty = targety
        self._speed = BULLETSPEED
        angle = math.atan2(self._ty - playery, self._tx - playerx)
        self._dx = int(round(self._speed * math.cos(angle)))
        self._dy = int(round(self._speed * math.sin(angle)))
        self._hit_target = False
        self.dmg = dmg

    def move(self):
        x, y = self.get_coords()
        if abs((self._tx - x) * (self._ty - y)) < BULLETSPEED * BULLETSPEED:
            self._hit_target = True
        if not self._hit_target:
            angle = math.atan2(self._ty - y, self._tx - x)
            self._dx = int(round(self._speed * math.cos(angle)))
            self._dy = int(round(self._speed * math.sin(angle)))
        self._set_coords(x + self._dx, y + self._dy)


class GameLogic(object):
    def __init__(self):
        pygame.init()
        self.displaysurf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.fpsclock = pygame.time.Clock()
        self.font = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
        pygame.display.set_caption('Simple shooting')

    def start(self):
        """ Run game """
        self.enemies = [self.enemy_placing()
                        for i in range(ENEMY_INITIAL_COUNT)]
        self.bullets = []
        self.player = Player(PLAYERSTARTPOSITION[0], PLAYERSTARTPOSITION[1])
        clock_enemies_spawn = 0
        while True:
            # Spawn a new enemy after set time periods
            clock_enemies_spawn += 1
            if clock_enemies_spawn >= ENEMY_SPAWN_TIME:
                clock_enemies_spawn = 0
                self.enemies.append(self.enemy_placing())

            # get and handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    if event.key in (K_UP, K_w):
                        self.player.start_move('up')
                    if event.key in (K_DOWN, K_s):
                        self.player.start_move('down')
                    if event.key in (K_LEFT, K_a):
                        self.player.start_move('left')
                    if event.key in (K_RIGHT, K_d):
                        self.player.start_move('right')
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        terminate()
                    if event.key in (K_UP, K_w):
                        self.player.end_move('up')
                    if event.key in (K_DOWN, K_s):
                        self.player.end_move('down')
                    if event.key in (K_LEFT, K_a):
                        self.player.end_move('left')
                    if event.key in (K_RIGHT, K_d):
                        self.player.end_move('right')
                elif event.type == MOUSEBUTTONDOWN:
                    self.player.set_shooting(True)
                    mousex, mousey = event.pos
                    self.bullets.append(Bullet(playerx, playery, mousex, mousey, BULLETDAMAGE))
                elif event.type == MOUSEBUTTONUP:
                    self.player.set_shooting(False)
            # draw background
            self.displaysurf.blit(TERRAIN_IMG, (0, 0))
            # actions per frame
            playerx, playery = self.player.get_coords()
            if self.player.get_shooting():
                mousex, mousey = pygame.mouse.get_pos()
                self.bullets.append(Bullet(playerx, playery, mousex, mousey, BULLETDAMAGE))
            for bullet in self.bullets:
                bullet.move()
                # remove bullet from list, if bullet is out of window
                pygame.draw.circle(self.displaysurf, BLUE, (bullet.get_coords()), BULLETSIZE)
                if self.is_out_of_window(bullet):
                    self.bullets.remove(bullet)
            self.player.move()
            for enemy in self.enemies:
                enemy.set_move_target(playerx, playery)
                enemy.move()
                self.displaysurf.blit( ENEMY_IMG, (enemy.get_round_coords()) )
            self.check_hits()
            # draw enemies, player and bullets
            self.displaysurf.blit(PLAYER_IMG, (self.player.get_coords()))
            pygame.display.update()
            self.fpsclock.tick(FPS)

    def is_obj_collision(self, obj1, obj2):
        """ Verifies if obj1 and obj2 collide with each other

            Check if distance between centers of objects is less than
            sum of widths of objects (assume, width = height)
        """
        x1, y1 = obj1.get_coords()
        w1, h1 = obj1.get_size()
        x2, y2 = obj2.get_coords()
        w2, h2 = obj2.get_size()

        # rough calculation, needs improvement
        distance = w1 + w2
        x1 = x1 + w1 / 2
        y1 = y1 + h1 / 2
        x2 = x2 + w2 / 2
        y2 = y2 + h2 / 2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) < distance

    def check_hits(self):
        """ Verifies if any bullet hit any enemy.
            Destroys corresponding bullet and enemy on collision.
        """
        bullets_to_remove = []
        enemies_to_remove = []
        for bullet in self.bullets:
            for enemy in self.enemies:
                if bullet not in bullets_to_remove and \
                   enemy not in enemies_to_remove and \
                   self.is_obj_collision(bullet, enemy):
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.append(enemy)
        for bullet in bullets_to_remove:
            self.bullets.remove(bullet)
        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)

    def is_out_of_window(self, obj):
        """ Verifies if any object is out of game window """
        x, y = obj.get_coords()
        if x < 0 or x > WINDOWWIDTH or y < 0 or y > WINDOWHEIGHT:
            return True
        return False

    def enemy_placing(self):
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


def terminate():
    """ Stop game """
    pygame.quit()
    sys.exit()

def main():
    game = GameLogic()
    game.start()

if __name__ == '__main__':
    main()
