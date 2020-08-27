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


class Checkbutton(tk.Checkbutton):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Checkbutton.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

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


class Radiobutton(tk.Radiobutton):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Radiobutton.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

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

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        self.tipwindow.wm_attributes('-topmost', True)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

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
        self.heading(column, command=partial(callback, column, not reverse))

    def _sort_by_num(self, column, reverse):
        self._sort(column, reverse, lambda x: float('inf') if x == '' else float(x), self._sort_by_num)

    def _sort_by_perc(self, column, reverse):
        self._sort(column, reverse, lambda x: float('inf') if x == '' else float(x[:-1]), self._sort_by_perc)

    def _sort_by_name(self, column, reverse):
        self._sort(column, reverse, str, self._sort_by_name)
