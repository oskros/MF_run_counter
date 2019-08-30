from tkinter import ttk
available_themes = ['ugly_blue', 'dark', 'default']


class Theme:
    def __init__(self, used_theme):
        if used_theme == 'ugly_blue':
            # General
            default_color = 'light sky blue'
            self.ttk_style = 'clam'

            # Backgrounds
            self.frame_color = default_color
            self.border_color = default_color
            self.label_color = default_color
            self.notebook_background = default_color

            # Widgets
            self.button_color = '#40ccd0'
            self.activebutton_color = 'white'
            self.listbox_color = 'white'
            self.pause_button_color = 'deep sky blue'
            self.circle_border_color = 'black'
            self.entry_color = 'white'

            # Text
            self.text_color = '#ffffff'
            self.run_count_color = 'red'
            self.hyperlink_color = 'blue'
            self.listbox_text = 'black'
            self.pause_button_text = 'black'

            # Selecting Comboboxes
            self.combohighlight_color = 'black'  # Highlight selection color
            self.combofield_color = 'SteelBlue1'  # Background of the combobox
            self.dropdown_button_color = 'blue'  # Color of the dropdown button

        elif used_theme == 'dark':
            # General
            default_color = 'black'
            self.ttk_style = 'clam'

            # Backgrounds
            self.frame_color = default_color
            self.label_color = default_color
            self.border_color = 'dark grey'
            self.notebook_background = 'grey10'

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

        elif used_theme == 'default':
            # General
            default_color = '#f0f0ed'
            self.ttk_style = 'vista'

            # Backgrounds
            self.frame_color = default_color
            self.border_color = default_color
            self.label_color = default_color
            self.notebook_background = default_color

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

        else:
            raise NotImplementedError

    def apply_theme_style(self):
        style = ttk.Style()
        style.theme_create('combostyle', parent=self.ttk_style,
                           settings={'TCombobox':
                                         {'configure':
                                              {'selectbackground': self.combohighlight_color,
                                               # 'selectforeground': 'grey90',
                                               'fieldbackground': self.combofield_color,
                                               'background': self.dropdown_button_color,
                                               }}}
                           )
        style.theme_use('combostyle')
        style.element_create('Plain.Notebook.tab', "from", self.ttk_style)
        style.element_create('Plain.Notebook', "from", self.ttk_style)
        style.layout("TNotebook.Tab",
                          [('Plain.Notebook.tab', {'children':
                                                       [('Notebook.padding', {'side': 'top', 'children':
                                                           [('Notebook.focus', {'side': 'top', 'children':
                                                               [('Notebook.label', {'side': 'top', 'sticky': ''})],
                                                                                'sticky': 'nswe'})],
                                                                              'sticky': 'nswe'})],
                                                   'sticky': 'nswe'})])
        style.configure("TNotebook", background=self.frame_color, tabmargins=[2, 4, 2, 0])
        style.configure("TNotebook.Tab", background=self.frame_color, foreground=self.text_color, lightcolor=self.border_color, padding=[2,1])