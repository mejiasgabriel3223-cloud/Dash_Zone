# game.py
import pygame
import random
from settings import S_WIDTH, S_HEIGHT
from entities import Player, DiagonalObstacle, ObstaclePoolManager

class CarreraDeObstaculos:
    def __init__(self, screen):
        self.screen = screen
        self.S_WIDTH = S_WIDTH
        self.S_HEIGHT = S_HEIGHT
        self.font = pygame.font.SysFont("consolas", 24)
        self.player_name = "Jugador"
        self.reset_game()

    def reset_game(self):
        """Reinicia las variables para una nueva partida"""
        self.ground_y = self.S_HEIGHT - 120
        self.player = Player(70, self.ground_y - 72, 53, 72, self.ground_y)
        
        self.gap_variants = [
            int(self.player.rect.width * 1.2) + 220,
            int(self.player.rect.width * 1.2) + 140,
            int(self.player.rect.width * 1.2) + 20
        ]
        self.player_name = getattr(self, "player_name", "Jugador")
        
        self.obstacle_types = [(34, 48), (38, 66)]
        self.obstacle_manager = ObstaclePoolManager(self.ground_y, self.obstacle_types)
        self.obstacle_manager.spawn_pair(self.S_WIDTH + 200, self.gap_variants)
        
        self.diagonal_obstacle = None
        self.next_diagonal_trigger = 100
        self.speed = 6.6
        self.score = 0
        
        # Variables de FPS
        self.last_fps_time = pygame.time.get_ticks()
        self.frames_count = 0
        self.current_fps = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "MENU"  # Vuelve al menú con Escape
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                self.player.jump()
            if event.type == pygame.KEYUP and event.key == pygame.K_w:
                self.player.release_jump()
        return None

    def update(self, dt):
        # Lógica de FPS
        self.frames_count += 1
        curr = pygame.time.get_ticks()
        if curr - self.last_fps_time >= 1000:
            self.current_fps = self.frames_count
            self.frames_count = 0
            self.last_fps_time = curr

        self.player.update()
        self.obstacle_manager.update(self.speed)
        
        if self.obstacle_manager.check_collision(self.player.rect):
            return "MENU"  # Chocaste, vuelve al menú

        # Lógica de seguridad para el obstáculo diagonal
        if (self.score // 10) >= self.next_diagonal_trigger and not self.diagonal_obstacle:
            is_safe = True
            for obs in self.obstacle_manager.active:
                if 0 < (obs.rect.x - self.player.rect.right) < 250:
                    is_safe = False
                    break
            
            if is_safe:
                self.diagonal_obstacle = DiagonalObstacle(self.S_WIDTH - 40, 32, 32, self.ground_y)
                self.next_diagonal_trigger += 67

        if self.diagonal_obstacle:
            self.diagonal_obstacle.update()
            if self.player.rect.colliderect(self.diagonal_obstacle.rect):
                return "MENU"
            if self.diagonal_obstacle.rect.right < 0:
                self.diagonal_obstacle = None

        if not self.obstacle_manager.active:
            self.obstacle_manager.spawn_pair(self.S_WIDTH + random.randint(120, 260), self.gap_variants)

        self.score += 1
        if self.score % 10 == 0:
            self.speed += 0.01
            
        return None

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.player.draw(self.screen)
        self.obstacle_manager.draw(self.screen)
        
        if self.diagonal_obstacle:
            self.diagonal_obstacle.draw(self.screen)
        
        pygame.draw.line(self.screen, (120, 120, 120), (0, self.ground_y), (self.S_WIDTH, self.ground_y), 2)
        
        score_text = self.font.render(f"Score: {self.score // 10}", True, (0, 0, 0))
        self.screen.blit(score_text, (20, 20))
        
        fps_text = self.font.render(f"FPS: {self.current_fps}", True, (0, 0, 180))
        self.screen.blit(fps_text, (self.S_WIDTH - 140, 20))