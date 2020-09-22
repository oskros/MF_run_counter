from init import *
from utils import tk_dynamic as tkd, tk_utils, color_themes
from memory_reader import reader
import os
import win32gui


class StatsTracker:
    def __init__(self, main_frame):
        if win32gui.FindWindow(None, 'Stats tracker'):
            return
        new_win = tkd.Toplevel()
        new_win.title('Stats tracker')
        new_win.wm_attributes('-topmost', main_frame.always_on_top)

        disp_coords = tk_utils.get_displaced_geom(main_frame.root, 240, 200)
        new_win.geometry(disp_coords)
        new_win.focus_get()
        new_win.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        new_win.resizable(False, False)

        color_themes.Theme(main_frame.active_theme).update_colors()

