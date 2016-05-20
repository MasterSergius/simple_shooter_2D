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
        self._hp = PLAYERHITPOINTS

    def start_move(self, direction):
        self._move_directions.append(direction)

    def end_move(self, direction):
        if direction in self._move_directions:
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

    def take_damage(self, damage):
        self._hp -= damage

    def is_alive(self):
        return self._hp > 0


class Enemy(GameObject):
    def __init__(self, x, y, hp, speed, dmg, img):
        GameObject.__init__(self, x, y)
        self._dx = 0
        self._dy = 0
        self._hit_target = False
        self._hp = hp
        self._speed = speed
        self._dmg = dmg
        self._img = img
        self._width, self._height = img.get_size()

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
        self.font = pygame.font.SysFont('arial', BASICFONTSIZE)
        pygame.display.set_caption('Simple shooting')
        self.game_time = 0
        self.time_text = '0:00'
        self.enemy_kills = 0

    def handle_events(self):
        """ Get and handle events (keyboard, mouse, etc.) """
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
                    self.show_menu(state="pause")
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
            elif event.type == MOUSEBUTTONUP:
                self.player.set_shooting(False)
            elif event.type == USEREVENT+1:
                self.update_timer()

    def show_menu(self, state="init"):
        """ Shows game menu """
        self.displaysurf.blit(TERRAIN_IMG, (0, 0))
        text_exit = "EXIT"
        if state == "init":
            text_play = "PLAY"
        elif state == "pause":
            text_play = "RESUME"
        elif state == "end":
            text_play = "SCORE: %s" % (self.game_time * self.enemy_kills)
            text_exit = "GAME OVER"
        rendered_text_play = self.font.render(text_play, True, (YELLOW))
        rendered_text_exit = self.font.render(text_exit, True, (YELLOW))
        pw, ph = rendered_text_play.get_size()
        px = WINDOWWIDTH / 2 - pw / 2
        py = WINDOWHEIGHT / 2 - ph - 10
        self.displaysurf.blit(rendered_text_play, (px, py))
        ew, eh = rendered_text_exit.get_size()
        ex = WINDOWWIDTH / 2 - ew / 2
        ey = WINDOWHEIGHT / 2 + eh + 10
        self.displaysurf.blit(rendered_text_exit, (ex, ey))
        pygame.display.update()
        while True:
            event = pygame.event.wait()
            if event.type == MOUSEBUTTONDOWN:
                mousex, mousey = pygame.mouse.get_pos()
                if self.mouse_in_rect((mousex, mousey), (px, py, pw, ph)):
                    return state
                if self.mouse_in_rect((mousex, mousey), (ex, ey, ew, eh)):
                    terminate()
            self.fpsclock.tick(FPS)

    def start(self):
        """ Run game """
        self.show_menu()
        # create initial enemies
        self.enemies = []
        speed = ENEMYSPEED / FPS
        for i in range(ENEMY_INITIAL_COUNT):
            x, y = self.enemy_placing()
            self.enemies.append(Enemy(x, y, ENEMYHITPOINTS, speed,
                                      ENEMY_DAMAGE, ENEMY_IMG))
        self.bullets = []
        self.player = Player(PLAYERSTARTPOSITION[0], PLAYERSTARTPOSITION[1])
        clock_enemies_spawn = 0
        firerate_counter = FIRERATE
        pygame.time.set_timer(USEREVENT+1, 1000)
        while True:
            self.handle_events()
            # Spawn a new enemy after set time periods
            clock_enemies_spawn += 1
            if clock_enemies_spawn >= ENEMY_SPAWN_TIME:
                clock_enemies_spawn = 0
                for counter in range(ENEMY_SPAWN_COUNT):
                    x, y = self.enemy_placing()
                    self.enemies.append(Enemy(x, y, ENEMYHITPOINTS, speed,
                                              ENEMY_DAMAGE, ENEMY_IMG))

            # draw background
            self.displaysurf.blit(TERRAIN_IMG, (0, 0))

            # move player, enemies, bullets
            playerx, playery = self.player.get_coords()
            if self.player.get_shooting():
                if firerate_counter >= FIRERATE:
                    firerate_counter = 0
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
            self.check_player_get_damage()
            # draw player, stats, etc.
            self.displaysurf.blit(PLAYER_IMG, (self.player.get_coords()))
            self.displaysurf.blit(self.font.render(self.time_text, True,
                                                   (YELLOW)), (20, 10))
            text_kills = 'Kills: %s' % self.enemy_kills
            self.displaysurf.blit(self.font.render(text_kills, True,
                                                   (YELLOW)),
                                                   (WINDOWWIDTH - 100, 10))
            pygame.display.update()
            if not self.player.is_alive():
                break
            firerate_counter += 1
            if firerate_counter > FIRERATE:
                firerate_counter = FIRERATE
            self.fpsclock.tick(FPS)
        # game over
        self.show_menu(state="end")

    def update_timer(self):
        self.game_time += 1
        mm = self.game_time / 60
        ss = self.game_time % 60
        self.time_text = '%s:%s' % (mm, str(ss).zfill(2))

    def mouse_in_rect(self, mouse, rect):
        """ Verifies if mouse inside rect.

            Params:
                mouse - tuple (x, y)
                rect - represented by tuple (x, y, w, h),
                       where (x, y) - coords of left top corner and
                       (w, h) - width and height of rect
        """
        mousex, mousey = mouse
        x, y, w, h = rect
        return mousex >= x and mousex <= x + w and \
               mousey >= y and mousey <= y + h

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
        distance = (w1 + w2) * 0.8
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
                    self.enemy_kills += 1
        for bullet in bullets_to_remove:
            self.bullets.remove(bullet)
        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)

    def check_player_get_damage(self):
        for enemy in self.enemies:
            if self.is_obj_collision(enemy, self.player):
                self.player.take_damage(ENEMY_DAMAGE)

    def is_out_of_window(self, obj):
        """ Verifies if any object is out of game window """
        x, y = obj.get_coords()
        if x < 0 or x > WINDOWWIDTH or y < 0 or y > WINDOWHEIGHT:
            return True
        return False

    def enemy_placing(self):
        """ Returns coords (x,y) in random part of game field.

            Possible places:
            | topleft | topmid | topright |
            -------------------------------
            | midleft |        | midright |
            -------------------------------
            | botleft | botmid | botright |
        """
        # set size of this grid
        GRID_SIZE = 15
        CELL_WIDTH = WINDOWWIDTH / GRID_SIZE
        CELL_HEIGHT = WINDOWHEIGHT / GRID_SIZE
        places = ('topleft', 'topmid', 'topright',
                  'midleft', 'midright',
                  'bottomleft', 'bottommid', 'bottomright')
        place = choice(places)
        if place == 'topleft':
            x = randint(0, CELL_WIDTH)
            y = randint(0, CELL_HEIGHT)
        if place == 'topmid':
            x = randint(CELL_WIDTH, WINDOWWIDTH - CELL_WIDTH)
            y = randint(0, CELL_HEIGHT)
        if place == 'topright':
            x = randint(WINDOWWIDTH - CELL_WIDTH, WINDOWWIDTH)
            y = randint(0, CELL_HEIGHT)
        if place == 'midleft':
            x = randint(0, CELL_WIDTH)
            y = randint(CELL_HEIGHT, WINDOWHEIGHT - CELL_HEIGHT)
        if place == 'midright':
            x = randint(WINDOWWIDTH - CELL_WIDTH, WINDOWWIDTH)
            y = randint(CELL_HEIGHT, WINDOWHEIGHT - CELL_HEIGHT)
        if place == 'bottomleft':
            x = randint(0, CELL_WIDTH)
            y = randint(WINDOWHEIGHT - CELL_HEIGHT, WINDOWHEIGHT)
        if place == 'bottommid':
            x = randint(CELL_WIDTH, WINDOWWIDTH - CELL_WIDTH)
            y = randint(WINDOWHEIGHT - CELL_HEIGHT, WINDOWHEIGHT)
        if place == 'bottomright':
            x = randint(WINDOWWIDTH - CELL_WIDTH, WINDOWWIDTH)
            y = randint(WINDOWHEIGHT - CELL_HEIGHT, WINDOWHEIGHT)
        return (x, y)


def terminate():
    """ Stop game """
    pygame.quit()
    sys.exit()

def main():
    game = GameLogic()
    game.start()

if __name__ == '__main__':
    main()
