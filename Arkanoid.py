import pygame
import os
import sqlite3
import csv
import time
from random import choice

pygame.init()
title = 'Arkanoid'
pygame.display.set_caption(title)
size = width, height, = 890, 650
screen = pygame.display.set_mode(size)

running = True
sprite_ball = pygame.sprite.Group()
sprite_platform = pygame.sprite.Group()
sprite_blocks = []  # список блоков-спрайтов

top_border = pygame.sprite.Group()
bottom_border = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()

clock = pygame.time.Clock()


def load_image(name):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    return image


class DataBase:
    def __init__(self):
        fullname = os.path.join('data', 'DataBaseAndLevelsMaps', 'DataBase.db')
        self.data_base = sqlite3.connect(fullname)
        self.data_base_cur = self.data_base.cursor()


class MainMenu:
    def __init__(self):
        self.background = load_image('background.png')
        screen.blit(self.background, (0, 0))
        screen.blit(game.title_font.render('A R K A N O I D', True, game.title_color), (328, 130))

        self.open_levels_menu_button = load_image('startButton.png')
        screen.blit(self.open_levels_menu_button, (355, 230))

        self.exit_button = load_image('exitButton.png')
        screen.blit(self.exit_button, (355, 345))

        self.buttons_rect = self.open_levels_menu_button.get_rect()

    def button_check(self, x, y):  # координаты клика
        # (355;230) - координаты кнопки play в главном меню
        if ((x > 355 and x < 355 + game.main_menu.buttons_rect[2]) and
                (y > 230 and y < 230 + game.main_menu.buttons_rect[3])):
            return 'play'
        # (355;345) - координаты кнопки exit в главном меню
        if ((x > 355 and x < 355 + game.main_menu.buttons_rect[2]) and
                (y > 345 and y < 345 + game.main_menu.buttons_rect[3])):
            return 'exit'


