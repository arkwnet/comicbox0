import cv2
import datetime
import tkinter
import ReiCommon
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
        self.image_bgr = self.draw_text(self.image_bgr, now.strftime("%Y/%m/%d %H:%M:%S"), 20, 5, self.font_clock, (255, 255, 255))
        # 小計
        self.image_bgr = self.draw_text(self.image_bgr, "いらっしゃいませ", 35, 440, self.font, (0, 0, 0))
        now_count = 1
        now_price = 200
        self.image_bgr = self.draw_text(self.image_bgr, str(now_count).rjust(2), 110, 535, self.font, (0, 0, 0))
        self.image_bgr = self.draw_text(self.image_bgr, str(now_price).rjust(5), 645, 535, self.font, (0, 0, 0))
        # 合計
        total_count = 1
        total_price = 200
        self.image_bgr = self.draw_text(self.image_bgr, str(total_count).rjust(5), 1100, 436, self.font, (0, 0, 0))
        self.image_bgr = self.draw_text(self.image_bgr, str(total_price).rjust(5), 1100, 482, self.font, (0, 0, 0))
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
        self.font = ImageFont.truetype("./assets/Kosugi-Regular.ttf", 42)
        self.image_main = cv2.imread("./assets/main.png")
        self.items = []
        with open("./items.csv", encoding = "utf-8") as f:
            for line in f:
                line_array = line.split(",")
                self.items.append(ReiCommon.Item(line_array[0], int(line_array[1]), 1))
        self.loop()
        self.master.mainloop()
