from init import *
from utils import tk_dynamic as tkd
import tkinter as tk
from tkinter import ttk
import webbrowser
from utils.other_utils import get_monitor_from_coord


def get_displaced_coords(master, app_x, app_y, pos_x=None, pos_y=None):
    if pos_x is None:
        pos_x = master.root.winfo_rootx()
    if pos_y is None:
        pos_y = master.root.winfo_rooty()
    mon = get_monitor_from_coord(master.root.winfo_rootx(), master.root.winfo_rooty(), disable_scaling=master.disable_scaling)
    min_x = mon.x
    min_y = mon.y
    max_x = mon.width + min_x
    max_y = mon.height + min_y

    return max(min(pos_x, max_x - app_x - 10), min_x - 5), max(min(pos_y, max_y - app_y), min_y)


def get_displaced_geom(master, app_x, app_y, pos_x=None, pos_y=None):
    if pos_x is None:
        pos_x = master.root.winfo_rootx()
    if pos_y is None:
        pos_y = master.root.winfo_rooty()
    mon = get_monitor_from_coord(master.root.winfo_rootx(), master.root.winfo_rooty(), disable_scaling=master.disable_scaling)
    min_x = mon.x
    min_y = mon.y
    max_x = mon.width + min_x
    max_y = mon.height + min_y

    displaced_x = max(min(pos_x, max_x - app_x - 10), min_x - 5)
    displaced_y = max(min(pos_y, max_y - app_y), min_y)

    return '%sx%s+%s+%s' % (app_x, app_y, displaced_x, displaced_y)


class RegistrationForm:
    def __init__(self, master, coords, first_profile):
        self.new_win = tk.Toplevel()
        self.new_win.title('Profile registration')
        self.new_win.wm_attributes('-topmost', 1)
        self.new_win.resizable(False, False)
        self.stringvars = []

        geom = get_displaced_geom(master, 290, 154, coords[0], coords[1])
        self.new_win.geometry(geom)
        # self.new_win.eval('tk::PlaceWindow . center')
        self.new_win.iconbitmap(media_path + 'icon.ico')

        lab_text = 'Please create your first profile.' if first_profile else 'Profile registration'
        tk.Label(self.new_win, text=lab_text, font='Helvetica 14').pack()

        self.a1 = self.make_entry_row('Profile name', restricted=True)
        self.a2 = self.make_entry_row('Character name')
        self.a3 = self.make_combobox_row('Run type', [
            '(A1) Mausoleum', '(A1) The Countess', '(A1) The Pit', '(A1) Andariel', '(A1) Cows', '-----------------------',
            '(A2) Stony Tomb', '(A2) Maggot Lair', '(A2) Ancient Tunnels', '(A2) Summoner', '-----------------------',
            '(A3) Arachnid Lair', '(A3) Swampy Pit', '(A3) Lower Kurast', '(A3) Sewers', '(A3) Kurast Temples', '(A3) Travincal', '(A3) Mephisto', '-----------------------',
            '(A4) River of Flame', '(A4) Chaos Sanctuary', '(A4) Diablo', '-----------------------',
            '(A5) Eldritch + Shenk', '(A5) Thresh Socket', '(A5) Red Portals', '(A5) Drifter Cavern', '(A5) Icy Cellar', '(A5) Pindleskin', '(A5) Nihlathak', '(A5) WSK + Baal',
            '(A5) Baal', '(A5) Uber Quest', '-----------------------',
            'Tier 1 maps', 'Tier 2 maps', 'Tier 3 maps', 'Mixed maps'], readonly=False)

        tk.Button(self.new_win, text='Submit', font='helvetica 12 bold', command=self.b1_action, bd=2).pack(fill=tk.X, expand=tk.YES)
        self.new_win.bind('<KeyPress-Return>', func=self.b1_action)
        self.new_win.bind('<KeyPress-Escape>', func=lambda e: self.close_mod())

        self.new_win.protocol("WM_DELETE_WINDOW", self.close_mod)
        self.a1.focus_set()

        self.new_win.focus_force()
        self.new_win.wait_window()

    def b1_action(self, event=None):
        try:
            a1 = self.a1.get()
            a2 = self.a2.get()
            a3 = self.a3.get()

            x = {'Profile name': a1, 'Character name': a2, 'Run type': a3}
        except AttributeError:
            self.returning = None
            self.new_win.destroy()
        else:
            self.returning = x
            self.new_win.destroy()

    def make_entry_row(self, text, restricted=False):
        frame = tk.Frame(self.new_win)
        frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(frame, width=16, text=text + ': ', anchor=tk.W).pack(side=tk.LEFT)
        self.stringvars.append(tk.StringVar())
        var = self.stringvars[-1]
        if restricted:
            out = tkd.RestrictedEntry(frame, textvariable=var)
        else:
            out = tk.Entry(frame, textvariable=var)
        out.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        return out

    def make_combobox_row(self, text, values, readonly=True):
        frame = tk.Frame(self.new_win)
        frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(frame, width=16, text=text + ': ', anchor=tk.W).pack(side=tk.LEFT)
        self.stringvars.append(tk.StringVar())
        var = self.stringvars[-1]
        out = ttk.Combobox(frame, textvariable=var, values=values)
        out.current(0)
        if readonly:
            out.config(state='readonly')
        out.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        return out

    def close_mod(self):
        self.returning = None
        self.new_win.destroy()


