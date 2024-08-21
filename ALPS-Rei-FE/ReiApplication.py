import cv2
import datetime
import tkinter
import ReiConfig
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont

class Application(tkinter.Frame):
    def draw_text(self, img, text, x, y, font, color):
        img = Image.fromarray(img)
        draw = ImageDraw.Draw(img)
        color_bgr = (color[2], color[1], color[0])
        draw.text((x, y), text, font = font, fill = color_bgr)
        img = np.array(img)
        return img
    
    def loop(self):
        timezone = datetime.timezone(datetime.timedelta(hours = 9), "JST")
        now = datetime.datetime.now(timezone)
        # 背景画像
        self.image_bgr = 255 * np.ones((ReiConfig.HEIGHT, ReiConfig.WIDTH, 3), np.uint8)
        self.image_bgr[0:ReiConfig.HEIGHT, 0:ReiConfig.WIDTH] = self.image_main
        # 日時
        self.image_bgr = self.draw_text(self.image_bgr, now.strftime("%Y/%m/%d %H:%M:%S"), 20, 5, self.font_clock, (0, 0, 0))
        # 小計
        self.image_bgr = self.draw_text(self.image_bgr, "いらっしゃいませ", 40, 445, self.font, (0, 0, 0))
        # ウインドウに転送
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
        self.font_clock = ImageFont.truetype("./assets/Kosugi-Regular.ttf", 18)
        self.font = ImageFont.truetype("./assets/Kosugi-Regular.ttf", 36)
        self.image_main = cv2.imread("./assets/main.png")
        self.loop()
        self.master.mainloop()
