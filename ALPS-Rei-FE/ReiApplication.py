import cv2
import tkinter
import ReiConfig
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont

class Application(tkinter.Frame):
    def loop(self):
        self.image_bgr = 255 * np.ones((ReiConfig.HEIGHT, ReiConfig.WIDTH, 3), np.uint8)
        self.image_bgr[0:ReiConfig.HEIGHT, 0:ReiConfig.WIDTH] = self.image_main
        self.image_rgb = cv2.cvtColor(self.image_bgr, cv2.COLOR_BGR2RGB)
        self.image_pil = Image.fromarray(self.image_rgb)
        self.image_tk = ImageTk.PhotoImage(self.image_pil)
        self.canvas.create_image(0, 0, image = self.image_tk, anchor = "nw")
        self.after(100, self.loop)
    
    def __init__(self, master = None):
        super().__init__(master)
        self.master.geometry(str(ReiConfig.WIDTH) + "x" + str(ReiConfig.HEIGHT))
        self.master.title(ReiConfig.TITLE)
        self.master.resizable(0, 0)
        self.canvas = tkinter.Canvas(self.master, highlightthickness = 0)
        self.canvas.place(x = 0, y = 0, w = ReiConfig.WIDTH, h = ReiConfig.HEIGHT)
        self.font = ImageFont.truetype("./assets/Kosugi-Regular.ttf", 42)
        self.image_main = cv2.imread("./assets/main.png")
        self.loop()
        self.master.mainloop()
