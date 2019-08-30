import tkinter as tk


class Toplevel(tk.Toplevel):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class Canvas(tk.Canvas):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class Tk(tk.Tk):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class Label(tk.Label):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class Hyperlink(tk.Label):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class RunLabel(tk.Label):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class Frame(tk.Frame):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class Button(tk.Button):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class PauseButton(tk.Button):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class LabelFrame(tk.LabelFrame):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.LabelFrame.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class Listbox(tk.Listbox):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Listbox.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class Entry(tk.Entry):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Entry.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val


class Radiobutton(tk.Radiobutton):
    objects = []

    def __init__(self, *args, **kwargs):
        tk.Radiobutton.__init__(self, *args, **kwargs)
        self.__class__.objects.append(self)

    @property
    def my_config(self):
        return self._my_config

    @my_config.setter
    def my_config(self, val):
        self._my_config = val
        self.config(**self._my_config)

    @classmethod
    def set_config(cls, **val):
        for obj in cls.objects:
            obj.my_config = val
