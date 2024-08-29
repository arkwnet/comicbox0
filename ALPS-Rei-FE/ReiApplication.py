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
        if len(self.cart) >= 1:
            self.image_bgr = self.draw_text(self.image_bgr, self.cart[len(self.cart) - 1].name, 35, 440, self.font, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, str(self.cart[len(self.cart) - 1].quantity).rjust(2), 110, 535, self.font, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, str(self.cart[len(self.cart) - 1].price * self.cart[len(self.cart) - 1].quantity).rjust(5), 645, 535, self.font, (0, 0, 0))
        # 購入リスト
        total_count = 0
        total_price = 0
        for i in range(len(self.cart)):
            self.image_bgr = self.draw_text(self.image_bgr, str(i + 1), 25, 132 + i * 32, self.font_table, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, self.cart[i].name, 145, 132 + i * 32, self.font_table, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, str(self.cart[i].quantity).rjust(2), 530, 132 + i * 32, self.font_table, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, str(self.cart[i].price).rjust(4), 615, 132 + i * 32, self.font_table, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, str(self.cart[i].price * self.cart[i].quantity).rjust(5), 735, 132 + i * 32, self.font_table, (0, 0, 0))
            total_count += self.cart[i].quantity
            total_price += self.cart[i].price * self.cart[i].quantity
        self.image_bgr = self.draw_text(self.image_bgr, str(total_count).rjust(5), 1100, 436, self.font, (0, 0, 0))
        self.image_bgr = self.draw_text(self.image_bgr, str(total_price).rjust(5), 1100, 482, self.font, (0, 0, 0))
        # 商品リスト
        for i in range(len(self.items)):
            self.image_bgr[101 + i * 44:147 + i * 44, 815:1255] = self.image_item
            self.image_bgr = self.draw_text(self.image_bgr, self.items[i].name, 865, 112 + i * 44, self.font_table, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, self.keymap[i].full, 1215, 112 + i * 44, self.font_table, (0, 0, 0))
        # ウインドウに転送
        self.image_rgb = cv2.cvtColor(self.image_bgr, cv2.COLOR_BGR2RGB)
        self.image_pil = Image.fromarray(self.image_rgb)
        self.image_tk = ImageTk.PhotoImage(self.image_pil)
        self.canvas.create_image(0, 0, image = self.image_tk, anchor = "nw")
        self.after(100, self.loop)
    
    def key_event(self, e):
        if e.keysym == "Escape":
            self.cart.clear()
        else:
            for i in range(len(self.items)):
                if e.keysym == self.keymap[i].half:
                    hit = False
                    for j in range(len(self.cart)):
                        if self.cart[j].name == self.items[i].name:
                            self.cart[j].quantity += 1
                            self.cart.append(self.cart[j])
                            del self.cart[j]
                            hit = True
                            break
                    if hit == False:
                        self.cart.append(self.items[i])
    
    def __init__(self, master = None):
        super().__init__(master)
        self.master.geometry(str(ReiConfig.WIDTH) + "x" + str(ReiConfig.HEIGHT))
        self.master.title(ReiConfig.TITLE)
        self.master.resizable(0, 0)
        self.canvas = tkinter.Canvas(self.master, highlightthickness = 0)
        self.canvas.place(x = 0, y = 0, w = ReiConfig.WIDTH, h = ReiConfig.HEIGHT)
        self.font_clock = ImageFont.truetype("./assets/Kosugi-Regular.ttf", 18)
        self.font_table = ImageFont.truetype("./assets/Kosugi-Regular.ttf", 22)
        self.font = ImageFont.truetype("./assets/Kosugi-Regular.ttf", 42)
        self.image_main = cv2.imread("./assets/main.png")
        self.image_item = cv2.imread("./assets/item.png")
        self.keymap = [
            ReiCommon.Key("Ｑ", "q"),
            ReiCommon.Key("Ｗ", "w"),
            ReiCommon.Key("Ｅ", "e"),
            ReiCommon.Key("Ｒ", "r"),
            ReiCommon.Key("Ｔ", "t"),
            ReiCommon.Key("Ｙ", "y"),
            ReiCommon.Key("Ｕ", "u")
        ]
        self.items = []
        self.cart = []
        with open("./items.csv", encoding = "utf-8") as f:
            for line in f:
                line_array = line.split(",")
                self.items.append(ReiCommon.Item(line_array[0], int(line_array[1]), 1))
        self.master.bind("<KeyPress>", self.key_event)
        self.loop()
        self.master.mainloop()
