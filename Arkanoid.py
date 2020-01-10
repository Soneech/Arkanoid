import pygame
import os
import sqlite3
import csv

pygame.init()
size = width, height, = 810, 600
screen = pygame.display.set_mode(size)

running = True
sprite_ball = pygame.sprite.Group()
sprite_platform = pygame.sprite.Group()
sprite_blocks = []
blocks = []

top_border = pygame.sprite.Group()
bottom_border = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()

clock = pygame.time.Clock()

def load_image(name):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    return image


def open_data_base(name):
    fullname = os.path.join('data', 'data_base&levels_maps', name)
    data_base = sqlite3.connect(fullname)
    return data_base

class DataBase:
    data_base = open_data_base('DataBase.db')

    def __init__(self):
        self.data_base = DataBase.data_base
        self.data_base_cur = self.data_base.cursor()


class MainMenu:
    def __init__(self):
        self.background = load_image('background.png')
        screen.blit(self.background, (0, 0))

        self.open_levels_menu_button = load_image('startButton.png')
        screen.blit(self.open_levels_menu_button, (315, 230))

        self.exit_button = load_image('exitButton.png')
        screen.blit(self.exit_button, (315, 345))

        self.buttons_rect = self.open_levels_menu_button.get_rect()


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
        screen.blit(self.back_button, (65, 459))

        screen.blit(game.font.render('Time', True, game.text_color), (250, 50))
        screen.blit(game.font.render('Lives', True, game.text_color), (400, 50))

    def load_scores_table(self):
        self.scores = self.data_base.execute('SELECT level, time, lives FROM User_scores').fetchall()
        for elem in self.scores:
            level, time, lives = elem

    def click_check(self):
        for elem in self.buttons_data:
            x1, y1 = elem
            return x1, y1

class Ball(pygame.sprite.Sprite):
    image = load_image('ball.png')  #  ЗАГРУЗКА ИЗОБРАЖЕНИЯ В СООТВЕТСТВИИ С ПОКУПКОЙ В ИГРОВОМ МАГАЗИНЕ!!!

    def __init__(self, ball):
        super().__init__(ball)
        self.ball_image = Ball.image
        self.rect = self.ball_image.get_rect()
        self.ball_move = False
        self.vx = 3  # скорости по x и y
        self.vy = 3

    def update(self):
        if not self.ball_move:  # если движение шарика не начато, он должен находиться на платформе
            self.rect.x = game.platform.rect.x
            self.rect.y = game.platform.rect.y - self.rect[3]
        else:
            self.rect = self.rect.move(self.vx, self.vy)
            if pygame.sprite.spritecollideany(self, sprite_platform):  # столкновение с платформой
                self.vy = -self.vy

            if pygame.sprite.spritecollideany(self, vertical_borders):  # с боковыми стенками
                self.vx = -self.vx

            if pygame.sprite.spritecollideany(self, top_border):
                self.vy = -self.vy

            if pygame.sprite.spritecollideany(self, bottom_border):
                self.ball_move = False
                game.level.lives -= 1  # при падении тратится кол-во попыток
                if game.level.lives == 0:
                    sprite_blocks.clear()
                    blocks.clear()
                    self.reset()
                    print('Game over')

            for i, sprite_block in enumerate(sprite_blocks):
                if pygame.sprite.spritecollideany(self, sprite_block):
                    self.vy = -self.vy
                    del sprite_blocks[i]
                    del blocks[i]
                    if len(blocks) == 0:  # ДОРАБОТАТЬ
                        print('You win!')
                        self.reset()

    def reset(self):
        self.ball_move = False
        game.in_levels_menu = True
        game.start_game = False
        game.open_levels_menu()



class Platform(pygame.sprite.Sprite):
    image = load_image('platform.png')

    def __init__(self, platform):
        super().__init__(platform)
        self.add(platform)
        self.platform_image = Platform.image
        self.rect = self.platform_image.get_rect()
        self.rect.x = width // 2 - self.rect[2] // 2
        self.rect.y = (height - 200)

    def update(self):
        x, y = pygame.mouse.get_pos()
        if x < 5:
            x = 5
        elif x > width - 5 - self.rect[2]:
            x = width - 5 - self.rect[2]
        self.rect.x = x


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


class Blocks(pygame.sprite.Sprite):
    image = load_image('block1.png')
    def __init__(self, block, name, x, y):  # ДОРАБОТАТЬ
        super().__init__(block)
        self.add(block)
        self.block_image = Blocks.image
        self.rect = self.block_image.get_rect()
        self.rect.x = self.rect[2] * x + 5
        self.rect.y = self.rect[3] * y + 50
        sprite_blocks.append(block)


