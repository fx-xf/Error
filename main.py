# Импорт библиотек и модулей
import pygame
import sys
import os
from random import randint
from levev_data_base import level

# Инициализация Pygame
pygame.init()

# Инициализация звуковых эффектов
pygame.mixer.init()

# Установка размеров экрана
width, height = 1200, 800

# Размеры игровых объектов
PLAYER_WIDTH, PLAYER_HEIGHT = 18, 44

BOSS_WIDTH, BOSS_HEIGHT = 160, 90

TARGET_WIDTH, TARGET_HEIGHT = 30, 30

CURSOR_SIZE = 40

# Загрузка звуковых эффектов
walk_sound = pygame.mixer.Sound(os.path.join('data', 'sound', 'walk.wav'))

death_sound = pygame.mixer.Sound(os.path.join('data', 'sound', 'death.wav'))

hit_hurt_sound = pygame.mixer.Sound(os.path.join('data', 'sound', 'hitHurt.wav'))

win_sound = pygame.mixer.Sound(os.path.join('data', 'sound', 'win.wav'))

# Создание окна
screen = pygame.display.set_mode((width, height))

pygame.display.set_caption('Error')

# Настройка часов
clock = pygame.time.Clock()

# Класс для создания тайлов (препятствий)
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super(Tile, self).__init__()

        self.image = image

        self.rect = self.image.get_rect()

        self.rect.topleft = (x, y)

# Класс для игрока
class Person(pygame.sprite.Sprite):
    
    # Время последнего воспроизведения звука ходьбы
    last_play_time = 0

    def __init__(self, x, y, max_health=100):
        super(Person, self).__init__()

        # Скорость движения игрока
        self.speed = 5

        # Загрузка изображения игрока
        original_image = pygame.image.load(os.path.join('data', 'person.png'))

        self.image = pygame.transform.scale(original_image, (PLAYER_WIDTH, PLAYER_HEIGHT))

        # Получение прямоугольника, описывающего положение игрока
        self.rect = self.image.get_rect()

        self.rect.topleft = (x, y)

        # Установка максимального и текущего здоровья игрока
        self.max_health = max_health

        self.health = self.max_health

    def update(self, tiles_group, target_down_list):
    
        # Получение нажатых клавиш
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0

        # Обработка нажатий клавиш для движения
        if keys[pygame.K_a]:
            dx = -self.speed

        if keys[pygame.K_d]:
            dx = self.speed

        if keys[pygame.K_w]:
            dy = -self.speed

        if keys[pygame.K_s]:
            dy = self.speed

        # Изменение координат игрока
        self.rect.x += dx

        self.handle_collisions(dx, 0, tiles_group, target_down_list)

        self.rect.y += dy

        self.handle_collisions(0, dy, tiles_group, target_down_list)

        # Воспроизведение звука ходьбы
        current_time = pygame.time.get_ticks()

        if keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]:
         
            current_time = pygame.time.get_ticks()

            # Проверка времени прошедшего с момента последнего воспроизведения звука
            if current_time - Person.last_play_time > 200: 
         
                walk_sound.play()

                # Обновление времени последнего воспроизведения звука
                Person.last_play_time = current_time

        else:
            # Остановка звука ходьбы, если игрок не двигается
            walk_sound.stop()

    def handle_collisions(self, dx, dy, tiles_group, target_down_list):
        # Обработка столкновений с тайлами
        collisions = pygame.sprite.spritecollide(self, tiles_group, False)

        for collision in collisions:

            if dx > 0:
                self.rect.right = collision.rect.left

            elif dx < 0:
                self.rect.left = collision.rect.right

            if dy > 0:
                self.rect.bottom = collision.rect.top

            elif dy < 0:
                self.rect.top = collision.rect.bottom

        # Обработка столкновений с целями
        for target in target_down_list:

            if pygame.sprite.collide_rect(self, target):
                # Уменьшение здоровья игрока при столкновении с целью
                self.health -= 10  

                # Сброс игры, если здоровье игрока меньше или равно 0
                if self.health <= 0:
                    reset_game()

# Класс для босса
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Boss, self).__init__()

        # Загрузка изображения босса
        original_image = pygame.image.load(os.path.join('data', 'boss.png'))

        self.image = pygame.transform.scale(original_image, (BOSS_WIDTH, BOSS_HEIGHT))

        # Получение прямоугольника, описывающего положение босса
        self.rect = self.image.get_rect()

        self.rect.topleft = (x, y)

        # Установка здоровья босса
        self.health = 100

# Класс для цели, которая двигается вниз
class TargetDown(pygame.sprite.Sprite):
    def __init__(self):
        super(TargetDown, self).__init__()

        # Установка начальной позиции цели в случайном месте в верхней части экрана
        self.px, self.py = randint(0, width - TARGET_WIDTH), -100

        # Установка скорости цели
        self.speed = randint(3, 15)

        # Получение прямоугольника, описывающего положение цели
        self.rect = pygame.Rect(self.px, self.py, TARGET_WIDTH, TARGET_HEIGHT)

        # Добавление цели в список целей, которые двигаются вниз
        target_down_list.append(self)
    
    def update(self):
        # Обновление позиции цели
        self.py += self.speed

        self.rect.y = self.py

        # Удаление цели из списка, если она выходит за пределы экрана
        if self.rect.top > height:
            target_down_list.remove(self)

    def draw(self):
        # Отрисовка цели
        pygame.draw.rect(screen, pygame.Color('green'), self.rect) 

    def is_clicked(self, mouse_pos):
        # Проверка, была ли цель кликнута мышью
        return self.rect.collidepoint(mouse_pos)         

