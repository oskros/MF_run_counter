from memory_reader import reader
import tkinter as tk
from collections import defaultdict
from utils import other_utils
from tkinter import messagebox
import sys


def kill_counter():
    try:
        r = reader.D2Reader()
        r.map_ptrs()
        # r.unit_map = dict()
    except other_utils.pymem_err_list:
        messagebox.showerror('No process', 'Diablo not opened. Start Diablo and then start the kill counter again')
        sys.exit()

    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    sv = tk.StringVar()
    # sv2 = tk.StringVar()

    def add_to_killed():
        try:
            ingame = r.in_game()
        except other_utils.pymem_err_list:
            messagebox.showerror('No process', 'Diablo not opened. Start Diablo and then start the kill counter again')
            sys.exit()
        if not ingame:
            r.observed_guids = set()
            r.dead_guids = []
            r.kill_counts = defaultdict(lambda: 0)
            sv.set('')
        else:
            r.update_dead_guids()
            sv.set('\n'.join(['%s: %s' % (k, v) for k, v in r.kill_counts.items()]))
            # sv2.set('\n'.join([str(x) for x in sorted(r.unit_map)]))
            # sv2.set('\n'.join(['%s: %s' % (k, v) for k, v in r.unit_map.items()]))
        root.after(50, add_to_killed)

    add_to_killed()

    tk.Label(root, text='killcount').pack()
    tk.Label(root, textvariable=sv).pack()

    # tk.Label(root, textvariable=sv2).pack()

    root.mainloop()


kill_counter()