import cv2
import datetime
import json
import logging
import os
import tkinter
import ReiCommon
import ReiConfig
import urllib.request
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(filename = "log.txt", encoding = "utf-8", level = logging.DEBUG)

class Application(tkinter.Frame):
    def draw_text(self, img, text, x, y, font, color):
        img = Image.fromarray(img)
        draw = ImageDraw.Draw(img)
        color_bgr = (color[2], color[1], color[0])
        draw.text((x, y), text, font = font, fill = color_bgr)
        img = np.array(img)
        return img
    
    def total(self):
        total = 0
        for i in range(len(self.cart)):
            total += self.cart[i].price * self.cart[i].quantity
        return total
    
    def loop(self):
        timezone = datetime.timezone(datetime.timedelta(hours = 9), "JST")
        now = datetime.datetime.now(timezone)
        # 背景画像
        self.image_bgr = 255 * np.ones((ReiConfig.HEIGHT, ReiConfig.WIDTH, 3), np.uint8)
        if self.mode == 0:
            self.image_bgr[0:ReiConfig.HEIGHT, 0:ReiConfig.WIDTH] = self.image_main
        elif self.mode == 1:
            self.image_bgr[0:ReiConfig.HEIGHT, 0:ReiConfig.WIDTH] = self.image_payment
        # 日時
        self.image_bgr = self.draw_text(self.image_bgr, now.strftime("%Y/%m/%d %H:%M:%S"), 20, 5, self.font_clock, (255, 255, 255))
        # 小計
        if self.mode == 0:
            if len(self.cart) >= 1:
                self.image_bgr = self.draw_text(self.image_bgr, self.cart[len(self.cart) - 1].name, 35, 440, self.font, (0, 0, 0))
                self.image_bgr = self.draw_text(self.image_bgr, str(self.cart[len(self.cart) - 1].quantity).rjust(2), 110, 535, self.font, (0, 0, 0))
                self.image_bgr = self.draw_text(self.image_bgr, str(self.cart[len(self.cart) - 1].price * self.cart[len(self.cart) - 1].quantity).rjust(5), 645, 535, self.font, (0, 0, 0))
        elif self.mode == 1:
            self.image_bgr = self.draw_text(self.image_bgr, "決済手段とお預かり金額を入力", 35, 440, self.font, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, str(self.payment.cash).rjust(5), 645, 535, self.font, (0, 0, 0))
        # 購入リスト
        total_count = 0
        for i in range(len(self.cart)):
            self.image_bgr = self.draw_text(self.image_bgr, str(i + 1), 25, 132 + i * 32, self.font_table, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, self.cart[i].name, 145, 132 + i * 32, self.font_table, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, str(self.cart[i].quantity).rjust(2), 530, 132 + i * 32, self.font_table, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, str(self.cart[i].price).rjust(4), 615, 132 + i * 32, self.font_table, (0, 0, 0))
            self.image_bgr = self.draw_text(self.image_bgr, str(self.cart[i].price * self.cart[i].quantity).rjust(5), 735, 132 + i * 32, self.font_table, (0, 0, 0))
            total_count += self.cart[i].quantity
        self.image_bgr = self.draw_text(self.image_bgr, str(total_count).rjust(5), 1100, 436, self.font, (0, 0, 0))
        self.image_bgr = self.draw_text(self.image_bgr, str(self.total()).rjust(5), 1100, 482, self.font, (0, 0, 0))
        if self.mode == 0:
            # 商品リスト
            for i in range(len(self.items)):
                self.image_bgr[101 + i * 44:147 + i * 44, 815:1255] = self.image_item
                self.image_bgr = self.draw_text(self.image_bgr, self.items[i].name, 865, 112 + i * 44, self.font_table, (0, 0, 0))
                self.image_bgr = self.draw_text(self.image_bgr, self.keymap[i].full, 1215, 112 + i * 44, self.font_table, (0, 0, 0))
        if self.mode == 1:
            # 決済手段リスト
            for i in range(len(self.method)):
                self.image_bgr[101 + i * 44:147 + i * 44, 815:1255] = self.image_item
                self.image_bgr = self.draw_text(self.image_bgr, self.method[i], 865, 112 + i * 44, self.font_table, (0, 0, 0))
                self.image_bgr = self.draw_text(self.image_bgr, self.keymap2[i].full, 1215, 112 + i * 44, self.font_table, (0, 0, 0))
        # ウインドウに転送
        self.image_rgb = cv2.cvtColor(self.image_bgr, cv2.COLOR_BGR2RGB)
        self.image_pil = Image.fromarray(self.image_rgb)
        self.image_tk = ImageTk.PhotoImage(self.image_pil)
        self.canvas.create_image(0, 0, image = self.image_tk, anchor = "nw")
        self.after(100, self.loop)
    
    def key_event(self, e):
        if self.mode == 0:
            if e.keysym == "Escape":
                self.cart.clear()
                self.display.clear()
            elif e.keysym == "space":
                total = 0
                for i in range(len(self.cart)):
                    total += self.cart[i].price * self.cart[i].quantity
                self.payment = ReiCommon.Payment("", self.total(), 0, 0)
                self.display.update("", "", "合計", str(self.payment.total))
                self.mode = 1
            else:
                for i in range(len(self.items)):
                    if e.keysym == self.keymap[i].half:
                        hit = False
                        for j in range(len(self.cart)):
                            if self.cart[j].name == self.items[i].name:
                                self.cart[j].quantity += 1
                                self.cart.append(self.cart[j])
                                del self.cart[j]
                                self.display.update(self.cart[len(self.cart) - 1].name, str(self.cart[len(self.cart) - 1].price), "小計", str(self.total()))
                                hit = True
                                break
                        if hit == False:
                            self.cart.append(self.items[i])
                            self.cart[len(self.cart) - 1].quantity = 1
                            self.display.update(self.cart[len(self.cart) - 1].name, str(self.cart[len(self.cart) - 1].price), "小計", str(self.total()))
        elif self.mode == 1:
            if e.keysym == "Escape":
                self.mode = 0
            elif e.keysym == "BackSpace":
                self.payment.cash = 0
            else:
                for i in range(10):
                    if e.keysym == str(i):
                        if (len(str(self.payment.cash)) <= 4):
                            self.payment.cash = int(str(self.payment.cash) + str(i))
                        break
                for i in range(len(self.method)):
                    if e.keysym == self.keymap2[i].half:
                        if self.payment.cash >= self.payment.total:
                            self.payment.method = self.method[i]
                            self.payment.change = self.payment.cash - self.payment.total
                            items = []
                            for j in range(len(self.cart)):
                                items.append({
                                    "name": self.cart[j].name,
                                    "price": str(self.cart[j].price),
                                    "quantity": str(self.cart[j].quantity)
                                })
                                self.logger.info("[ITEM] timestamp=" + datetime.datetime.now().isoformat() + ", price=" + str(self.cart[j].price) + ", quantity=" + str(self.cart[j].quantity))
                            self.id += 1
                            obj = {
                                "id": str(self.id),
                                "items": items,
                                "total": str(self.payment.total),
                                "payment": self.payment.method,
                                "cash": str(self.payment.cash),
                                "change": str(self.payment.change)
                            }
                            obj_json = json.dumps(obj).encode("utf-8")
                            request = urllib.request.Request(os.getenv("BACKEND_URL") + "/record", data = obj_json, method = "POST", headers = {"Content-Type": "application/json", "User-Agent": "mozilla/5.0"})
                            with urllib.request.urlopen(request) as response:
                                response_body = response.read().decode("utf-8")
                            if self.payment.method == "現金":
                                self.payment.method = "お預かり"
                            with open("./receipt.json", "wt", encoding = "utf-8") as f:
                                json.dump(obj, f, indent = 2, ensure_ascii = False)
                            with open("./id", "w", encoding = "utf-8") as f:
                                f.write(str(self.id))
                            self.display.update(self.payment.method, str(self.payment.cash), "お釣り", str(self.payment.change))
                            self.logger.info("[PURCHASE] timestamp=" + datetime.datetime.now().isoformat() + ", id=" + str(self.id) + ", total=" + str(self.payment.total) + ", payment=" + self.payment.method + ", cash=" + str(self.payment.cash) + ", change=" + str(self.payment.change))
                            self.cart.clear()
                            self.mode = 0
                            break
    
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
        self.image_payment = cv2.imread("./assets/payment.png")
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
        self.keymap2 = [
            ReiCommon.Key("Ａ", "a"),
            ReiCommon.Key("Ｓ", "s"),
            ReiCommon.Key("Ｄ", "d"),
            ReiCommon.Key("Ｆ", "f"),
            ReiCommon.Key("Ｇ", "g"),
            ReiCommon.Key("Ｈ", "h"),
            ReiCommon.Key("Ｊ", "j")
        ]
        self.id = 0
        if os.path.isfile("./id"):
            with open("./id", encoding = "utf-8") as f:
                self.id = int(f.read())
        self.display = ReiCommon.Display()
        self.display.clear()
        self.items = []
        self.cart = []
        self.payment = None
        self.method = []
        self.mode = 0
        with open("./items.csv", encoding = "utf-8") as f:
            for line in f:
                line_array = line.split(",")
                self.items.append(ReiCommon.Item(line_array[0], int(line_array[1]), 1))
        with open("./payment.csv", encoding = "utf-8") as f:
            for line in f:
                line_array = line.split(",")
                self.method.append(line_array[0])
        self.logger = logging.getLogger(__name__)
        self.logger.info("[START] timestamp=" + datetime.datetime.now().isoformat())
        self.master.bind("<KeyPress>", self.key_event)
        self.loop()
        self.master.mainloop()
