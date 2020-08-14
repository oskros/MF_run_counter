from init import *
import tk_dynamic as tkd
import tkinter as tk
import webbrowser


class About(tkd.Frame):
    def __init__(self, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        label0 = tkd.Label(self, text="""MF Run counter for Diablo 2                         
         
In development since July 2019 by
oskros#1889 on Discord.

Please see the README.md file available
on Github""", justify=tk.LEFT)
        label0.pack()
        link0 = tkd.Hyperlink(self, text="Open Readme", cursor="hand2")
        link0.pack()
        link0.bind("<Button-1>", lambda e: webbrowser.open_new(release_repo.rstrip('releases') + 'blob/master/README.md'))

        label = tkd.Label(self, text="\n\nVisit the page below for new releases")
        label.pack()

        link1 = tkd.Hyperlink(self, text="Release Hyperlink", cursor="hand2")
        link1.pack()
        link1.bind("<Button-1>", lambda e: webbrowser.open_new(release_repo))

        lab2 = tkd.Label(self, text="\n\nCurrent version: %s" % version)
        lab2.pack(side=tk.BOTTOM)