import csv
from tkinter import ttk
from utils import tk_dynamic as tkd
from init import assets_path

available_themes = ['dark', 'blue', 'light']
used_base_style = 'clam'  # , 'default', 'winnative', 'clam', 'alt']


def _load_theme_colors():
    """Load theme colors from CSV file. Returns dict mapping theme names to color dictionaries."""
    theme_colors = {theme: {} for theme in available_themes}
    with open(assets_path + 'theme_colors.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for theme in available_themes:
                theme_colors[theme][row['color_property']] = row[theme].strip()
    return theme_colors


class Theme:
    def __init__(self, used_theme):
        # Defer ttk.Style() creation until after root window exists (lazy initialization)
        self._style = None
        self._used_base_style = used_base_style

        self.used_theme = used_theme
        
        # Load colors from CSV into dictionary
        all_themes = _load_theme_colors()
        self.colors = all_themes[used_theme]

    @property
    def style(self):
        """Lazy initialization of ttk.Style - only created when needed (after root window exists)"""
        if self._style is None:
            self._style = ttk.Style()
            self._style.theme_use(self._used_base_style)
        return self._style

    def apply_theme_style(self):
        settings = {
            'TCombobox': {
                'configure': {'selectbackground': self.colors['combohighlight_color'],
                              # 'selectforeground': 'grey90',
                              'fieldbackground': self.colors['combofield_color'],
                              'background': self.colors['dropdown_button_color'],
                              },
                'map': {'fieldbackground': [('readonly', self.colors['combofield_color'])],
                        'foreground': [('readonly', 'black')]}
            },
            "TNotebook": {
                "configure": {"background": self.colors['notebook_background_color'],
                              "tabmargins": [2, 4, 2, 0]}
            },
            "TNotebook.Tab": {
                "configure": {"padding": [2, 1],
                              "background": self.colors['tab_background_color'],
                              "foreground": self.colors['text_color'],
                              "lightcolor": self.colors['border_color']
                              },
                "map": {
                    "background": [("selected", self.colors['selected_tab_color']), ("active", self.colors['hover_tab_background_color'])],
                    "expand": [("selected", [2, 1, 2, 0])],
                    "padding": [],
                    "lightcolor": []
                    }
            },
            "TScrollbar": {
                "configure": {
                    "background": self.colors['sb_btn_background'],
                    "darkcolor": self.colors['sb_btn_border_se'],
                    "lightcolor": self.colors['sb_btn_border_nw'],
                    "troughcolor": self.colors['sb_bar_background'],
                    "bordercolor": self.colors['sb_bordercolor'],
                    "arrowcolor": self.colors['sb_arrowcolor'],
                    "gripcount": 0,
                },
                "map": {"background": [("active", self.colors['sb_select_btn'])]}
            },
        }

        self.style.theme_settings(used_base_style, settings=settings)
        self.style.map('Treeview', foreground=self.fixed_map('foreground'), background=self.fixed_map('background'))

    def update_colors(self):
        tkd.Tk.set_config(bg=self.colors['frame_color'], highlightbackground=self.colors['border_color'])
        tkd.Toplevel.set_config(bg=self.colors['frame_color'])
        tkd.Label.set_config(bg=self.colors['label_color'], fg=self.colors['text_color'])
        tkd.Hyperlink.set_config(bg=self.colors['label_color'], fg=self.colors['hyperlink_color'])
        tkd.RunLabel.set_config(bg=self.colors['label_color'], fg=self.colors['run_count_color'])
        tkd.Button.set_config(bg=self.colors['button_color'], fg=self.colors['button_text_color'])
        tkd.PauseButton.set_config(bg=self.colors['pause_button_color'], fg=self.colors['pause_button_text'])
        tkd.Listbox.set_config(bg=self.colors['listbox_color'], fg=self.colors['listbox_text'], highlightbackground=self.colors['border_color'])
        tkd.Frame.set_config(bg=self.colors['frame_color'])
        tkd.LabelFrame.set_config(bg=self.colors['frame_color'])
        tkd.Entry.set_config(bg=self.colors['entry_color'])
        tkd.RestrictedEntry.set_config(bg=self.colors['entry_color'])
        tkd.Radiobutton.set_config(bg=self.colors['button_color'], selectcolor=self.colors['activebutton_color'])
        tkd.Canvas.set_config(bg=self.colors['frame_color'])
        tkd.Text.set_config(bg=self.colors['listbox_color'], fg=self.colors['listbox_text'])
        tkd.ListboxLabel.set_config(bg=self.colors['listbox_color'], fg=self.colors['listbox_text'])
        tkd.ListboxFrame.set_config(bg=self.colors['listbox_color'])
        tkd.Checkbutton.set_config(activebackground=self.colors['label_color'], activeforeground=self.colors['text_color'],
                                   background=self.colors['label_color'], foreground=self.colors['text_color'],
                                   selectcolor=self.colors['active_checkbox_color'])
        tkd.EthGrailCheckbutton.set_config(activebackground=self.colors['listbox_color'], activeforeground=self.colors['text_color'],
                                           background=self.colors['listbox_color'], foreground=self.colors['text_color'],
                                           selectcolor=self.colors['listbox_color'])

    def fixed_map(self, option):
        # Fix for setting text colour for Tkinter 8.6.9
        # From: https://core.tcl.tk/tk/info/509cafafae
        #
        # Returns the style map for 'option' with any styles starting with
        # ('!disabled', '!selected', ...) filtered out.

        # style.map() returns an empty list for missing options, so this
        # should be future-safe.
        return [elm for elm in self.style.map('Treeview', query_opt=option) if
                elm[:2] != ('!disabled', '!selected') and elm[0] != '!disabled !selected']