class MultiEntryBox(object):
    def __init__(self, entries, title, coords=None, defaults=None, masks=None, msg=None):
        self.root = tk.Toplevel()
        self.enum = len(entries)

        self.root.focus_set()
        self.root.iconbitmap(media_path + 'icon.ico')
        self.root.title(title)
        self.root.wm_attributes("-topmost", True)

        if msg is not None:
            frm_0 = tk.Frame(self.root)
            frm_0.pack()
            message = tk.Label(frm_0, text=str(msg), font=('arial', 11))
            message.pack(padx=8, pady=8)

        frm_1 = tk.Frame(self.root)
        frm_1.pack(ipadx=4, ipady=2)

        for i, e in enumerate(entries):
            ff = tk.Frame(frm_1)
            ff.pack()
            tk.Label(ff, font='arial 11', text=e, width=8).pack(side=tk.LEFT, expand=True, fill=tk.X, pady=3)
            setattr(self, 'e' + str(i), tk.Entry(ff, font=('arial', 11), justify='center'))
            getattr(self, 'e' + str(i)).pack(side=tk.LEFT, expand=True, fill=tk.X)
            if defaults is not None:
                getattr(self, 'e' + str(i)).insert(tk.END, defaults[i])
            if masks is not None and masks[i] is not None:
                getattr(self, 'e' + str(i)).config(show=masks[i])
            if i == 0:
                getattr(self, 'e' + str(i)).focus_set()

        # button frame
        frm_2 = tk.Frame(frm_1)
        frm_2.pack(padx=4, pady=4)

        # buttons
        btn_1 = tk.Button(frm_2, width=8, text='OK', command=self.b1_action)
        btn_1.pack(side='left')

        btn_2 = tk.Button(frm_2, width=8, text='Cancel', command=self.close_mod)
        btn_2.pack(side='left')

        # The enter button will trigger button 1, while escape will close the window
        self.root.bind('<KeyPress-Return>', func=self.b1_action)
        self.root.bind('<KeyPress-Escape>', func=self.close_mod)

        self.root.update_idletasks()
        if coords:
            xp = coords[0]
            yp = coords[1]
        else:
            xp = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
            yp = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        geom = (self.root.winfo_width(), self.root.winfo_height(), xp, yp)
        self.root.geometry('{0}x{1}+{2}+{3}'.format(*geom))

        # call self.close_mod when the close button is pressed
        self.root.protocol("WM_DELETE_WINDOW", self.close_mod)

        # a trick to activate the window (on windows 7)
        self.root.deiconify()

        # wait for response before outputting result
        self.root.wait_window()

    def b1_action(self, event=None):
        self.returning = [getattr(self, 'e' + str(i)).get() for i in range(self.enum)]
        self.root.destroy()

    def close_mod(self, event=None):
        self.returning = None
        self.root.destroy()


