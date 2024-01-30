import tkinter as tk
import cv2
from PIL import Image, ImageTk

from constants import *


class GUI:
    def __init__(self):
        # Inicjalizuje interfejs użytkownika
        self.fps = default_fps

        self.root = tk.Tk()
        self.root.title("Real-time Object Detection")

        # Ustawienia interfejsu z obrazem
        self.canvas = tk.Canvas(self.root, width=600, height=300)
        self.canvas.pack(padx=10, pady=10)

        # Etykieta dla wyświetlania liczby klatek na sekundę
        self.label_fps = tk.Label(self.root, text="FPS: ")
        self.label_fps.pack(pady=10)

        # Etykieta dla wyświetlania informacji o pierwszych monetach
        self.label_first_coins = tk.Label(self.root, text="First Coins: ")
        self.label_first_coins.pack(pady=10)

        # Przycisk do zmiany prędkości odtwarzania wideo
        self.change_fps_button = tk.Button(self.root, text="Change FPS", command=self.change_fps)
        self.change_fps_button.pack(pady=10)

        # Przycisk do zamknięcia aplikacji
        self.quit_button = tk.Button(self.root, text="Quit", command=self.root.destroy)
        self.quit_button.pack(pady=10)

    def change_fps(self):
        # Zmienia prędkość odtwarzania wideo na podstawie aktualnej wartości
        if self.fps == default_fps:
            self.fps = slowed_fps
        else:
            self.fps = default_fps

    def update_gui(self, frame, pre_frame, detected_coins):
        # Konwertuje klatki do formatu odpowiedniego dla tkintera
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_frame = Image.fromarray(frame_rgb)
        img_frame = ImageTk.PhotoImage(image=img_frame)

        pre_frame_rgb = cv2.cvtColor(pre_frame, cv2.COLOR_BGR2RGB)
        img_preframe = Image.fromarray(pre_frame_rgb)
        img_preframe = ImageTk.PhotoImage(image=img_preframe)

        # Aktualizuje widok na interfejsie
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_frame)
        self.canvas.create_image(img_frame.width() + 10, 0, anchor=tk.NW, image=img_preframe)

        # Wyświetla informacje o prędkości odtwarzania i pierwszych monetach
        first_coins_values = [coin[0] for coin in detected_coins]
        self.label_fps.config(text=f"FPS: {self.fps}")
        self.label_first_coins.config(text=f"First Coins: {first_coins_values}")

        # Aktualizuje interfejs
        self.root.update_idletasks()
        self.root.update()
