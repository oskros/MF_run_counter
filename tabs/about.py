from init import *
from utils import tk_dynamic as tkd
import tkinter as tk


class About(tkd.Frame):
    def __init__(self, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        label0 = tkd.Label(self, text="""MF Run counter for Diablo 2                         
         
In development since July 2019 by
oskros#1889 on Discord.

Please see the README.md file available
on Github""", justify=tk.LEFT)
        label0.pack()
        tkd.Hyperlink(self, hyperlink=release_repo.rstrip('releases') + 'blob/master/README.md', text="Open Readme").pack()
        tkd.Label(self, text="\n\nVisit the page below for new releases").pack()
        tkd.Hyperlink(self, hyperlink=release_repo, text="Release Hyperlink").pack()
        tkd.Label(self, text="\n\nCurrent version: %s" % version).pack(side=tk.BOTTOM)
