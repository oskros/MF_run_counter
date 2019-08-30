class Theme:
    def __init__(self, used_theme):
        if used_theme == 'test':
            self.tkk_style = 'clam'
            self.default_color = '#f0f0ed'
            self.frame_color = '#40E0D0'
            self.border_color = '#40E0D0'
            self.label_color = '#40E0D0'
            self.button_color = '#40ccd0'
            # self.activebutton_color = '#40E0D0'
            self.text_color = '#ffffff'
            self.run_count_color = 'red'
            self.hyperlink_color = 'blue'
            self.listbox_color = 'white'
            self.listbox_text = 'black'
            self.pause_button_color = 'deep sky blue'
            self.pause_button_text = 'black'
            self.notebook_background = self.frame_color
            self.circle_border_color = 'black'
            self.select_color = 'white'
        elif used_theme == 'dark':
            self.ttk_style = 'clam'
            self.default_color = 'black'
            self.frame_color = self.default_color
            self.border_color = 'dark grey'
            self.label_color = self.default_color
            self.button_color = 'grey40'
            # self.activebutton_color = '#40E0D0'
            self.text_color = '#ffffff'
            self.run_count_color = 'dark orange'
            self.hyperlink_color = 'dodger blue'
            self.listbox_color = 'grey33'
            self.listbox_text = 'white'
            self.pause_button_color = 'deep sky blue'
            self.pause_button_text = 'black'
            self.notebook_background = 'grey10'
            self.circle_border_color = 'grey33'
            self.select_color = 'grey78'
        else:
            self.ttk_style = 'vista'
            self.default_color = '#f0f0ed'
            self.frame_color = self.default_color
            self.border_color = self.default_color
            self.label_color = self.default_color
            self.button_color = self.default_color
            # self.activebutton_color = '#40E0D0'
            self.text_color = 'black'
            self.run_count_color = 'red'
            self.hyperlink_color = 'blue'
            self.listbox_color = 'white'
            self.listbox_text = 'black'
            self.pause_button_color = 'deep sky blue'
            self.pause_button_text = 'black'
            self.notebook_background = self.default_color
            self.circle_border_color = 'black'
            self.select_color = 'white'