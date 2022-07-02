import os

import pygame
import random

# 定义常量
W, H = 288, 512
FPS = 30

pygame.init()
SCREEN = pygame.display.set_mode((W, H))
pygame.display.set_caption('YuFan编程FlappyBrid')
CLOCK = pygame.time.Clock()

# bird = pygame.image.load('resources/images/redbird-midflap.png')
#
# bgpic = pygame.image.load('resources/images/background-day.png')
# guide = pygame.image.load('resources/images/message.png')
# floor = pygame.image.load('resources/images/base.png')
# pipe = pygame.image.load('resources/images/pipe-green.png')
# gameover = pygame.image.load('resources/images/gameover.png')
IMAGES = {}
for image in os.listdir('resources/images'):
    name, extension = os.path.splitext(image)
    path = os.path.join('resources/images', image)
    IMAGES[name] = pygame.image.load(path)

FLOOR_Y = H - IMAGES['base'].get_height()
start = pygame.mixer.Sound('resources/audios/swoosh.wav')
die = pygame.mixer.Sound('resources/audios/die.wav')
hit = pygame.mixer.Sound('resources/audios/hit.wav')
point = pygame.mixer.Sound('resources/audios/point.wav')
fly = pygame.mixer.Sound('resources/audios/wing.wav')


def main():
    while True:
        start.play()
        IMAGES['background'] = IMAGES[random.choice(['background-day', 'background-night'])]
        color = random.choice(['redbird', 'yellowbird', 'bluebird'])
        IMAGES['bird'] = [IMAGES[color + '-upflap'], IMAGES[color + '-midflap'], IMAGES[color + '-downflap']]
        pipe = IMAGES[random.choice(['pipe-green', 'pipe-red'])]
        IMAGES['pipe'] = [pipe, pygame.transform.flip(pipe, False, True)]
        menu_window()
        result = game_window()
        end_window(result)


def menu_window():
    # 地板移动出现视觉移动效果
    floor_gap = IMAGES['base'].get_width() - W
    floor_x = 0

    guide_x = (W - IMAGES['message'].get_width()) / 2
    guide_y = (FLOOR_Y - IMAGES['message'].get_height()) / 2
    bird_x = W * 0.2
    bird_y = (H - IMAGES['bird'][0].get_height()) / 2
    # 菜单界面小鸟浮动
    bird_y_vel = 1
    bird_y_range = [bird_y - 8, bird_y + 8]

    # 小鸟拍动翅膀
    idx = 0
    repeat = 5
    frames = [0] * repeat + [1] * repeat + [2] * repeat + [1] * repeat

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

        floor_x -= 4
        if floor_x <= -floor_gap:
            floor_x = 0

        bird_y += bird_y_vel
        if bird_y < bird_y_range[0] or bird_y > bird_y_range[1]:
            # 上线浮动关键代码
            bird_y_vel *= -1

        # 翅膀浮动关键代码
        idx += 1
        idx %= len(frames)

        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(IMAGES['base'], (floor_x, FLOOR_Y))
        SCREEN.blit(IMAGES['message'], (guide_x, guide_y))
        SCREEN.blit(IMAGES['bird'][frames[idx]], (bird_x, bird_y))
        SCREEN.blit(IMAGES['tip'], (20, 20))
        pygame.display.update()
        CLOCK.tick(FPS)


