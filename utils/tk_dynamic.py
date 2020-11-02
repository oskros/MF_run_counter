from init import *
import os, sys
import tkinter as tk
from tkinter import ttk
import webbrowser
from functools import partial


class Toplevel(tk.Toplevel):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Toplevel.destroy(self)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_motion(self, event):
        try:
            deltax = event.x - self.x
            deltay = event.y - self.y
        except (TypeError, AttributeError):
            return
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry("+%s+%s" % (x, y))

    def moveleft(self, event):
        x = self.winfo_x() - 1
        y = self.winfo_y()
        self.geometry("+%s+%s" % (x, y))

    def moveright(self, event):
        x = self.winfo_x() + 1
        y = self.winfo_y()
        self.geometry("+%s+%s" % (x, y))

    def moveup(self, event):
        x = self.winfo_x()
        y = self.winfo_y() - 1
        self.geometry("+%s+%s" % (x, y))

    def movedown(self, event):
        x = self.winfo_x()
        y = self.winfo_y() + 1
        self.geometry("+%s+%s" % (x, y))


class Canvas(tk.Canvas):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Canvas.destroy(self)

    def create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def create_circle_arc(self, x, y, r, **kwargs):
        if "start" in kwargs and "end" in kwargs:
            kwargs["extent"] = kwargs["end"] - kwargs["start"]
            del kwargs["end"]
        return self.create_arc(x - r, y - r, x + r, y + r, **kwargs)

    def stroke_text(self, x, y, textcolor, strokecolor, **kwargs):
        # make stroke text
        self.create_text(x, y, font=('courier', 16, 'bold'), fill=strokecolor, **kwargs)
        # make regular text
        self.create_text(x, y, font=('courier', 16), fill=textcolor, **kwargs)


class Tk(tk.Tk):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Tk.destroy(self)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_motion(self, event):
        try:
            deltax = event.x - self.x
            deltay = event.y - self.y
        except (TypeError, AttributeError):
            return
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry("+%s+%s" % (x, y))

    def moveleft(self, event):
        x = self.winfo_x() - 1
        y = self.winfo_y()
        self.geometry("+%s+%s" % (x, y))

    def moveright(self, event):
        x = self.winfo_x() + 1
        y = self.winfo_y()
        self.geometry("+%s+%s" % (x, y))

    def moveup(self, event):
        x = self.winfo_x()
        y = self.winfo_y() - 1
        self.geometry("+%s+%s" % (x, y))

    def movedown(self, event):
        x = self.winfo_x()
        y = self.winfo_y() + 1
        self.geometry("+%s+%s" % (x, y))


class Notebook(ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        ttk.Notebook.__init__(self, master=master, **kwargs)

    def next_tab(self):
        tabs = self.tabs()
        cur_tab = self.select()

        nxt_idx = tabs.index(cur_tab) + 1
        if nxt_idx >= len(tabs):
            nxt_idx = 0
        self.select(tabs[nxt_idx])

    def prev_tab(self):
        tabs = self.tabs()
        cur_tab = self.select()

        prev_idx = tabs.index(cur_tab) - 1
        if prev_idx < 0:
            prev_idx = len(tabs) - 1
        self.select(tabs[prev_idx])


class Label(tk.Label):
    objects = []

    def __init__(self, *args, **kwargs):
        tooltip = kwargs.pop('tooltip', None)
        tk.Label.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)
        if tooltip is not None:
            create_tooltip(self, tooltip)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Label.destroy(self)


class Checkbutton(tk.Checkbutton):
    objects = []

    def __init__(self, *args, **kwargs):
        tooltip = kwargs.pop('tooltip', None)
        tk.Checkbutton.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)
        if tooltip is not None:
            create_tooltip(self, tooltip)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Checkbutton.destroy(self)


class EthGrailCheckbutton(tk.Checkbutton):
    objects = []

    def __init__(self, *args, **kwargs):
        tooltip = kwargs.pop('tooltip', None)
        tk.Checkbutton.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)
        if tooltip is not None:
            create_tooltip(self, tooltip)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Checkbutton.destroy(self)


