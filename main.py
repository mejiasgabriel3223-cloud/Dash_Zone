# main.py
import pygame
import sys
from settings import S_WIDTH, S_HEIGHT, FPS
from menu import EstadoMenu
from game import CarreraDeObstaculos


def main():
    pygame.init()
    screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    pygame.display.set_caption("Carrera de Obstáculos")
    clock = pygame.time.Clock()

    menu = EstadoMenu(screen)
    juego = CarreraDeObstaculos(screen)

    estado_actual = "MENU"
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if estado_actual == "MENU":
            resultado = menu.manejar_eventos(events)
            if resultado == "JUGANDO":
                juego.reset_game()
                juego.player_name = menu.player_name
                estado_actual = "JUGANDO"
            elif resultado == "SALIR":
                running = False

            menu.actualizar()
            menu.dibujar()

        elif estado_actual == "JUGANDO":
            resultado_eventos = juego.handle_events(events)
            if resultado_eventos == "MENU":
                estado_actual = "MENU"

            resultado_update = juego.update(dt)
            if resultado_update == "MENU":
                estado_actual = "MENU"
                score = juego.score // 10
                menu.finalizar_partida(score, juego.player_name)

            juego.draw()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()