# entities.py
import pygame
import random
from settings import GRAVITY, JUMP_FORCE

class Player:
    def __init__(self, x, y, w, h, ground_y):
        self.rect = pygame.Rect(x, y, w, h)
        self.vy = 0
        self.ground_y = ground_y
        self.holding_jump = False

    def jump(self):
        if self.rect.bottom >= self.ground_y:
            self.vy = JUMP_FORCE
            self.holding_jump = True

    def release_jump(self):
        self.holding_jump = False

    def update(self):
        if self.vy < 0 and self.holding_jump:
            self.vy += GRAVITY * 0.5
        else:
            self.vy += GRAVITY
            
        self.rect.y += self.vy
        
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.vy = 0
            self.holding_jump = False

    def draw(self, screen):
        pygame.draw.rect(screen, (40, 40, 40), self.rect)


class Obstacle:
    def __init__(self, x, w, h, ground_y):
        self.rect = pygame.Rect(x, ground_y - h, w, h)

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 180, 0), self.rect)


class DiagonalObstacle(Obstacle):
    def __init__(self, x, w, h, ground_y, speed_x=10, speed_y=4):
        self.rect = pygame.Rect(x, 0, w, h)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.ground_y = ground_y

    def update(self, speed=None):
        self.rect.x -= self.speed_x
        if self.rect.bottom < self.ground_y:
            self.rect.y += self.speed_y
            if self.rect.bottom > self.ground_y:
                self.rect.bottom = self.ground_y
        else:
            self.rect.bottom = self.ground_y

    def draw(self, screen):
        pygame.draw.rect(screen, (180, 0, 0), self.rect)


class ObstaclePoolManager:
    """Gestiona la memoria y la aleatoriedad de los obstáculos"""
    def __init__(self, ground_y, types):
        self.ground_y = ground_y
        self.types = types
        self.pool = [Obstacle(0, 10, 10, ground_y) for _ in range(6)]
        self.active = []

    def spawn_pair(self, start_x, gap_variants):
        dist = random.choice(gap_variants)
        current_x = start_x
        for _ in range(2):
            w, h = random.choice(self.types)
            if self.pool:
                obs = self.pool.pop()
                obs.rect = pygame.Rect(current_x, self.ground_y - h, w, h)
            else:
                obs = Obstacle(current_x, w, h, self.ground_y)
            self.active.append(obs)
            current_x += w + dist

    def update(self, speed):
        for obs in self.active:
            obs.update(speed)
        for i in range(len(self.active) - 1, -1, -1):
            if self.active[i].rect.right < 0:
                self.pool.append(self.active.pop(i))

    def draw(self, screen):
        for obs in self.active:
            obs.draw(screen)

    def check_collision(self, player_rect):
        return any(player_rect.colliderect(o.rect) for o in self.active)