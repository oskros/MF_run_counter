from tkinter import ttk
from utils import tk_dynamic as tkd

available_themes = ['dark', 'blue', 'light']
used_base_style = 'clam'  # , 'default', 'winnative', 'clam', 'alt']


class Theme:
    def __init__(self, used_theme):
        self.style = ttk.Style()
        self.style.theme_use(used_base_style)

        self.used_theme = used_theme
        if self.used_theme == 'blue':
            # General
            default_color = 'LightSkyBlue1'

            # Backgrounds
            self.frame_color = default_color
            self.border_color = default_color
            self.label_color = default_color
            self.notebook_background_color = default_color

            # Tab colors
            self.selected_tab_color = 'alice blue'
            self.hover_tab_background_color = 'lavender'
            self.tab_background_color = self.frame_color

            # Widgets
            self.button_color = 'SkyBlue1'
            self.activebutton_color = 'alice blue'
            self.active_checkbox_color = 'alice blue'
            self.listbox_color = 'alice blue'
            self.pause_button_color = 'DodgerBlue2'
            self.circle_border_color = 'black'
            self.entry_color = 'alice blue'

            # Text
            self.text_color = 'black'
            self.button_text_color = 'black'
            self.run_count_color = 'red'
            self.hyperlink_color = 'blue'
            self.listbox_text = 'black'
            self.pause_button_text = 'black'

            # Selecting Comboboxes
            self.combohighlight_color = 'black'  # Highlight selection color
            self.combofield_color = 'alice blue'  # Background of the combobox
            self.dropdown_button_color = 'cornflower blue'  # Color of the dropdown button
            self.combo_listbox_foreground = 'black'
            self.combo_listbox_selectbackground = 'black'
            self.combo_listbox_selectforeground = 'white'

            # Scrollbars
            self.sb_btn_background = 'cornflower blue'
            self.sb_btn_border_se = 'black'
            self.sb_btn_border_nw = 'white'
            self.sb_bar_background = 'lavender'
            self.sb_bordercolor = 'grey50'
            self.sb_arrowcolor = 'white'
            self.sb_select_btn = 'DodgerBlue3'

        elif self.used_theme == 'dark':
            # General
            default_color = 'black'

            # Backgrounds
            self.frame_color = default_color
            self.label_color = default_color
            self.border_color = 'dark grey'
            self.notebook_background_color = 'grey10'

            # Tab colors
            self.tab_background_color = self.frame_color
            self.selected_tab_color = 'grey20'
            self.hover_tab_background_color = 'grey30'

            # Widgets
            self.button_color = 'grey47'
            self.activebutton_color = 'grey78'
            self.active_checkbox_color = 'gray20'
            self.listbox_color = 'grey33'
            self.pause_button_color = 'deep sky blue'
            self.circle_border_color = 'grey33'
            self.entry_color = 'grey78'

            # Text
            self.text_color = '#ffffff'
            self.button_text_color = 'white'
            self.run_count_color = 'dark orange'
            self.hyperlink_color = 'dodger blue'
            self.listbox_text = 'white'
            self.pause_button_text = 'black'

            # Selecting Comboboxes
            self.combohighlight_color = 'blue'  # Highlight selection color
            self.combofield_color = 'grey90'  # Background of the combobox
            self.dropdown_button_color = 'grey70'  # Color of the dropdown button
            self.combo_listbox_foreground = 'black'
            self.combo_listbox_selectbackground = 'black'
            self.combo_listbox_selectforeground = 'white'

            # Scrollbars
            self.sb_btn_background = 'grey50'
            self.sb_btn_border_se = 'black'
            self.sb_btn_border_nw = 'grey90'
            self.sb_bar_background = 'grey70'
            self.sb_bordercolor = 'grey50'
            self.sb_arrowcolor = 'white'
            self.sb_select_btn = 'grey35'

        else:
            # General
            default_color = '#f0f0ed'

            # Backgrounds
            self.frame_color = default_color
            self.border_color = default_color
            self.label_color = default_color
            self.notebook_background_color = default_color

            # Tab colors
            self.selected_tab_color = 'white'
            self.hover_tab_background_color = 'white'
            self.tab_background_color = self.frame_color

            # Widgets
            self.button_color = 'grey85'
            self.activebutton_color = 'white'
            self.active_checkbox_color = 'white'
            self.listbox_color = 'white'
            self.pause_button_color = 'deep sky blue'
            self.circle_border_color = 'black'
            self.entry_color = 'white'

            # Text
            self.text_color = 'black'
            self.button_text_color = 'black'
            self.checkbox_text = 'black'
            self.run_count_color = 'red'
            self.hyperlink_color = 'blue'
            self.listbox_text = 'black'
            self.pause_button_text = 'black'

            # Selecting Comboboxes
            self.combohighlight_color = 'blue'  # Highlight selection color
            self.combofield_color = 'white'  # Background of the combobox
            self.dropdown_button_color = 'grey90'  # Color of the dropdown button
            self.combo_listbox_foreground = 'black'
            self.combo_listbox_selectbackground = 'black'
            self.combo_listbox_selectforeground = 'white'

            # Scrollbars
            self.sb_btn_background = 'grey70'
            self.sb_btn_border_se = 'grey70'
            self.sb_btn_border_nw = 'grey70'
            self.sb_bar_background = default_color
            self.sb_bordercolor = default_color
            self.sb_arrowcolor = 'black'
            self.sb_select_btn = 'grey50'

    def apply_theme_style(self):
        settings = {
            'TCombobox': {
                'configure': {'selectbackground': self.combohighlight_color,
                              # 'selectforeground': 'grey90',
                              'fieldbackground': self.combofield_color,
                              'background': self.dropdown_button_color,
                              },
                'map': {'fieldbackground': [('readonly', self.combofield_color)],
                        'foreground': [('readonly', 'black')]}
            },
            "TNotebook": {
                "configure": {"background": self.notebook_background_color,
                              "tabmargins": [2, 4, 2, 0]}
            },
            "TNotebook.Tab": {
                "configure": {"padding": [2, 1],
                              "background": self.tab_background_color,
                              "foreground": self.text_color,
                              "lightcolor": self.border_color
                              },
                "map": {
                    "background": [("selected", self.selected_tab_color), ("active", self.hover_tab_background_color)],
                    "expand": [("selected", [2, 1, 2, 0])],
                    "padding": [],
                    "lightcolor": []
                    }
            },
            "TScrollbar": {
                "configure": {
                    "background": self.sb_btn_background,
                    "darkcolor": self.sb_btn_border_se,
                    "lightcolor": self.sb_btn_border_nw,
                    "troughcolor": self.sb_bar_background,
                    "bordercolor": self.sb_bordercolor,
                    "arrowcolor": self.sb_arrowcolor,
                    "gripcount": 0,
                },
                "map": {"background": [("active", self.sb_select_btn)]}
            },
        }

        self.style.theme_settings(used_base_style, settings=settings)
        self.style.map('Treeview', foreground=self.fixed_map('foreground'), background=self.fixed_map('background'))

    def update_colors(self):
        tkd.Tk.set_config(bg=self.frame_color, highlightbackground=self.border_color)
        tkd.Toplevel.set_config(bg=self.frame_color)
        tkd.Label.set_config(bg=self.label_color, fg=self.text_color)
        tkd.Hyperlink.set_config(bg=self.label_color, fg=self.hyperlink_color)
        tkd.RunLabel.set_config(bg=self.label_color, fg=self.run_count_color)
        tkd.Button.set_config(bg=self.button_color, fg=self.button_text_color)
        tkd.PauseButton.set_config(bg=self.pause_button_color, fg=self.pause_button_text)
        tkd.Listbox.set_config(bg=self.listbox_color, fg=self.listbox_text, highlightbackground=self.border_color)
        tkd.Frame.set_config(bg=self.frame_color)
        tkd.LabelFrame.set_config(bg=self.frame_color)
        tkd.Entry.set_config(bg=self.entry_color)
        tkd.RestrictedEntry.set_config(bg=self.entry_color)
        tkd.Radiobutton.set_config(bg=self.button_color, selectcolor=self.activebutton_color)
        tkd.Canvas.set_config(bg=self.frame_color)
        tkd.Text.set_config(bg=self.listbox_color, fg=self.listbox_text)
        tkd.ListboxLabel.set_config(bg=self.listbox_color, fg=self.listbox_text)
        tkd.ListboxFrame.set_config(bg=self.listbox_color)
        tkd.Checkbutton.set_config(activebackground=self.label_color, activeforeground=self.text_color,
                                   background=self.label_color, foreground=self.text_color,
                                   selectcolor=self.active_checkbox_color)
        tkd.EthGrailCheckbutton.set_config(activebackground=self.listbox_color, activeforeground=self.text_color,
                                           background=self.listbox_color, foreground=self.text_color,
                                           selectcolor=self.listbox_color)

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
