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
        self.frenzy_alert_font = pygame.font.SysFont("consolas", 48, bold=True)
        self.player_name = "Jugador"
        self.reset_game()

    def reset_game(self):
        """Reinicia las variables para una nueva partida"""
        self.ground_y = self.S_HEIGHT - 120
        
        # JUGADOR un poco más ancho
        self.player = Player(70, self.ground_y - 64, 34, 64, self.ground_y)
        
        # Variantes de separación: cerca, intermedio 1, intermedio 2, medio, grande
        self.gap_variants = [20, 75, 160, 220, 300]
        self.player_name = getattr(self, "player_name", "Jugador")
        
        # OBSTÁCULOS MÁS DELGADOS
        self.obstacle_types = [(16, 44), (20, 56)]
        self.obstacle_manager = ObstaclePoolManager(self.ground_y, self.obstacle_types)
        self.obstacle_manager.spawn_pair(self.S_WIDTH + 200, self.gap_variants)
        
        self.diagonal_obstacle = None
        self.next_diagonal_trigger = 100
        self.base_speed = 6.6
        self.speed = self.base_speed
        self.score = 0
        
        self.boost_active = False
        self.boost_multiplier = 1.0
        self.next_boost_trigger = 200
        self.boost_duration_points = 100
        self.boost_end_score = 0
        self.frenzy_alert_timer = 0.0
        self.frenzy_alert_active = False
        
        self.last_fps_time = pygame.time.get_ticks()
        self.frames_count = 0
        self.current_fps = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "MENU"
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                if not self.player.space_jumping and not self.player.fast_fall:
                    self.player.jump()
            if event.type == pygame.KEYUP and event.key == pygame.K_w:
                self.player.release_jump()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.player.fast_fall:
                    self.player.stop_space_jump()
                    self.player.start_space_jump()
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.player.stop_space_jump()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                if not self.player.space_jumping and not self.player.holding_jump:
                    self.player.start_fast_fall()
            if event.type == pygame.KEYUP and event.key == pygame.K_s:
                self.player.stop_fast_fall()
        return None

    def update_speed(self, dt):
        """Acelera el juego y activa el modo frenesí según la puntuación."""
        self.speed = self.base_speed + min(4.4, (self.score // 10) * 0.03)

        if self.boost_active:
            self.speed *= 1.35
            self.frenzy_alert_timer += dt
            if self.score >= self.boost_end_score:
                self.boost_active = False
                self.boost_end_score = 0
                self.frenzy_alert_active = False
        elif (self.score // 10) >= self.next_boost_trigger:
            self.boost_active = True
            self.boost_end_score = self.score + self.boost_duration_points
            self.next_boost_trigger += 200
            self.frenzy_alert_active = True
            self.frenzy_alert_timer = 0.0

    def update(self, dt):
        self.frames_count += 1
        curr = pygame.time.get_ticks()
        if curr - self.last_fps_time >= 1000:
            self.current_fps = self.frames_count
            self.frames_count = 0
            self.last_fps_time = curr

        self.update_speed(dt)
        self.player.update()
        self.obstacle_manager.update(self.speed)
        
        if self.obstacle_manager.check_collision(self.player.rect):
            return "MENU" 

        # GENERACIÓN CORREGIDA DE OBSTÁCULOS DIAGONALES
        if (self.score // 10) >= self.next_diagonal_trigger and not self.diagonal_obstacle:
            is_safe = True
            
            # Ahora comprobamos la distancia respecto al PUNTO DE APARICIÓN (S_WIDTH)
            # para asegurarnos de que no spawnee justo encima o detrás de un obstáculo terrestre
            for obs in self.obstacle_manager.active:
                if abs(obs.rect.x - self.S_WIDTH) < 380:
                    is_safe = False
                    break

            if is_safe:
                spawn_x = self.S_WIDTH
                self.diagonal_obstacle = DiagonalObstacle(spawn_x, 30, 30, self.ground_y)
                self.next_diagonal_trigger += 33 if self.boost_active else 67

        if self.diagonal_obstacle:
            self.diagonal_obstacle.update()
            if self.player.rect.colliderect(self.diagonal_obstacle.rect):
                return "MENU"
            if self.diagonal_obstacle.rect.right < 0:
                self.diagonal_obstacle = None

        if not self.obstacle_manager.active:
            self.obstacle_manager.spawn_pair(self.S_WIDTH + random.randint(120, 260), self.gap_variants)

        self.score += 1
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

        boost_state = "Modo Frenesí: ON" if self.boost_active else "Modo Frenesí: OFF"
        boost_text = self.font.render(boost_state, True, (220, 90, 0) if self.boost_active else (100, 100, 100))
        self.screen.blit(boost_text, (20, 56))

        if self.frenzy_alert_active:
            elapsed = self.frenzy_alert_timer
            if elapsed < 0.25:
                scale = 0.8 + elapsed / 0.25 * 1.4
            else:
                scale = 2.2 - (elapsed / 0.7) * 1.5
            scale = max(0.2, min(scale, 2.2))
            text_surface = self.frenzy_alert_font.render("MODO FRENESI", True, (220, 0, 0))
            rect = text_surface.get_rect(center=(self.S_WIDTH // 2, self.S_HEIGHT // 2 - 40))
            scaled_surface = pygame.transform.scale_by(text_surface, scale)
            scaled_rect = scaled_surface.get_rect(center=rect.center)
            self.screen.blit(scaled_surface, scaled_rect)
        
        fps_text = self.font.render(f"FPS: {self.current_fps}", True, (0, 0, 180))
        self.screen.blit(fps_text, (self.S_WIDTH - 140, 20))