class MessageBox(object):
    def __init__(self, msg, b1='OK', b2='Cancel', entry=False, coords=None, title='Message', hyperlink='', master=None, disabled_btn_input=None):
        self.root = tk.Toplevel()
        self.root.focus_set()
        self.root.iconbitmap(media_path + 'icon.ico')
        self.root.title(title)
        self.root.wm_attributes("-topmost", True)
        self.msg = str(msg)
        self.disabled_btn_input = disabled_btn_input
        if self.disabled_btn_input:
            self.entry_var = tk.StringVar()
            self.entry_var.trace_add('write', lambda name, index, mode: self.check_input())
            entry = True

        # ctrl+c to copy self.msg
        self.root.bind('<Control-c>', func=self.to_clip)

        # default values for the buttons to return
        self.b1_return = True
        self.b2_return = False

        # if b1 or b2 is a tuple unpack into the button text & return value
        if isinstance(b1, tuple):
            b1, self.b1_return = b1
        if isinstance(b2, tuple):
            b2, self.b2_return = b2

        # main frame
        frm_1 = tk.Frame(self.root)
        frm_1.pack(ipadx=4, ipady=2)

        # the message
        message = tk.Label(frm_1, text=self.msg, font=('arial', 11))
        message.pack(padx=8, pady=8)

        # if entry or hyperlink is True create and set focus
        if hyperlink:
            self.button = tk.Label(frm_1, text=release_repo, fg="blue", cursor="hand2", font=('arial', 11))
            self.button.pack()
            self.button.bind("<Button-1>", lambda e: webbrowser.open_new(hyperlink))

        if entry:
            if disabled_btn_input is not None:
                self.entry = tk.Entry(frm_1, font=('arial', 11), justify='center', textvariable=self.entry_var)
            else:
                self.entry = tk.Entry(frm_1, font=('arial', 11), justify='center')
            self.entry.pack()
            self.entry.focus_set()

        # button frame
        frm_2 = tk.Frame(frm_1)
        frm_2.pack(padx=4, pady=4)

        # buttons
        self.btn_1 = tk.Button(frm_2, width=8, text=b1, command=self.b1_action)
        self.btn_1.pack(side='left')
        if disabled_btn_input is not None:
            self.btn_1.config(state=tk.DISABLED)
        if not entry:
            self.btn_1.focus_set()

        if b2 != '':
            btn_2 = tk.Button(frm_2, width=8, text=b2, command=self.b2_action)
            btn_2.pack(side='left')

        # The enter button will trigger button 1, while escape will close the window
        self.root.bind('<KeyPress-Return>', func=self.b1_action)
        self.root.bind('<KeyPress-Escape>', func=lambda e: self.close_mod())

        # Roughly center the box on screen. For accuracy see: https://stackoverflow.com/a/10018670/1217270
        self.root.update_idletasks()
        if coords and master:
            xp, yp = get_displaced_coords(master, self.root.winfo_width(), self.root.winfo_height(), coords[0], coords[1])
        elif coords:
            xp = coords[0]
            yp = coords[1]
        else:
            xp = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
            yp = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        geom = (self.root.winfo_width(), self.root.winfo_height(), xp, yp)
        self.root.geometry('{0}x{1}+{2}+{3}'.format(*geom))

        # call self.close_mod when the close button is pressed
        self.root.protocol("WM_DELETE_WINDOW", self.close_mod)

        # a trick to activate the window (on windows 7)
        self.root.deiconify()

        if entry:
            self.entry.focus_set()
        else:
            self.btn_1.focus_set()

        # wait for response before outputting result
        self.root.wait_window()

    def b1_action(self, event=None):
        if self.btn_1['state'] == 'disabled':
            return

        try:
            x = self.entry.get()
        except AttributeError:
            self.returning = self.b1_return
            self.root.destroy()
        else:
            if x:
                self.returning = x
                self.root.destroy()

    def b2_action(self, event=None):
        self.returning = self.b2_return
        self.root.destroy()

    def close_mod(self):
        self.returning = None
        self.root.destroy()

    def to_clip(self, event=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.msg)

    def check_input(self):
        if self.entry_var.get() == self.disabled_btn_input:
            self.btn_1.config(state=tk.ACTIVE)
        else:
            self.btn_1.config(state=tk.DISABLED)


def add_circle(parent, pixels, color):
    canvas = tkd.Canvas(parent, width=pixels + 2, height=pixels + 2, borderwidth=0, highlightthickness=0)

    cpix = pixels // 2
    circ_id = canvas.create_circle(cpix, cpix, cpix, fill=color, width=0.5)  # outline = 'black'
    canvas.create_circle_arc(cpix, cpix, pixels // 2.2, style="arc", outline="white", width=pixels // 12.5,
                             start=270 - 25, end=270 + 25)
    return canvas, circ_id


if __name__ == '__main__':
    print(MessageBox('Type "DELETE" to confirm', entry=True, disabled_btn_input='DELETE').returning)