class ListboxLabel(tk.Label):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Label.destroy(self)


class Hyperlink(tk.Label):
    objects = []

    def __init__(self, *args, **kwargs):
        hyperlink = kwargs.pop('hyperlink')
        cs = kwargs.pop('cursor', 'hand2')
        tk.Label.__init__(self, *args, **kwargs, cursor=cs)
        self.__class__.objects.append(self)
        self.bind("<Button-1>", lambda e: webbrowser.open_new(hyperlink))

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Label.destroy(self)


class RunLabel(tk.Label):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Label.destroy(self)


class Frame(tk.Frame):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Frame.destroy(self)


class ListboxFrame(tk.LabelFrame):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.LabelFrame.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.LabelFrame.destroy(self)


class Button(tk.Button):
    objects = []

    def __init__(self, *args, **kwargs):
        tooltip = kwargs.pop('tooltip', None)
        tk.Button.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)
        if tooltip is not None:
            create_tooltip(self, tooltip)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Button.destroy(self)


class PauseButton(tk.Button):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Button.destroy(self)


class LabelFrame(tk.LabelFrame):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.LabelFrame.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.LabelFrame.destroy(self)


class Listbox(tk.Listbox):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Listbox.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Listbox.destroy(self)


class Listbox2(tk.Listbox):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Listbox.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Listbox.destroy(self)


class Entry(tk.Entry):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Entry.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Entry.destroy(self)


class RestrictedEntry(tk.Entry):
    objects = []

    def __init__(self, *args, **kwargs):
        self.num_only = kwargs.pop('num_only', False)
        tk.Entry.__init__(self, *args, **kwargs)
        if self.num_only:
            self.allowed_chars = '.0123456789'
        else:
            self.allowed_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

        vcmd = (self.register(self.validate_input), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.config(validate='key', validatecommand=vcmd)

        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Entry.destroy(self)

    def validate_input(self, *args):
        if args[0] == '1':
            if self.num_only and args[4] == '.' and '.' in args[3]:
                return False
            return args[4] in self.allowed_chars
        else:
            return True


class Radiobutton(tk.Radiobutton):
    objects = []

    def __init__(self, *args, **kwargs):
        tooltip = kwargs.pop('tooltip', None)
        tk.Radiobutton.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)
        if tooltip is not None:
            create_tooltip(self, tooltip)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Radiobutton.destroy(self)


class Text(tk.Text):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

        self.tag_configure('currentLine', background='#1874CD', foreground='white')
        self.bind('<Button-1>', lambda _: self.highlight_line())

        self.bind('<FocusOut>', lambda e: self.tag_remove('currentLine', 1.0, tk.END))
        self.bind('<FocusIn>', lambda e: self.tag_add('currentLine', 'insert linestart', 'insert lineend+1c'))

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        cur_obj = next(idx for idx, x in enumerate(self.objects) if x.bindtags() == self.bindtags())
        del self.__class__.objects[cur_obj]
        tk.Text.destroy(self)

    def highlight_line(self, delay=10):
        def delayed_highlight():
            self.tag_remove('currentLine', 1.0, tk.END)
            self.tag_add('currentLine', 'insert linestart', 'insert lineend+1c')
        # This bound function is called before the cursor actually moves.
        # So delay checking the cursor position and moving the highlight 10 ms.

        self.after(delay, delayed_highlight)


