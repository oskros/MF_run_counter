import tkinter as tk


class MessageBox(object):
    def __init__(self, msg, b1, b2, frame, entry):
        root = self.root = tk.Tk()
        self.root.focus_set()
        root.title('Message')
        self.root.attributes("-toolwindow", True)
        self.root.wm_attributes("-topmost", True)
        # self.root.overrideredirect(True)
        # self.root.config(borderwidth=3, relief='raised')
        self.msg = str(msg)
        # ctrl+c to copy self.msg
        root.bind('<Control-c>', func=self.to_clip)
        # remove the outer frame if frame=False
        if not frame: root.overrideredirect(True)
        # default values for the buttons to return
        self.b1_return = True
        self.b2_return = False
        # if b1 or b2 is a tuple unpack into the button text & return value
        if isinstance(b1, tuple): b1, self.b1_return = b1
        if isinstance(b2, tuple): b2, self.b2_return = b2
        # main frame
        frm_1 = tk.Frame(root)
        frm_1.pack(ipadx=2, ipady=2)
        # the message
        message = tk.Label(frm_1, text=self.msg, font=('arial', 11))
        message.pack(padx=8, pady=8)
        # if entry=True create and set focus
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
        if not entry: btn_1.focus_set()
        btn_2 = tk.Button(frm_2, width=8, text=b2)
        btn_2['command'] = self.b2_action
        btn_2.pack(side='left')
        # the enter button will trigger the focused button's action
        root.bind('<KeyPress-Return>', func=self.b1_action)
        root.bind('<KeyPress-Escape>', func=self.b2_action)
        # roughly center the box on screen
        # for accuracy see: https://stackoverflow.com/a/10018670/1217270
        root.update_idletasks()
        xp = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        yp = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        geom = (root.winfo_width(), root.winfo_height(), xp, yp)
        root.geometry('{0}x{1}+{2}+{3}'.format(*geom))
        # call self.close_mod when the close button is pressed
        root.protocol("WM_DELETE_WINDOW", self.close_mod)
        # a trick to activate the window (on windows 7)
        root.deiconify()
        # if t is specified: call time_out after t seconds

    def b1_action(self, event=None):
        try: x = self.entry.get()
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
        self.b2_action()

    def to_clip(self, event=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.msg)


def mbox(msg, b1='OK', b2='Cancel', frame=True, entry=False):
    """Create an instance of MessageBox, and get data back from the user.
    msg = string to be displayed
    b1 = text for left button, or a tuple (<text for button>, <to return on press>)
    b2 = text for right button, or a tuple (<text for button>, <to return on press>)
    frame = include a standard outerframe: True or False
    t = time in seconds (int or float) until the msgbox automatically closes
    entry = include an entry widget that will have its contents returned: True or False
    """
    msgbox = MessageBox(msg, b1, b2, frame, entry)
    msgbox.root.mainloop()
    # the function pauses here until the mainloop is quit
    msgbox.root.destroy()
    return msgbox.returning