class Level(DataBase, pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.level_info = self.data_base.execute('SELECT num, map, fps, lives FROM Levels').fetchall()
        self.level_info = list(self.level_info[0])
        self.start_time = None
        screen.fill((29, 34, 41))


    def load_level(self):
        self.level_num = self.level_info[0]
        self.level_map_file = self.level_info[1]
        self.fps = self.level_info[2]
        self.lives = self.level_info[3]
        self.start_lives = self.lives

        with open('data/data_base&levels_maps/' + self.level_map_file, encoding='utf-8-sig') as file:
            level_map = list(csv.reader(file))
            for y, row in enumerate(level_map):
                for x, elem in enumerate(row[0]):
                    block = Blocks(pygame.sprite.Group(), 'block1.png', x, y)
                    blocks.append(block)

    def start_timer(self):
        self.start_time = pygame.time.get_ticks()  # время старта уровня

    def show_time(self):
        self.time_since_start = (pygame.time.get_ticks() - self.start_time) // 1000

        minute = self.time_since_start // 60
        seconds = self.time_since_start % 60
        if minute < 10:
            minute = '0' + str(minute) + ':'
        if seconds < 10:
            seconds = '0' + str(seconds)

        message = 'Time: ' + str(minute) + str(seconds)
        screen.blit(game.font.render(message, True, game.text_color), (1, 2))

    def show_lives(self):
        lives = 'Lives: ' + str(self.lives)
        screen.blit(game.font.render(lives, True, game.text_color), (741, 2))


class Game:
    def __init__(self):
        self.ball = Ball(sprite_ball)
        self.platform = Platform(sprite_platform)

        self.font = pygame.font.SysFont('Sans', 24)
        self.text_color = (73, 248, 254)  # ДОРАБОТАТЬ

    def open_main_menu(self):
        self.main_menu = MainMenu()
        self.in_menu = True
        self.in_levels_menu = False
        self.start_game = False

    def open_levels_menu(self):
        pygame.mouse.set_visible(True)
        self.in_levels_menu = True
        self.in_menu = False
        self.levels_menu = LevelsMenu()

    def start_level(self):
        pygame.mouse.set_visible(False)
        self.in_levels_menu = False
        self.start_game = True
        self.level = Level()

    def change_button_style(self, name, button, coord):  # меняет стиль кнопки или её состояние
        self.button = button
        self.button = load_image(name)
        screen.blit(self.button, coord)

game = Game()
game.open_main_menu()

Border(5, 50, width - 5, 5, 'top')
Border(5, height - 5, width - 5, height - 5, 'bottom')
Border(5, 50, 5, height - 5, 'left')
Border(width - 5, 50, width - 5, height - 5, 'right')


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y, = event.pos

            if game.start_game:
                game.ball.ball_move = True  # начало движения шарика
                if game.level.lives == game.level.start_lives:  # событие, происходищее только при старте уровня
                    game.level.start_timer()

            elif game.in_menu:  # переходы из главного меню
                # (315;230) - координаты кнопки play в главном меню
                if ((x > 315 and x < 315 + game.main_menu.buttons_rect[2]) and
                    y > 230 and y < 230 + game.main_menu.buttons_rect[3]):
                    game.open_levels_menu()  # переход в меню уровней
                    game.levels_menu.load_scores_table()
                if ((x > 315 and x < 315 + game.main_menu.buttons_rect[2]) and
                    y > 345 and y < 345 + game.main_menu.buttons_rect[3]):
                    running = False  # выход из игры

            elif game.in_levels_menu:  # переходы из меню уровней
                x1, y1 = game.levels_menu.click_check()  # получение координат нажатой кнопки
                if ((x > x1 and x < x1 + game.levels_menu.buttons_rect[2]) and
                        y >= y1 and y <= y1 + game.levels_menu.buttons_rect[3]):
                    game.start_level()
                    game.level.load_level()

                # (65;559) - координаты кнопки "back", возвращающей в главное меню
                if ((x > 65 and x < 65 + game.main_menu.buttons_rect[2]) and
                        y > 459 and y < 459 + game.main_menu.buttons_rect[3]):
                    game.open_main_menu()

        elif event.type == pygame.MOUSEMOTION:  # меняет стиль кнопок при наведении на них
            x, y, = event.pos
            if game.in_menu:  # кнопки главного меню (play, exit)
                if ((x > 315 and x < 315 + game.main_menu.buttons_rect[2]) and
                    y > 230 and y < 230 + game.main_menu.buttons_rect[3]):
                    game.change_button_style('clickedStartButton.png', game.main_menu.open_levels_menu_button,
                                                                                                (315, 230))
                else:
                    game.change_button_style('startButton.png', game.main_menu.exit_button, (315, 230))

                if ((x > 315 and x < 315 + game.main_menu.buttons_rect[2]) and
                        y > 345 and y < 345 + game.main_menu.buttons_rect[3]):
                    game.change_button_style('clickedExitButton.png', game.main_menu.open_levels_menu_button,
                                                                                                (315, 345))
                else:
                    game.change_button_style('exitButton.png', game.main_menu.exit_button, (315, 345))

            elif game.in_levels_menu:
                x1, y1 = game.levels_menu.click_check()  # получение координат нажатой кнопки
                if ((x > x1 and x < x1 + game.levels_menu.buttons_rect[2]) and
                        y >= y1 and y <= y1 + game.levels_menu.buttons_rect[3]):
                    game.change_button_style('clickedStartLevelButton.png', game.levels_menu.start_game_button,
                                                                                                    (x1, y1))
                else:
                    game.change_button_style('startLevelButton.png', game.levels_menu.start_game_button,
                                                                                                (x1, y1))
                if ((x > 65 and x < 65 + game.main_menu.buttons_rect[2]) and
                        y > 459 and y < 459 + game.main_menu.buttons_rect[3]):
                    game.change_button_style('clickedBackButton.png', game.levels_menu.start_game_button,
                                                                                                (65, 459))
                else:
                    game.change_button_style('backButton.png', game.levels_menu.start_game_button,
                                                                                                (65, 459))

    if game.start_game:  # действия во время игры
        screen.fill((29, 34, 41))
        game.level.show_lives()  # отображает жизни

        if game.level.start_time:
            game.level.show_time()  # отображает время, прошедшее с начала игры
        else:
            screen.blit(game.font.render('Time: 00:00', True, game.text_color), (0, 0))

        clock.tick(game.level.fps)

        sprite_ball.draw(screen)
        sprite_platform.draw(screen)

        for el in blocks:
            screen.blit(el.block_image, (el.rect.x, el.rect.y))

        sprite_platform.update()
        sprite_ball.update()

    pygame.display.flip()

pygame.quit()