class Tooltip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    # @staticmethod
    # def get_monitor_from_coord(x, y):
    #     monitors = screeninfo.get_monitors()
    #
    #     for m in reversed(monitors):
    #         if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
    #             return m
    #     return monitors[0]
    #
    # def get_displaced_geom(self, root, window_width, window_height, pos_x, pos_y):
    #     mon = self.get_monitor_from_coord(root.winfo_rootx(), root.winfo_rooty())
    #     min_x = mon.x
    #     min_y = mon.y
    #     max_x = mon.width + min_x
    #     max_y = mon.height + min_y
    #
    #     displaced_x = max(min(pos_x, max_x - window_width), min_x - 5)
    #     displaced_y = max(min(pos_y, max_y - window_height), min_y)
    #
    #     return '%sx%s+%s+%s' % (window_width, window_height, displaced_x, displaced_y)

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")

        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27

        self.tipwindow = tw = tk.Toplevel(self.widget)
        self.tipwindow.wm_attributes('-topmost', True)
        tw.wm_overrideredirect(1)

        # tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)


        # tw.update()
        # geom = self.get_displaced_geom(self.widget, self.tipwindow.winfo_width(), self.tipwindow.winfo_height(), x, y)
        # tw.wm_geometry(geom)

        geom = "+%d+%d" % (x, y)
        tw.wm_geometry(geom)


    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def create_tooltip(widget, text):
    tooltip = Tooltip(widget)
    widget.bind('<Enter>', lambda event: tooltip.showtip(text))
    widget.bind('<Leave>', lambda event: tooltip.hidetip())


class Treeview(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        self.alternate_colour = kwargs.pop('alternate_colour', False)
        ttk.Treeview.__init__(self, *args, **kwargs)
        if self.alternate_colour:
            self.tag_configure('Odd', background='white')
            self.tag_configure('Even', background='gray95')

    def heading(self, column, sort_by=None, **kwargs):
        if sort_by and not hasattr(kwargs, 'command'):
            func = getattr(self, f"_sort_by_{sort_by}", None)
            if func:
                kwargs['command'] = partial(func, column, False)
        return super().heading(column, **kwargs)

    def _sort(self, column, reverse, data_type, callback):
        l = [(self.set(k, column), k) for k in self.get_children('')]
        l.sort(key=lambda t: data_type(t[0]), reverse=reverse)
        for index, (_, k) in enumerate(l):
            self.move(k, '', index)
            if self.alternate_colour:
                self.item(k, tag='Even' if index % 2 != 0 else 'Odd')
        self.heading(column, command=partial(callback, column, not reverse))

    def _sort_by_num(self, column, reverse):
        if reverse:
            foo = lambda x: float('-inf') if x == '' else float(x.replace('%', ''))
        else:
            foo = lambda x: float('inf') if x == '' else float(x.replace('%', ''))
        self._sort(column, reverse, foo, self._sort_by_num)

    def _sort_by_name(self, column, reverse):
        self._sort(column, reverse, str, self._sort_by_name)


class CaretButton(Button):
    def __init__(self, root, command=lambda: None, active=False, **kwargs):
        tooltip = kwargs.pop('tooltip', None)
        self.command = lambda: self.run_command(command)
        up_arrow_path = media_path + 'caret-up.png'
        dn_arrow_path = media_path + 'caret-down.png'

        pic_geom = (374, 43)
        new_geom = (130, 14)

        self.up_arrow = tk.PhotoImage(file=up_arrow_path).subsample(pic_geom[0]//new_geom[0], pic_geom[1]//new_geom[1])
        self.dn_arrow = tk.PhotoImage(file=dn_arrow_path).subsample(pic_geom[0]//new_geom[0], pic_geom[1]//new_geom[1])

        self.active = bool(active)
        Button.__init__(self, root, image=self.up_arrow if self.active else self.dn_arrow, command=self.command, **kwargs)
        if tooltip is not None:
            create_tooltip(self, tooltip)

    def run_command(self, command):
        self.active = not self.active
        # print(self.active)
        self.config(image=self.up_arrow if self.active else self.dn_arrow)
        command()

    def toggle_image(self, active=None):
        if active is None:
            self.active = not self.active
        else:
            self.active = active
        self.config(image=self.up_arrow if self.active else self.dn_arrow)


if __name__ == '__main__':
    root = tk.Tk()
    CaretButton(root, active=False).pack()

    root.mainloop()