class LevelsMenu(DataBase):
    def __init__(self):
        super().__init__()
        self.background = load_image('background.png')
        screen.blit(self.background, (0, 0))

        self.start_game_button = load_image('startLevelButton.png')

        self.back_button = load_image('backButton.png')
        self.buttons_rect = self.start_game_button.get_rect()

        self.buttons_data = self.data_base.execute('SELECT x, y FROM Levels').fetchall()
        for coord in self.buttons_data:
            x, y = coord
            screen.blit(self.start_game_button, (x, y))
        screen.blit(self.back_button, (100, 500))

        screen.blit(game.font.render('Time', True, game.text_color), (380, 30))
        screen.blit(game.font.render('Lives', True, game.text_color), (600, 30))

        self.scores = self.data_base.execute('SELECT level, time, lives FROM User_scores').fetchall()

    def load_scores_table(self):
        if len(self.scores) != 0:
            for elem in self.scores:
                level, time, lives = elem
                screen.blit(game.font.render(time, True, game.text_color), (380, 120 + 95 * int(level - 1)))
                screen.blit(game.font.render(str(lives), True, game.text_color), (615, 120 + 95 * int(level - 1)))

    def add_result_to_db(self, level_num, time, lives, start_lives):  # level_num - номер уровня, начиная с 0
        new_minutes = str(time // 60)
        new_seconds = str(time % 60)
        if int(new_minutes) < 10:
            new_minutes = '0' + new_minutes + ':'
        if int(new_seconds) < 10:
            new_seconds = '0' + new_seconds
        new_time = new_minutes + new_seconds
        new_lives = start_lives - lives  # т.е. потраченные жизни

        if len(self.scores) >= level_num + 1:
            scores = list(self.scores[level_num])
            old_time = scores[1].split(':')
            old_minutes = int(old_time[0])
            old_seconds = int(old_time[1])
            old_time = old_minutes * 60 + old_seconds
            if time < old_time:
                self.data_base_cur.execute('UPDATE User_scores SET time=? WHERE level=?', (new_time, level_num + 1))

            old_lives = scores[2]
            if new_lives < old_lives:
                self.data_base_cur.execute('UPDATE User_scores SET lives=? WHERE level=?', (new_lives, level_num + 1))

        else:
            self.data_base_cur.execute('INSERT INTO User_scores(level, time, lives) VALUES(?,?,?)',
                                       (level_num + 1, new_time, new_lives))

        self.data_base.commit()
        self.load_scores_table()

    def start_buttons_check(self, x, y):  # x и y - координаты клика, x1 и y1 - координаты кнопок
        if ((x > x1 and x < x1 + game.levels_menu.buttons_rect[2]) and
                (y >= y1 and y <= y1 + game.levels_menu.buttons_rect[3])):
            return 'start'

    def back_button_ckeck(self, x, y):  # x, y - координаты клика
        if ((x > 100 and x < 100 + game.main_menu.buttons_rect[2]) and
                (y > 500 and y < 500 + game.main_menu.buttons_rect[3])):
            return 'back'


class Ball(pygame.sprite.Sprite):
    image = load_image('ball.png')

    def __init__(self, ball):
        super().__init__(ball)
        self.ball_image = Ball.image
        self.rect = self.ball_image.get_rect()
        self.vx = 3  # скорости по x и y
        self.vy = 3

    def update(self):
        if not game.level.ball_move:  # если движение шарика не начато, он должен находиться на платформе
            self.rect.x = game.platform.rect.x + 63
            self.rect.y = game.platform.rect.y - self.rect[3]
            self.vx = choice([-3, 3])
        else:
            self.rect = self.rect.move(self.vx, self.vy)
            if pygame.sprite.spritecollideany(self, sprite_platform):  # столкновение с платформой
                self.vy = -self.vy

            if pygame.sprite.spritecollideany(self, vertical_borders):  # с боковыми стенками
                self.vx = -self.vx

            if pygame.sprite.spritecollideany(self, top_border):
                self.vy = -self.vy

            if pygame.sprite.spritecollideany(self, bottom_border):
                game.level.ball_fell()

            for i, sprite_block in enumerate(sprite_blocks):
                if pygame.sprite.spritecollideany(self, sprite_block):
                    self.vy = -self.vy
                    game.level.break_blocks(i)


class Platform(pygame.sprite.Sprite):
    image = load_image('platform.png')

    def __init__(self, platform):
        super().__init__(platform)
        self.add(platform)
        self.platform_image = Platform.image
        self.rect = self.platform_image.get_rect()
        self.rect.x = width // 2 - self.rect[2] // 2
        self.rect.y = (height - 80)

    def update(self):
        x, y = pygame.mouse.get_pos()
        if x < 5:  # платформа не может заходить за установленные границы
            x = 5
        elif x > width - 5 - self.rect[2]:
            x = width - 5 - self.rect[2]
        self.rect.x = x  # платформа перемещается только горизонатльно


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2, pos):
        super().__init__(sprite_ball)
        if pos == 'left' or pos == 'right':  # вертикальные стенки
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        elif pos == 'top':  # верхняя стенка
            self.add(top_border)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
        else:
            self.add(bottom_border)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class YellowBlock(pygame.sprite.Sprite):
    image = load_image('yellowBlock.png')

    def __init__(self, block, x, y):
        super().__init__(block)
        self.add(block)
        self.block_image = YellowBlock.image
        self.rect = self.block_image.get_rect()
        self.rect.x = self.rect[2] * x + 6
        self.rect.y = self.rect[3] * y + 50
        sprite_blocks.append(block)


class BlueBlock(pygame.sprite.Sprite):
    image = load_image('blueBlock.png')

    def __init__(self, block, x, y):
        super().__init__(block)
        self.add(block)
        self.block_image = BlueBlock.image
        self.rect = self.block_image.get_rect()
        self.rect.x = self.rect[2] * x + 6
        self.rect.y = self.rect[3] * y + 50
        sprite_blocks.append(block)


class VioletBlock(pygame.sprite.Sprite):
    image = load_image('violetBlock.png')

    def __init__(self, block, x, y):
        super().__init__(block)
        self.add(block)
        self.block_image = VioletBlock.image
        self.rect = self.block_image.get_rect()
        self.rect.x = self.rect[2] * x + 6
        self.rect.y = self.rect[3] * y + 50
        sprite_blocks.append(block)


class PurpleBlock(pygame.sprite.Sprite):
    image = load_image('purpleBlock.png')

    def __init__(self, block, x, y):
        super().__init__(block)
        self.add(block)
        self.block_image = PurpleBlock.image
        self.rect = self.block_image.get_rect()
        self.rect.x = self.rect[2] * x + 6
        self.rect.y = self.rect[3] * y + 50
        sprite_blocks.append(block)


