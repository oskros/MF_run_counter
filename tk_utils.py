from init import *
import tk_dynamic as tkd
import tkinter as tk
import webbrowser


def build_time_str(elap):
    hours = int(elap / 3600)
    minutes = int(elap / 60 - hours * 60.0)
    seconds = int(elap - hours * 3600.0 - minutes * 60.0)
    hseconds = int((elap - hours * 3600.0 - minutes * 60.0 - seconds) * 10)
    return '%02d:%02d:%02d:%1d' % (hours, minutes, seconds, hseconds)


class TabSwitch:
    def _next_tab(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()

        nxt_idx = tabs.index(cur_tab) + 1
        if nxt_idx >= len(tabs):
            nxt_idx = 0
        self.tabcontrol.select(tabs[nxt_idx])

    def _prev_tab(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()

        prev_idx = tabs.index(cur_tab) - 1
        if prev_idx < 0:
            prev_idx = len(tabs) - 1
        self.tabcontrol.select(tabs[prev_idx])


class MovingFrame:
    def _start_move(self, event):
        self.x = event.x
        self.y = event.y

    def _stop_move(self, event):
        self.x = None
        self.y = None

    def _on_motion(self, event):
        try:
            deltax = event.x - self.x
            deltay = event.y - self.y
        except (TypeError, AttributeError):
            return
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry("+%s+%s" % (x, y))


class RegistrationForm:
    def __init__(self, coords):
        self.new_win = tk.Tk()
        self.new_win.title('Profile registration')
        self.new_win.wm_attributes('-topmost', 1)
        if coords is not None:
            self.new_win.geometry('+%d+%d' % (coords[0], coords[1]))
        self.new_win.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        self.allowed_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

        l = tk.Label(self.new_win, text='Profile registration', font='Helvetica 14')
        l.pack()

        self.a1 = self.make_row('Profile name')
        self.a2 = self.make_row('Character name')
        self.a3 = self.make_row('Run type')
        self.a4 = self.make_row('Active MF %')

        # Restrict input to profile name, only allowing characters that can appear in a windows file name
        vcmd = (self.new_win.register(self.validate_input), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.a1.config(validate='key', validatecommand=vcmd)

        tk.Button(self.new_win, text='Submit', font='helvetica 12 bold', command=self.b1_action, bd=2).pack(fill=tk.X, expand=tk.YES)
        self.new_win.bind('<KeyPress-Return>', func=self.b1_action)
        self.new_win.bind('<KeyPress-Escape>', func=lambda e: self.close_mod())

        self.new_win.protocol("WM_DELETE_WINDOW", self.close_mod)
        self.a1.focus_set()

    def b1_action(self, event=None):
        try:
            a1 = self.a1.get()
            a2 = self.a2.get()
            a3 = self.a3.get()
            a4 = self.a4.get()

            x = {'Profile name': a1, 'Character name': a2, 'Run type': a3, 'Active MF %': a4}
        except AttributeError:
            self.returning = None
            self.new_win.quit()
        else:
            self.returning = x
            self.new_win.quit()

    def make_row(self, text):
        frame = tk.Frame(self.new_win)
        frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(frame, width=22, text=text + ': ', anchor=tk.W).pack(side=tk.LEFT)
        var = tk.StringVar()
        out = tk.Entry(frame, textvariable=var)
        out.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        return out

    def validate_input(self, *args):
        if args[0] == '1':
            return args[4] in self.allowed_chars
        else:
            return True

    def close_mod(self):
        self.returning = None
        self.new_win.quit()


def registration_form(coords=None):
    reg_form = RegistrationForm(coords)
    reg_form.new_win.focus_force()
    reg_form.new_win.mainloop()

    reg_form.new_win.destroy()
    return reg_form.returning


class MessageBox(object):
    def __init__(self, msg, b1, b2, entry, coords, title, hyperlink):
        root = self.root = tk.Tk()
        self.root.focus_set()
        root.title(title)
        self.root.attributes("-toolwindow", True)
        self.root.wm_attributes("-topmost", True)
        self.msg = str(msg)

        # ctrl+c to copy self.msg
        root.bind('<Control-c>', func=self.to_clip)

        # default values for the buttons to return
        self.b1_return = True
        self.b2_return = False

        # if b1 or b2 is a tuple unpack into the button text & return value
        if isinstance(b1, tuple):
            b1, self.b1_return = b1
        if isinstance(b2, tuple):
            b2, self.b2_return = b2

        # main frame
        frm_1 = tk.Frame(root)
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
            self.entry = tk.Entry(frm_1, font=('arial', 11), justify='center')
            self.entry.pack()
            self.entry.focus_set()

        # button frame
        frm_2 = tk.Frame(frm_1)
        frm_2.pack(padx=4, pady=4)

        # buttons
        btn_1 = tk.Button(frm_2, width=8, text=b1)
        btn_1['command'] = self.b1_action
        btn_1.pack(side='left')
        if not entry:
            btn_1.focus_set()
        if b2 != '':
            btn_2 = tk.Button(frm_2, width=8, text=b2)
            btn_2['command'] = self.b2_action
            btn_2.pack(side='left')

        # The enter button will trigger button 1, while escape will close the window
        root.bind('<KeyPress-Return>', func=self.b1_action)
        root.bind('<KeyPress-Escape>', func=lambda e: self.close_mod())

        # Roughly center the box on screen. For accuracy see: https://stackoverflow.com/a/10018670/1217270
        root.update_idletasks()
        if coords:
            xp = coords[0]
            yp = coords[1]
        else:
            xp = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
            yp = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        geom = (root.winfo_width(), root.winfo_height(), xp, yp)
        root.geometry('{0}x{1}+{2}+{3}'.format(*geom))

        # call self.close_mod when the close button is pressed
        root.protocol("WM_DELETE_WINDOW", self.close_mod)

        # a trick to activate the window (on windows 7)
        root.deiconify()

    def b1_action(self, event=None):
        try:
            x = self.entry.get()
        except AttributeError:
            self.returning = self.b1_return
            self.root.quit()
        else:
            if x:
                self.returning = x
                self.root.quit()

    def b2_action(self, event=None):
        self.returning = self.b2_return
        self.root.quit()

    def close_mod(self):
        self.returning = None
        self.root.quit()

    def to_clip(self, event=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.msg)


def mbox(msg, b1='OK', b2='Cancel', entry=False, coords=False, title='Message', hyperlink=''):
    msgbox = MessageBox(msg, b1, b2, entry, coords, title, hyperlink)
    msgbox.root.mainloop()

    # the function pauses here until the mainloop is quit
    msgbox.root.destroy()
    return msgbox.returning


def add_circle(parent, pixels, color):
    canvas = tkd.Canvas(parent, width=pixels + 2, height=pixels + 2, borderwidth=0, highlightthickness=0)

    cpix = pixels // 2
    circ_id = canvas.create_circle(cpix, cpix, cpix, fill=color, width=0.5)  # outline = 'black'
    canvas.create_circle_arc(cpix, cpix, pixels // 2.2, style="arc", outline="white", width=pixels // 12.5,
                             start=270 - 25, end=270 + 25)
    return canvas, circ_id


if __name__ == '__main__':
    print(registration_form())