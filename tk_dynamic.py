import tkinter as tk


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
        self.__class__.objects.pop()
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
        self.__class__.objects.pop()
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
        self.__class__.objects.pop()
        tk.Tk.destroy(self)


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
        self.__class__.objects.pop()
        tk.Label.destroy(self)


class Hyperlink(tk.Label):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        self.__class__.objects.pop()
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
        self.__class__.objects.pop()
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
        self.__class__.objects.pop()
        tk.Frame.destroy(self)


class Button(tk.Button):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.config(val)

    def destroy(self):
        self.__class__.objects.pop()
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
        self.__class__.objects.pop()
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
        self.__class__.objects.pop()
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
        self.__class__.objects.pop()
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
        self.__class__.objects.pop()
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
        self.__class__.objects.pop()
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
        self.__class__.objects.pop()
        tk.Radiobutton.destroy(self)
