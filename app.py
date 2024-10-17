"""
File: app.py
Author: Chuncheng Zhang
Date: 2024-10-17
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Application for IP location.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-10-17 ------------------------
# Requirements and constants
import time
import noise
import contextlib
import numpy as np

from PIL import Image, ImageTk
from threading import Thread, RLock

import tkinter as tk
from tkinter import ttk

from util.ip_toolbox import get_ip_address, get_location, get_img


# %% ---- 2024-10-17 ------------------------
# Function and class
rlock = RLock()


class NoiseImage(object):
    noise = noise.snoise3
    size = (100, 100)
    scale = (1, 1)
    rlock = rlock

    def prepare(self):
        xg, yg = np.meshgrid(
            np.linspace(0, self.scale[0], self.size[0]),
            np.linspace(0, self.scale[1], self.size[1]),
        )

        self.xr = xg.ravel()
        self.yr = yg.ravel()
        self.mat = np.zeros_like(xg)

    @contextlib.contextmanager
    def lock(self):
        try:
            self.rlock.acquire()
            yield
        finally:
            self.rlock.release()

    def generate(self, z=None):
        if z is None:
            z = time.time() % 3600

        buf = np.zeros_like(self.xr)
        for i, (x, y) in enumerate(zip(self.xr, self.yr)):
            buf[i] = self.noise(x, y, z)

        with self.lock():
            self.mat = buf.reshape(self.size)

        return buf

    def mat2img(self):
        with self.lock():
            m = 255*(self.mat + 1)*0.5
        return Image.fromarray(m.astype(np.uint8))


class MyCanvas(object):
    ni = NoiseImage()

    def __init__(self, canvas):
        self.ni.prepare()
        self.canvas = canvas
        self.canvas_img = None
        self.queried_img = None
        pass

    def query_img(self, lat, lon):
        img = get_img(lat, lon)
        self.queried_img = img

    def draw(self):
        if self.queried_img is None:
            self.ni.generate()
            img = self.ni.mat2img()

            self.photo_img = ImageTk.PhotoImage(img.resize((500, 500)))

            if self.canvas_img is None:
                self.canvas_img = self.canvas.create_image(
                    50, 50, image=self.photo_img)
            else:
                self.canvas.itemconfig(self.canvas_img, image=self.photo_img)

            self.canvas.after(30, self.draw)
        else:
            img = self.queried_img

            self.photo_img = ImageTk.PhotoImage(img.resize((500, 500)))

            if self.canvas_img is None:
                self.canvas_img = self.canvas.create_image(
                    50, 50, image=self.photo_img)
            else:
                self.canvas.itemconfig(self.canvas_img, image=self.photo_img)

        return

    def query_draw(self, lat, lon):
        img = get_img(lat, lon)
        print(f'Got img: {img}, {lat}, {lon}')
        self.photo_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self.photo_img)
        return


def promise_change_text(label):
    ip = get_ip_address(use_proxy=False)
    label.config(text=f'IP address: {ip}')

# %%


# %% ---- 2024-10-17 ------------------------
# Play ground
if __name__ == '__main__':
    root = tk.Tk()

    frm = ttk.Frame(root, padding=50, width=600)
    frm.grid(row=0, column=0)

    frm2 = ttk.Frame(root, padding=50, width=600)
    frm2.grid(row=0, column=1)

    ttk.Label(frm, text='Left panel').pack()
    ttk.Label(frm2, text='Right panel').pack()

    canvas = tk.Canvas(frm)
    mc = MyCanvas(canvas)
    mc.draw()

    def _query_local_ip(panel):
        label = ttk.Label(panel, text="Local IP Address")
        box = tk.Listbox(panel, width=30, height=15)

        label.pack()
        box.pack()
        canvas.pack()

        def _query():
            ip = get_ip_address(use_proxy=False)
            label.config(text=f'IP address: {ip}')
            location = get_location(ip)
            for i, (k, v) in enumerate(location.items()):
                box.insert(i+1, f'{i+1}. {k}: {v}')
            Thread(target=mc.query_img, args=(
                location['lat'], location['lon'],), daemon=True).start()

        Thread(target=_query, daemon=True).start()

    _query_local_ip(frm)

    def _query_vpn_ip(panel):
        label = ttk.Label(panel, text="VPN IP Address")
        box = tk.Listbox(panel, width=30, height=15)
        canvas = tk.Canvas(panel)

        label.pack()
        box.pack()

        img = Image.open('img.png')
        photo_img = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image=photo_img)

        canvas.pack()

        mc = MyCanvas(canvas)

        def _query():
            ip = get_ip_address(use_proxy=True)
            label.config(text=f'VPN address: {ip}')

            location = get_location(ip)
            for i, (k, v) in enumerate(location.items()):
                box.insert(i+1, f'{i+1}. {k}: {v}')

            # img = get_img(location['lat'], location['lon'])
            img = Image.open('img.png')
            photo_img = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, image=photo_img)

            # mc.query_draw(location['lat'], location['lon'])

        Thread(target=_query, daemon=True).start()

    _query_vpn_ip(frm2)

    # canvas = tk.Canvas(frm)
    # canvas.pack()
    # mc = MyCanvas(canvas)
    # Thread(target=mc.query_img, args=(50, 50,), daemon=True).start()
    # mc.draw()

    # Thread(target=promise_change_text, args=(label,), daemon=True).start()

    ttk.Button(frm, text="Quit", command=root.destroy).pack()

    root.mainloop()

# %% ---- 2024-10-17 ------------------------
# Pending


# %% ---- 2024-10-17 ------------------------
# Pending