class Level(DataBase, pygame.sprite.Sprite):
    def __init__(self, level_num):  # level_num - номер уровня, начиная с 0
        super().__init__()
        self.level_info = self.data_base.execute('SELECT num, map, fps, lives FROM Levels').fetchall()
        self.level_info = list(self.level_info[level_num])
        self.start_time = None
        self.ball_move = False
        screen.fill((41, 41, 41))
        self.load_level(level_num)

    def load_level(self, level_num):
        self.level_num = level_num
        self.level_map_file = self.level_info[1]
        self.fps = self.level_info[2]
        self.lives = self.level_info[3]
        self.start_lives = self.lives
        self.balls = []  # список изображений шарика(показывает оставшиеся жизни)
        for i in range(self.lives):  # в основном цикле идёт отрисовка
            ball_image = load_image('ball.png')
            self.balls.append([ball_image, width - 45 - 30 * i, 5])

        with open('data/DataBaseAndLevelsMaps/' + self.level_map_file, encoding='utf-8-sig') as file:
            level_map = list(csv.reader(file))
            for y, row in enumerate(level_map):
                for x, block_style in enumerate(row[0]):
                    if block_style == 'y':
                        YellowBlock(pygame.sprite.Group(), x, y)
                    elif block_style == 'b':
                        BlueBlock(pygame.sprite.Group(), x, y)
                    elif block_style == 'v':
                        VioletBlock(pygame.sprite.Group(), x, y)
                    elif block_style == 'p':
                        PurpleBlock(pygame.sprite.Group(), x, y)

    def start_timer(self):
        self.start_time = pygame.time.get_ticks() // 1000  # кол-во секунд с момента pygame.init()

    def show_time(self):
        self.time_since_start = (pygame.time.get_ticks() // 1000 - self.start_time)

        self.minutes = self.time_since_start // 60
        self.seconds = self.time_since_start % 60
        minute, seconds = str(self.minutes), str(self.seconds)

        if self.minutes < 10:
            minute = '0' + str(self.minutes) + ':'
        if self.seconds < 10:
            seconds = '0' + str(self.seconds)

        message = 'Time: ' + str(minute) + str(seconds)
        screen.blit(game.font.render(message, True, game.text_color), (20, 2))

    def show_lives(self):
        for ball in self.balls:
            screen.blit(ball[0], (ball[1], ball[2]))

    def ball_fell(self):
        self.ball_move = False
        del self.balls[-1]
        self.lives -= 1  # при падении тратится кол-во попыток
        if self.lives == 0:
            self.game_over()

    def break_blocks(self, i):
        del sprite_blocks[i]
        if len(sprite_blocks) == 0:
            self.win()

    def win(self):
        screen.blit(game.title_font.render('You win!', True, game.win_color), (360, 410))
        pygame.display.flip()
        time.sleep(2)
        game.levels_menu.add_result_to_db(self.level_num, self.time_since_start, self.lives, self.start_lives)
        self.complete_level()

    def game_over(self):
        screen.blit(game.title_font.render('Game over', False, game.fail_color), (360, 410))
        pygame.display.flip()
        time.sleep(2)
        self.complete_level()

    def complete_level(self):
        sprite_blocks.clear()
        self.ball_move = False
        game.start_game = False
        game.open_levels_menu()


class Game(DataBase):
    def __init__(self):
        super().__init__()
        self.ball = Ball(sprite_ball)
        self.platform = Platform(sprite_platform)
        self.compl_levels = 0  # кол-во пройденных уровней начиная с 1

        self.font = pygame.font.SysFont('Sans', 24)
        self.text_color = (73, 248, 254)

        self.title_font = pygame.font.SysFont('Sans', 40, True)  # шрифт для заставки(bold)
        self.title_color = (100, 150, 255)

        self.fail_color = (255, 0, 0)
        self.win_color = (0, 255, 0)

    def open_main_menu(self):
        self.main_menu = MainMenu()
        self.in_menu = True
        self.in_levels_menu = False
        self.start_game = False

    def open_levels_menu(self):
        pygame.mouse.set_visible(True)
        self.in_levels_menu = True
        self.in_menu = False
        self.start_game = False
        self.levels_menu = LevelsMenu()
        self.levels_menu.load_scores_table()

    def start_level(self, level_num):
        pygame.mouse.set_visible(False)
        self.in_levels_menu = False
        self.start_game = True
        self.level = Level(level_num)

    def completed_levels(self):
        # кол-во пройденных уровней начиная с 1
        self.compl_levels = len(self.data_base.execute('SELECT level FROM User_scores').fetchall())

    def change_button_style(self, name, button, coord):  # меняет стиль кнопки
        self.button = button
        self.button = load_image(name)
        screen.blit(self.button, coord)


game = Game()
game.open_main_menu()

Border(5, 50, width - 5, 5, 'top')
Border(5, height - 20, width - 5, height - 20, 'bottom')
Border(5, 50, 5, height - 20, 'left')
Border(width - 5, 50, width - 5, height - 20, 'right')


def pause():
    pause = True
    while pause:
        time = pygame.time.get_ticks() // 1000  # кол-во секунд с момента pygame.init()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # продолжение игры
                    pause = False
                    # время, проведённое "в паузе"
                    pause_time = time - game.level.time_since_start - game.level.start_time
                    game.level.start_time += pause_time

                elif event.key == pygame.K_ESCAPE:  # можно покинуть уровень, не снимая с паузы
                    pause = False
                    game.level.complete_level()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game.in_menu:
                    running = False

                elif game.in_levels_menu:
                    game.open_main_menu()

                elif game.start_game:
                    game.level.complete_level()
            elif event.key == pygame.K_SPACE:
                if game.level.ball_move:
                    pause()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y, = event.pos

            if game.start_game:
                game.level.ball_move = True  # начало движения шарика
                if game.level.lives == game.level.start_lives:  # событие, происходищее только при старте уровня
                    game.level.start_timer()  # начало отсчёта времени

            elif game.in_menu:  # переходы из главного меню
                # получение координат кнопки и её имени(play/exit)
                clicked_button_name = game.main_menu.button_check(x, y)
                if clicked_button_name == 'play':
                    game.open_levels_menu()  # переход в меню уровней

                elif clicked_button_name == 'exit':
                    running = False  # выход из игры

            elif game.in_levels_menu:  # переходы из меню уровней
                # получение координат нажатой кнопки и её имени(start/back)
                for level_num, coord in enumerate(game.levels_menu.buttons_data):
                    if level_num + 1 <= game.compl_levels + 1:  # открывает для прохождения следующий уровень
                        x, y = event.pos
                        x1, y1 = coord  # координаты кнопок
                        clicked_button_name = game.levels_menu.start_buttons_check(x, y)
                        if clicked_button_name == 'start':
                            game.start_level(level_num)

                x, y = event.pos
                clicked_button_name = game.levels_menu.back_button_ckeck(x, y)
                if clicked_button_name == 'back':
                    game.open_main_menu()

        elif event.type == pygame.MOUSEMOTION:  # смена стиля кнопок при наведении на них
            x, y, = event.pos
            if game.in_menu:
                # кнопки главного меню (play, exit)
                hover_button_name = game.main_menu.button_check(x, y)
                if hover_button_name == 'play':
                    # (355;230) - координаты кнопки play в главном меню
                    game.change_button_style('clickedStartButton.png', game.main_menu.open_levels_menu_button,
                                             (355, 230))
                else:
                    game.change_button_style('startButton.png', game.main_menu.exit_button, (355, 230))

                if hover_button_name == 'exit':
                    # (355;345) - координаты кнопки exit в главном меню
                    game.change_button_style('clickedExitButton.png', game.main_menu.open_levels_menu_button,
                                             (355, 345))
                else:
                    game.change_button_style('exitButton.png', game.main_menu.exit_button, (355, 345))

            elif game.in_levels_menu:
                for coord in game.levels_menu.buttons_data:
                    x, y = event.pos
                    x1, y1 = coord  # координаты кнопок
                    hover_button_name = game.levels_menu.start_buttons_check(x, y)
                    if hover_button_name == 'start':
                        game.change_button_style('clickedStartLevelButton.png', game.levels_menu.start_game_button,
                                                 (x1, y1))
                    if not hover_button_name:  # переводит кнопку старта в обычное состояние
                        game.change_button_style('startLevelButton.png', game.levels_menu.start_game_button,
                                                 (x1, y1))
                hover_button_name = game.levels_menu.back_button_ckeck(x, y)
                if hover_button_name == 'back':
                    # (100;500) - координаты кнопки "back", возвращающей в главное меню
                    game.change_button_style('clickedBackButton.png', game.levels_menu.start_game_button,
                                             (100, 500))
                else:
                    game.change_button_style('backButton.png', game.levels_menu.start_game_button,
                                             (100, 500))
    if game.start_game:  # действия во время игры
        screen.fill((29, 34, 41))
        game.level.show_lives()  # отображает жизни(в виде шариков)

        if game.level.start_time:
            game.level.show_time()  # отображает время, прошедшее с начала игры
        else:
            screen.blit(game.font.render('Time: 00:00', True, game.text_color), (20, 2))

        clock.tick(game.level.fps)

        sprite_ball.draw(screen)
        sprite_platform.draw(screen)

        for block in sprite_blocks:
            block.draw(screen)

        sprite_platform.update()
        sprite_ball.update()
    game.completed_levels()

    pygame.display.flip()

pygame.quit()
