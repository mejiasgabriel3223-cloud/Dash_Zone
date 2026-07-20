import os
import pygame

class SoundPlayer:
    _current_track = None

    def __init__(self):
        self.initialized = False
        self.current_game_track = 0  # <-- Atributo añadido para evitar el error
        self.audio_folder = os.path.join(os.path.dirname(__file__), "audio")
        self._init_mixer()

    def _init_mixer(self):
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
            pygame.mixer.init()
            self.initialized = True
        except pygame.error:
            self.initialized = False

    def play_menu_music(self):
        if not self.initialized:
            return
        
        menu_files = [
            "Good Kid-Tea Leaves.mp3",
            "Good Kid-Tea Leaves.ogg",
            "Good Kid-Tea Leaves.wav",
            "menu.mp3",
            "menu.ogg",
            "menu.wav",
        ]
        
        path = self._find_first_existing(menu_files)
        if not path:
            return

        if SoundPlayer._current_track == path and pygame.mixer.music.get_busy():
            return

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.18)
            SoundPlayer._current_track = path
        except pygame.error:
            pass

    def play_game_music(self, track=0):
        if not self.initialized:
            return

        game_playlists = [
            [
                "Rift-Good Kid.mp3",
                "Rift-Good Kid.ogg",
                "Rift-Good Kid.wav",
                "game1.mp3",
                "game1.ogg",
                "game1.wav",
            ],
            [
                "Rift-Good Kid.mp3",
                "Rift-Good Kid.ogg",
                "Rift-Good Kid.wav",
                "game2.mp3",
                "game2.ogg",
                "game2.wav",
            ]
        ]

        if track < 0 or track >= len(game_playlists):
            track = 0

        path = self._find_first_existing(game_playlists[track])
        if not path:
            return

        self.current_game_track = track  # <-- Actualizamos el índice de la pista actual

        if SoundPlayer._current_track == path and pygame.mixer.music.get_busy():
            return

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.14)
            SoundPlayer._current_track = path
        except pygame.error:
            pass

    def _find_first_existing(self, filenames):
        for filename in filenames:
            path = os.path.join(self.audio_folder, filename)
            if os.path.exists(path):
                return path
        return None

    def stop_all(self):
        if not self.initialized:
            return
        try:
            pygame.mixer.music.stop()
            SoundPlayer._current_track = None
            self.current_game_track = 0
        except pygame.error:
            pass