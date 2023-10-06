from init import *
from utils import tk_dynamic as tkd
import tkinter as tk


class About(tkd.Frame):
    def __init__(self, main_fr, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        top_fr = tkd.Frame(self)
        top_fr.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tkd.Label(top_fr, text="MF Run Counter", font=('Segoe UI', 11, 'bold')).pack(pady=(0, 2))

        self.img = tk.PhotoImage(master=parent, file=media_path + 'about_icon.png')
        tkd.Label(top_fr, image=self.img, borderwidth=0).pack(pady=0)

        btm_fr = tkd.Frame(self)
        btm_fr.pack(side=tk.BOTTOM, fill=tk.X, expand=True, anchor=tk.S)

        tkd.Label(btm_fr, text='New releases & README info', borderwidth=0, highlightthickness=0, justify=tk.LEFT).pack(anchor=tk.W)
        tkd.Hyperlink(btm_fr, hyperlink=release_repo.rstrip('releases'), text="           Github Repository", borderwidth=0, highlightthickness=0, justify=tk.LEFT).pack(anchor=tk.W, pady=[0, 7])

        tkd.Label(btm_fr, text='Created by:', justify=tk.LEFT, borderwidth=0, highlightthickness=0).pack(anchor=tk.W)
        tkd.Label(btm_fr, text='           oskros#1889', font=('Segoe UI', 9, 'bold'), borderwidth=0, highlightthickness=0, justify=tk.LEFT).pack(anchor=tk.W)

        tkd.Label(btm_fr, text='Find me here:', justify=tk.LEFT, borderwidth=0, highlightthickness=0).pack(anchor=tk.W, pady=(7, 0))
        tkd.Hyperlink(btm_fr, hyperlink='https://discord.gg/JhkTF2g', text='           https://discord.gg/JhkTF2g', justify=tk.LEFT, borderwidth=0, highlightthickness=0).pack(anchor=tk.W)

        v_fr = tkd.Frame(btm_fr)
        v_fr.pack(side=tk.BOTTOM, fill=tk.X, expand=True, anchor=tk.S)
        tkd.Label(v_fr, text="v.%s" % version, justify=tk.RIGHT).pack(side=tk.RIGHT, anchor=tk.E)
        tkd.Label(v_fr, text='Downloads: %s' % main_fr.dl_count, justify=tk.LEFT).pack(side=tk.LEFT, anchor=tk.W)
