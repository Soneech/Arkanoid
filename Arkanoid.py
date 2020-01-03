import pygame
import random
import os

pygame.init()
size = width, height, = 800, 700
screen = pygame.display.set_mode(size)
screen.fill((99, 235, 235))

running = True

sprite_ball = pygame.sprite.Sprite()
sprite_platform = pygame.sprite.Sprite()
all_sprites = pygame.sprite.Group()
all_sprites.add(sprite_ball)
all_sprites.add(sprite_platform)

top_border = pygame.sprite.Group()
bottom_border = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()

clock = pygame.time.Clock()

def load_image(name):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    return image


class Ball(pygame.sprite.Sprite):
    image = load_image('bomb.png')  #  ЗАГРУЗКА ИЗОБРАЖЕНИЯ В СООТВЕТСТВИИ С ПОКУПКОЙ В ИГРОВОМ МАГАЗИНЕ!!!

    def __init__(self, ball):
        super().__init__(ball)
        self.ball_image = Ball.image
        sprite_ball.image = self.ball_image
        sprite_ball.rect = self.ball_image.get_rect()
        sprite_ball.rect.x = random.randint(0, width)  # НАСТРОИТЬ ТАК, ЧТОБЫ ШАРИК СПАУНИЛСЯ НИЖЕ КУБИКОВ!!!
        sprite_ball.rect.y = random.randint(0, height - 40)
        self.rect = sprite_ball.rect
        self.vx = 2  # скорости по x и y
        self.vy = 2

    def update(self):
        sprite_ball.rect = sprite_ball.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, sprite_platform):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        if pygame.sprite.spritecollideany(self, top_border):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, bottom_border):
            self.vx, self.vy = 0, 0


class Platform(pygame.sprite.Sprite):
    image = load_image('platform.png')
    def __init__(self, platform):
        super().__init__(platform)
        self.platform_image = Platform.image
        sprite_platform.image = self.platform_image
        sprite_platform.rect = self.platform_image.get_rect()
        sprite_platform.rect.x = width // 2 - sprite_platform.rect[2] // 2
        sprite_platform.rect.y = height - 20
        self.rect = sprite_platform.rect
        # self.rect = self.platform_image.get_rect()
        # self.rect.x = width // 2 - self.rect[2] // 2
        # self.rect.y = height - 20

    def move(self):
        pass


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2, pos):
        super().__init__(all_sprites)
        if pos == 'left' or pos == 'right':  # вертикальная стенка
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


Border(5, 5, width - 5, 5, 'top')
Border(5, height - 5, width - 5, height - 5, 'bottom')
Border(5, 5, 5, height - 5, 'left')
Border(width - 5, 5, width - 5, height - 5, 'right')

ball = Ball(all_sprites)  # ДОРАБОТАТЬ!!!!!!!!!!
platform = Platform(all_sprites)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    clock.tick(60)  # ДОРАБОТАТЬ!!!!!!!!!!
    screen.fill((99, 235, 235))
    all_sprites.draw(screen)
    sprite_ball.update()
    pygame.display.flip()

pygame.quit()