def game_window():
    fly.play()
    score = 0
    floor_gap = IMAGES['base'].get_width() - W
    floor_x = 0

    bird = Bird(W * 0.2, H * 0.4)
    distance = 150
    n_pairs = 4
    pipe_gap = 100
    pipe_group = pygame.sprite.Group()
    for i in range(n_pairs):
        # 随机水管长度0.3-0.7
        pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
        pipe_up = Pipe(W + i * distance, pipe_y, True)
        pipe_down = Pipe(W + i * distance, pipe_y - pipe_gap, False)
        pipe_group.add(pipe_up)
        pipe_group.add(pipe_down)
    # pipe = Pipe(W, H * 0.5)

    while True:
        flap = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fly.play()
                    return
                elif event.key == pygame.K_UP:
                    flap = True
                    fly.play()
                elif event.key == pygame.K_w:
                    point.play()

        floor_x -= 4
        if floor_x <= -floor_gap:
            floor_x = 0

        bird.update(flap)

        first_pipe_up = pipe_group.sprites()[0]
        first_pipe_down = pipe_group.sprites()[1]
        if first_pipe_up.rect.right < 0:
            pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
            new_pipe_up = Pipe(first_pipe_up.rect.x + n_pairs * distance, pipe_y, True)
            new_pipe_down = Pipe(first_pipe_down.rect.x + n_pairs * distance, pipe_y - pipe_gap, False)
            pipe_group.add(new_pipe_up)
            pipe_group.add(new_pipe_down)
            first_pipe_up.kill()
            first_pipe_down.kill()

        pipe_group.update()

        # 判断如何输掉比赛+碰撞测试
        if bird.rect.y > FLOOR_Y or bird.rect.y < 0 or pygame.sprite.spritecollideany(bird, pipe_group):
            bird.dying = True
            hit.play()
            die.play()
            result = {'bird': bird, 'pipe_group': pipe_group, 'score': score}
            return result

        if bird.rect.left + first_pipe_up.x_vel < first_pipe_up.rect.centerx < bird.rect.left:
            point.play()
            score += 1

        # 碰撞代码
        # for pipe in pipe_group.sprites():
        #     right_to_left = max(bird.rect.right, pipe.rect.right) - min(bird.rect.left, pipe.rect.left)
        #     bottom_to_top = max(bird.rect.bottom, pipe.rect.bottom) - min(bird.rect.top, pipe.rect.top)
        #     if right_to_left < bird.rect.width + pipe.rect.width and bottom_to_top < bird.rect.height + pipe.rect.height:
        #         hit.play()
        #         die.play()
        #         result = {'bird': bird, 'pipe_group': pipe_group}
        #         return result

        SCREEN.blit(IMAGES['background'], (0, 0))
        pipe_group.draw(SCREEN)
        SCREEN.blit(IMAGES['base'], (floor_x, FLOOR_Y))
        show_score(score)
        SCREEN.blit(bird.image, bird.rect)
        pygame.display.update()
        CLOCK.tick(FPS)


def end_window(result):
    # floor_gap = IMAGES['base'].get_width() - W
    # floor_x = 0

    gameover_x = (W - IMAGES['gameover'].get_width()) / 2
    gameover_y = (FLOOR_Y - IMAGES['gameover'].get_height()) / 2

    bird = result['bird']
    pipe_group = result['pipe_group']

    # bird = Bird(W * 0.5, H * 0.3)

    while True:
        if bird.dying:
            bird.go_die()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return

        # floor_x -= 4
        # if floor_x <= -floor_gap:
        #     floor_x = 0

        bird.go_die()

        SCREEN.blit(IMAGES['background'], (0, 0))
        pipe_group.draw(SCREEN)
        SCREEN.blit(IMAGES['base'], (0, FLOOR_Y))
        SCREEN.blit(IMAGES['gameover'], (gameover_x, gameover_y))
        show_score(result['score'])
        SCREEN.blit(bird.image, bird.rect)
        pygame.display.update()
        CLOCK.tick(FPS)


def show_score(score):
    score_str = str(score)
    n = len(score_str)
    w = IMAGES['0'].get_width() * 1.1
    x = (W - n * w) / 2
    y = H * 0.1
    for number in score_str:
        SCREEN.blit(IMAGES[number], (x, y))
        x += w


class Bird:
    def __init__(self, x, y):
        self.frames = [0] * 5 + [1] * 5 + [2] * 5 + [1] * 5
        self.idx = 0
        self.images = IMAGES['bird']
        self.image = self.images[self.frames[self.idx]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.y_vel = -10
        self.max_y_vel = 10
        self.gravity = 1
        self.rotate = 45
        self.max_rotate = -20
        self.rotate_vel = -3
        self.y_vel_after_flap = -10
        self.rotate_after_flap = 45
        self.dying = False

    def update(self, flap=False):
        if flap:
            self.y_vel = self.y_vel_after_flap
            self.rotate = self.rotate_after_flap

        self.y_vel = min(self.y_vel + self.gravity, self.max_y_vel)
        self.rect.y += self.y_vel
        self.rotate = max(self.rotate + self.rotate_vel, self.max_rotate)

        self.idx += 1
        self.idx %= len(self.frames)
        self.image = self.images[self.frames[self.idx]]
        self.image = pygame.transform.rotate(self.image, self.rotate)

    def go_die(self):
        if self.rect.y < FLOOR_Y:
            self.rect.y += self.max_y_vel
            self.rotate = -90
            self.image = self.images[self.frames[self.idx]]
            self.image = pygame.transform.rotate(self.image, self.rotate)
        else:
            self.dying = False


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, upwards=True):
        pygame.sprite.Sprite.__init__(self)
        if upwards:
            self.image = IMAGES['pipe'][0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.top = y
        else:
            self.image = IMAGES['pipe'][1]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y
        self.x_vel = -4

    def update(self):
        self.rect.x += self.x_vel


if __name__ == '__main__':
    main()
