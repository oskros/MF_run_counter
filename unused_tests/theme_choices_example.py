from utils import tk_dynamic as tkd
from tkinter import ttk
import tkinter as tk

themes = ['light', 'dark']
theme_map = {
    'light': {
        tkd.Tk: dict(bg='#f0f0ed'),
        tkd.Label: dict(bg='#f0f0ed', fg='black'),
        tkd.Button: dict(bg='gray85', fg='black'),
        tkd.LabelFrame: dict(bg='#f0f0ed'),
        tkd.Radiobutton: dict(bg='gray85', selectcolor='white')
    },
    'dark': {
        tkd.Tk: dict(bg='black'),
        tkd.Label: dict(bg='black', fg='#ffffff'),
        tkd.Button: dict(bg='gray47', fg='#ffffff'),
        tkd.LabelFrame: dict(bg='black'),
        tkd.Radiobutton: dict(bg='gray47', selectcolor='gray78')
    }
}


class ThemedTkinter:
    def __init__(self, theme=themes[0]):
        self.root = tkd.Tk()

        self.active_theme = theme
        self.theme_var = tk.StringVar(value=theme)
        self.make_widgets()

        self._change_theme()
        self.root.mainloop()

    def make_widgets(self):
        tkd.Label(self.root, text='This is a test application').pack()

        # Create a test row
        lf1 = tkd.LabelFrame(self.root)
        lf1.pack(expand=True, fill=tk.X)
        svar = tk.IntVar(value=0)

        tkd.Label(lf1, text='Option 1').pack(side=tk.LEFT)
        tkd.Radiobutton(lf1, text='Off', indicatoron=False, value=0, variable=svar).pack(side=tk.RIGHT)
        tkd.Radiobutton(lf1, text='On', indicatoron=False, value=1, variable=svar).pack(side=tk.RIGHT)

        # Create choice to change theme
        lf2 = tkd.LabelFrame(self.root)
        lf2.pack(expand=True, fill=tk.X)

        tkd.Label(lf2, text='Active theme').pack(side=tk.LEFT)
        theme_choices = ttk.Combobox(lf2, textvariable=self.theme_var, state='readonly', values=themes)
        theme_choices.bind("<FocusOut>", lambda e: theme_choices.selection_clear())
        theme_choices.bind("<<ComboboxSelected>>", lambda e: self._change_theme())
        theme_choices.config(width=11)
        theme_choices.pack(side=tk.RIGHT, fill=tk.X, padx=2)

    def _change_theme(self):
        if self.theme_var.get() != self.active_theme:
            self.active_theme = self.theme_var.get()
            chosen_theme = theme_map[self.active_theme]
            for k, v in chosen_theme.items():
                k.set_config(**v)


ThemedTkinter()
