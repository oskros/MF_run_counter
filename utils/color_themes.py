from tkinter import ttk
from utils import tk_dynamic as tkd

available_themes = ['blue', 'dark', 'light']  # , 'default', 'winnative', 'clam', 'alt']
used_base_style = 'clam'


class Theme:
    def __init__(self, used_theme):
        self.used_theme = used_theme
        if self.used_theme == 'blue':
            # General
            default_color = 'LightSkyBlue1'
            self.ttk_style = used_base_style

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
            self.listbox_color_stats = 'alice blue'
            self.pause_button_color = 'DodgerBlue2'
            self.circle_border_color = 'black'
            self.entry_color = 'alice blue'

            # Text
            self.text_color = 'black'
            self.run_count_color = 'red'
            self.hyperlink_color = 'blue'
            self.listbox_text = 'black'
            self.listbox_text_stats = 'black'
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
            self.ttk_style = used_base_style

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
            self.active_checkbox_color = 'gray20'
            # self.listbox_color_stats = 'grey90'
            self.listbox_color = 'grey33'
            self.listbox_color_stats = self.listbox_color
            self.pause_button_color = 'deep sky blue'
            self.circle_border_color = 'grey33'
            self.entry_color = 'grey78'

            # Text
            self.text_color = '#ffffff'
            self.run_count_color = 'dark orange'
            self.hyperlink_color = 'dodger blue'
            # self.listbox_text_stats = 'black'
            self.listbox_text = 'white'
            self.listbox_text_stats = self.listbox_text
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
            self.sb_btn_border_nw = 'white'
            self.sb_bar_background = 'grey70'
            self.sb_bordercolor = 'grey50'
            self.sb_arrowcolor = 'white'
            self.sb_select_btn = 'grey35'

        else:
            # General
            default_color = '#f0f0ed'
            self.ttk_style = used_base_style

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
            self.active_checkbox_color = 'white'
            self.listbox_color = 'white'
            self.listbox_color_stats = 'white'
            self.pause_button_color = 'deep sky blue'
            self.circle_border_color = 'black'
            self.entry_color = 'white'

            # Text
            self.text_color = 'black'
            self.checkbox_text = 'black'
            self.run_count_color = 'red'
            self.hyperlink_color = 'blue'
            self.listbox_text = 'black'
            self.listbox_text_stats = 'black'
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
        style = ttk.Style()
        style_name = 'my_' + self.used_theme
        if style_name not in style.theme_names():
            settings = {'TCombobox': {
                'configure': {'selectbackground': self.combohighlight_color,
                              # 'selectforeground': 'grey90',
                              'fieldbackground': self.combofield_color,
                              'background': self.dropdown_button_color,
                              }
            },
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
                            "expand": [("selected", [2, 1, 2, 0])]}},
                "TScrollbar": {
                    "configure": {
                        "background": self.sb_btn_background,
                        "darkcolor": self.sb_btn_border_se,
                        "lightcolor": self.sb_btn_border_nw,
                        "troughcolor": self.sb_bar_background,
                        "bordercolor": self.sb_bordercolor,
                        "arrowcolor": self.sb_arrowcolor,
                    },
                    "map": {"background": [("active", self.sb_select_btn)]}
                },
            }
            style.theme_create(style_name, parent=self.ttk_style, settings=settings)
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
        tkd.Listbox2.set_config(bg=self.listbox_color_stats, fg=self.listbox_text_stats, highlightbackground=self.border_color)
        tkd.Frame.set_config(bg=self.frame_color)
        tkd.LabelFrame.set_config(bg=self.frame_color)
        tkd.Entry.set_config(bg=self.entry_color)
        # tkd.RestrictedEntry.set_config(bg=self.entry_color)
        tkd.Radiobutton.set_config(bg=self.button_color, selectcolor=self.activebutton_color)
        tkd.Canvas.set_config(bg=self.frame_color)
        tkd.Text.set_config(bg=self.listbox_color, fg=self.listbox_text)
        tkd.ListboxLabel.set_config(bg=self.listbox_color, fg=self.listbox_text)
        tkd.ListboxFrame.set_config(bg=self.listbox_color)
        tkd.Checkbutton.set_config(activebackground=self.label_color, activeforeground=self.text_color, background=self.label_color, foreground=self.text_color, selectcolor=self.active_checkbox_color)