# Функция отрисовки курсора
def draw_cursor(screen):
    cursor_image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'cursor.png')), (CURSOR_SIZE, CURSOR_SIZE))

    mouse_x, mouse_y = pygame.mouse.get_pos()

    screen.blit(cursor_image, (mouse_x, mouse_y))

# Функция создания уровня
def create_level(level):
    level_game = level

    all_sprites = pygame.sprite.Group()

    person_group = pygame.sprite.Group()

    level = [
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                       B                   ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                 WWWWWWWWWWWWWWWWWWWW      ",
        "                 W                  W      ",
        "                 W                  W      ",
        "                 W                  W      ",
        "                 W                  W      ",
        "                 W                  W      ",
        "                 W        P         W      ",
        "                 W                  W      ",
        "                 W                  W      ",
        "                 W                  W      ",
        "                 W                  W      ",
        "                 W                  W      ",
        "                 WWWWWWWWWWWWWWWWWWWW      ",
        "                                           ",
        "                                           ",
        "                                           ",
        "                                           ",
    ]

    tiles_group = pygame.sprite.Group()

    tile_size = 22

    for row_index, row in enumerate(level_game):

        for col_index, tile in enumerate(row):
      
            x = col_index * tile_size

            y = row_index * tile_size

            # Создание тайлов в зависимости от символов в описании уровня
            if tile == "W":
      
                wall_image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'wall.png')), (tile_size, tile_size))

                wall_tile = Tile(x, y, wall_image)

                tiles_group.add(wall_tile)

                all_sprites.add(wall_tile)

            elif tile == "P":
      
                person = Person(x, y)

                person_group.add(person)

                all_sprites.add(person)

            elif tile == "B":
      
                boss = Boss(x, y)

                all_sprites.add(boss)

                tiles_group.add(boss)

    return tiles_group, all_sprites, person_group

# Функция отрисовки полоски здоровья босса
def draw_health_bar(screen, boss):
    bar_width = 200

    bar_height = 20

    bar_x = (width - bar_width) // 2

    bar_y = height - 50

    bar_color = (0, 255, 0) 

    outline_color = (255, 255, 255)  

    health_width = (boss.health / 100) * bar_width

    # Отрисовка полоски здоровья
    pygame.draw.rect(screen, outline_color, (bar_x, bar_y, bar_width, bar_height), 2)

    pygame.draw.rect(screen, bar_color, (bar_x, bar_y, health_width, bar_height))

# Функция уменьшения здоровья босса
def decrease_boss_health(boss, amount):
    boss.health -= amount

    # Обработка случая, когда здоровье босса становится меньше 0
    if boss.health < 0:
        boss.health = 0

        # Воспроизведение звука победы
        win_sound.play()

# Функция отображения стартового меню
def start_menu():
    screen.fill((0, 0, 0))  

    font = pygame.font.Font(None, 36)

    text = font.render("Press SPACE to start", True, (0, 255, 0))

    text_rect = text.get_rect(center=(width // 2, height // 2))

    screen.blit(text, text_rect)

    pygame.display.flip()

# Функция сброса игры
def reset_game():
    global person, target_down_list, game_active

    person = Person(0, 0)

    boss.health = 100

    target_down_list = []

    game_active = True

    death_sound.play()

# Функция отображения меню победы
def victory_menu():
    screen.fill((0, 0, 0))  

    font = pygame.font.Font(None, 36)

    text = font.render("You defeated the boss! Press SPACE to play again", True, (0, 255, 0))

    text_rect = text.get_rect(center=(width // 2, height // 2))

    screen.blit(text, text_rect)

    pygame.display.flip()

# Создание объектов игры
person = Person(0, 0)

target_down_list = []

boss = Boss(0, 0)

# Скрытие указателя мыши
pygame.mouse.set_visible(False)

# Создание уровня
tiles_group, all_sprites, person_group = create_level(level)

# Таймеры для появления целей
timer_down1 = 60

timer_down2 = 30

# Флаг активности игры
game_active = False

running = True

# Основной игровой цикл
while running:

    for event in pygame.event.get():
        
        # закрытие окна 
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN \
            and game_active:

            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                for target in target_down_list:

                    if target.is_clicked(mouse_pos):
                        # Уменьшение здоровья босса при клике на цель
                        decrease_boss_health(boss, 20)

                        target_down_list.remove(target)

                        hit_hurt_sound.play()

        elif event.type == pygame.KEYDOWN \
             and not game_active:

            if event.key == pygame.K_SPACE:
                reset_game()

    if game_active:

        # Проверка условий завершения игры
        if person.health <= 0:

            if boss.health > 0:
                reset_game()

        if boss.health <= 0:
            game_active = False

            # Воспроизведение звука победы
            win_sound.play()

            # Отображение меню победы (закомментировано)
            # victory_menu()

        # Обновление таймеров для появления целей
        if timer_down1 > 0:
            timer_down1 -= 1

        else:
            target_down1 = TargetDown()

            timer_down1 = randint(10, 30)

        if timer_down2 > 0:
            timer_down2 -= 1

        else:
            target_down2 = TargetDown()

            timer_down2 = randint(5, 15)

        # Обновление позиций и состояний объектов
        for target in target_down_list:
            target.update()

        person_group.update(tiles_group, target_down_list)

        boss.update()

        # Отрисовка объектов
        screen.fill((0, 0, 0))

        for target in target_down_list:
            target.draw()

        tiles_group.draw(screen)

        all_sprites.draw(screen)

        draw_health_bar(screen, boss) 

        draw_cursor(screen)

    else:
        # Отображение стартового меню
        start_menu()

    pygame.display.flip()

    # Ограничение частоты кадров
    clock.tick(60)

# Завершение работы Pygame и выход из программы
pygame.quit()

sys.exit()