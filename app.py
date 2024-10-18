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

from util.ip_toolbox import IpToolbox


# %% ---- 2024-10-17 ------------------------
# Function and class
rlock = RLock()
ip_toolbox = IpToolbox()


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
        return

    @contextlib.contextmanager
    def lock(self):
        try:
            self.rlock.acquire()
            yield
        finally:
            self.rlock.release()
        return

    def generate(self, z=None):
        if z is None:
            z = time.time() % 3600

        buf = np.zeros_like(self.xr)
        for i, (x, y) in enumerate(zip(self.xr, self.yr)):
            buf[i] = self.noise(x, y, z)

        with self.lock():
            self.mat = buf.reshape(self.size)

        return buf

    def get_img(self):
        with self.lock():
            m = 255*(self.mat + 1)*0.5
        return Image.fromarray(m.astype(np.uint8))


class AnimatingCanvas(object):
    ni = NoiseImage()

    def __init__(self, canvas: tk.Canvas):
        self.ni.prepare()
        self.canvas: tk.Canvas = canvas
        self.canvas_img = None
        self.queried_img = None
        pass

    def query_img(self, lat, lon, width=300, height=300):
        def _bg():
            img = ip_toolbox.get_img(lat, lon, width=width, height=height)
            self.queried_img = img
        Thread(target=_bg, daemon=True).start()
        return

    def draw(self):
        # Draw the loading (animating) image
        if self.queried_img is None:
            self.ni.generate()
            img = self.ni.get_img()

            self.photo_img = ImageTk.PhotoImage(img.resize((600, 600)))

            if self.canvas_img is None:
                self.canvas_img = self.canvas.create_image(
                    0, 0, image=self.photo_img)
            else:
                self.canvas.itemconfig(self.canvas_img, image=self.photo_img)

            self.canvas.after(30, self.draw)

        # Draw the queried_img
        # and stop the animating
        else:
            img = self.queried_img
            self.photo_img = ImageTk.PhotoImage(img)
            self.canvas_img = self.canvas.create_image(
                0, 0, image=self.photo_img, anchor=tk.NW)

        return


class MyFrame(ttk.Frame):
    title = 'My customized frame'
    label_text = 'Label'
    box_size = {'width': 30, 'height': 15}
    canvas_size = {'width': 300, 'height': 300}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def layout(self):
        # Initialize the components
        self.title_label = ttk.Label(self, text=self.title)
        self.detail_label = ttk.Label(self, text=self.label_text)
        self.box = tk.Listbox(self, **self.box_size)
        self.canvas = tk.Canvas(self, **self.canvas_size)
        self.ac = AnimatingCanvas(self.canvas)

        # Start the animation
        self.ac.draw()

        # Put the components
        self.title_label.pack()
        self.detail_label.pack()
        self.box.pack()
        self.canvas.pack()

        return

    def draw_local_ip(self):
        Thread(target=self._draw_local_ip, daemon=True).start()
        return

    def draw_vpn_ip(self):
        Thread(target=self._draw_vpn_ip, daemon=True).start()
        return

    def _draw_local_ip(self):
        ip = ip_toolbox.get_ip_address(use_proxy=False)
        self.detail_label.config(text=f'IP address: {ip}')
        location = ip_toolbox.get_location(ip)
        for i, (k, v) in enumerate(location.items()):
            self.box.insert(i+1, f'{i+1}. {k}: {v}')
        self.ac.query_img(location['lat'], location['lon'])
        return

    def _draw_vpn_ip(self):
        ip = ip_toolbox.get_ip_address(use_proxy=True)
        self.detail_label.config(text=f'VPN address: {ip}')
        location = ip_toolbox.get_location(ip)
        for i, (k, v) in enumerate(location.items()):
            self.box.insert(i+1, f'{i+1}. {k}: {v}')
        self.ac.query_img(location['lat'], location['lon'])
        return


# %%

# %% ---- 2024-10-17 ------------------------
# Play ground
if __name__ == '__main__':
    root = tk.Tk()

    # --------------------------------------------------------------------------------
    frm1 = MyFrame(root, padding=20, width=600)
    frm1.layout()
    frm1.draw_local_ip()
    frm1.grid(row=0, column=0)

    # --------------------------------------------------------------------------------
    frm2 = MyFrame(root, padding=20, width=600)
    frm2.layout()
    frm2.draw_vpn_ip()
    frm2.grid(row=0, column=1)

    ttk.Button(root, text="Quit", command=root.destroy).grid(row=1, column=1)

    root.mainloop()

# %% ---- 2024-10-17 ------------------------
# Pending


# %% ---- 2024-10-17 ------------------------
# Pending
