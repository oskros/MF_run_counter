from init import *
from utils import tk_dynamic as tkd
import tkinter as tk


class About(tkd.Frame):
    def __init__(self, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        label0 = tkd.Label(self, text="""MF Run Counter for Diablo 2\n\nIn development since July 2019 by\noskros#1889 on Discord.\n\nPlease see the README.md file""")
        label0.pack()
        tkd.Hyperlink(self, hyperlink=release_repo.rstrip('releases') + 'blob/master/README.md', text="Open Readme").pack()
        tkd.Label(self, text="\nVisit the page below for new releases").pack()
        tkd.Hyperlink(self, hyperlink=release_repo, text="Release Hyperlink").pack()

        tkd.Label(self, text="\nJoin Sightup's D2 Discord channel").pack()
        tkd.Hyperlink(self, hyperlink='https://discord.gg/NTRFy8S', text='Discord invite link').pack()

        tkd.Label(self, text="\nCurrent version: %s" % version).pack(side=tk.BOTTOM)
