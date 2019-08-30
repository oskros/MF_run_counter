from tkinter import ttk
import tk_dynamic as tkd
available_themes = ['blue', 'dark', 'vista']


class Theme:
    def __init__(self, used_theme):
        self.used_theme = used_theme
        if self.used_theme == 'blue':
            # General
            default_color = 'light blue'
            self.ttk_style = 'clam'

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
            self.button_color = 'light sky blue'
            self.activebutton_color = 'white'
            self.listbox_color = 'white'
            self.pause_button_color = 'DodgerBlue2'
            self.circle_border_color = 'black'
            self.entry_color = 'white'

            # Text
            self.text_color = 'black'
            self.run_count_color = 'red'
            self.hyperlink_color = 'blue'
            self.listbox_text = 'black'
            self.pause_button_text = 'black'

            # Selecting Comboboxes
            self.combohighlight_color = 'black'  # Highlight selection color
            self.combofield_color = 'lavender'  # Background of the combobox
            self.dropdown_button_color = 'cornflower blue'  # Color of the dropdown button
            self.combo_listbox_foreground = 'black'
            self.combo_listbox_selectbackground = 'black'
            self.combo_listbox_selectforeground = 'white'
        elif self.used_theme == 'dark':
            # General
            default_color = 'black'
            self.ttk_style = 'clam'

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
            self.button_color = 'grey40'
            self.activebutton_color = 'grey78'
            self.listbox_color = 'grey33'
            self.pause_button_color = 'deep sky blue'
            self.circle_border_color = 'grey33'
            self.entry_color = 'grey78'

            # Text
            self.text_color = '#ffffff'
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
        elif self.used_theme == 'vista':
            # General
            default_color = '#f0f0ed'
            self.ttk_style = 'vista'

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
            self.button_color = default_color
            self.activebutton_color = 'white'
            self.listbox_color = 'white'
            self.pause_button_color = 'deep sky blue'
            self.circle_border_color = 'black'
            self.entry_color = 'white'

            # Text
            self.text_color = 'black'
            self.run_count_color = 'red'
            self.hyperlink_color = 'blue'
            self.listbox_text = 'black'
            self.pause_button_text = 'black'

            # Selecting Comboboxes
            self.combohighlight_color = 'blue'  # Highlight selection color
            self.combofield_color = 'white'  # Background of the combobox
            self.dropdown_button_color = 'white'  # Color of the dropdown button
            self.combo_listbox_foreground = 'black'
            self.combo_listbox_selectbackground = 'black'
            self.combo_listbox_selectforeground = 'white'
        else:
            raise NotImplementedError

        self.apply_theme_style()
        self.update_colors()

    def apply_theme_style(self):
        style = ttk.Style()
        style_name = 'my_' + self.used_theme if self.used_theme != 'vista' else self.used_theme
        if style_name not in style.theme_names() and self.used_theme != 'vista':
            style.theme_create(style_name, parent=self.ttk_style,
                               settings={'TCombobox':
                                             {'configure':
                                                  {'selectbackground': self.combohighlight_color,
                                                   # 'selectforeground': 'grey90',
                                                   'fieldbackground': self.combofield_color,
                                                   'background': self.dropdown_button_color,
                                                   }},
                                         "TNotebook": {
                                             "configure": {"background": self.notebook_background_color,
                                                           "tabmargins": [2, 4, 2, 0]}
                                         },
                                         "TNotebook.Tab": {
                                             "configure": {"padding": [2, 1],
                                                           "background": self.tab_background_color,
                                                           "foreground": self.text_color,
                                                           "lightcolor": self.border_color},
                                             "map": {"background": [("selected", self.selected_tab_color),
                                                                    ("active", self.hover_tab_background_color)],
                                                     "expand": [("selected", [2, 1, 2, 0])]}}
                                         }
                               )
        style.theme_use(style_name)

    def update_colors(self):
        tkd.Tk.set_config(bg=self.frame_color, highlightbackground=self.border_color)
        tkd.Toplevel.set_config(bg=self.frame_color)
        tkd.Label.set_config(bg=self.label_color, fg=self.text_color)
        tkd.Hyperlink.set_config(bg=self.label_color, fg=self.hyperlink_color)
        tkd.RunLabel.set_config(bg=self.label_color, fg=self.run_count_color)
        tkd.Button.set_config(bg=self.button_color, fg=self.text_color)
        tkd.PauseButton.set_config(bg=self.pause_button_color, fg=self.pause_button_text)
        tkd.Listbox.set_config(bg=self.listbox_color, fg=self.listbox_text, highlightbackground=self.border_color)
        tkd.Frame.set_config(bg=self.frame_color)
        tkd.LabelFrame.set_config(bg=self.frame_color)
        tkd.Entry.set_config(bg=self.entry_color)
        tkd.Radiobutton.set_config(bg=self.button_color, selectcolor=self.activebutton_color)
        tkd.Canvas.set_config(bg=self.frame_color)