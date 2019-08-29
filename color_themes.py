THEME = 'dark'


if THEME == 'test':
    tkk_style = 'clam'
    default_color = '#f0f0ed'
    frame_color = '#40E0D0'
    border_color = '#40E0D0'
    label_color = '#40E0D0'
    button_color = '#40ccd0'
    # activebutton_color = '#40E0D0'
    text_color = '#ffffff'
    run_count_color = 'red'
    hyperlink_color = 'blue'
    listbox_color = 'white'
    listbox_text = 'black'
    pause_button_color = 'deep sky blue'
    pause_button_text = 'black'
    notebook_background = frame_color
    circle_border_color = 'black'
    select_color = 'white'
elif THEME == 'dark':
    ttk_style = 'clam'
    default_color = 'black'
    frame_color = default_color
    border_color = 'dark grey'
    label_color = default_color
    button_color = 'grey40'
    # activebutton_color = '#40E0D0'
    text_color = '#ffffff'
    run_count_color = 'dark orange'
    hyperlink_color = 'dodger blue'
    listbox_color = 'grey33'
    listbox_text = 'white'
    pause_button_color = 'deep sky blue'
    pause_button_text = 'black'
    notebook_background = 'grey10'
    circle_border_color = 'grey33'
    select_color = 'grey78'
else:
    ttk_style = 'vista'
    default_color = '#f0f0ed'
    frame_color = default_color
    border_color = default_color
    label_color = default_color
    button_color = default_color
    # activebutton_color = '#40E0D0'
    text_color = 'black'
    run_count_color = 'red'
    hyperlink_color = 'blue'
    listbox_color = 'white'
    listbox_text = 'black'
    pause_button_color = 'deep sky blue'
    pause_button_text = 'black'
    notebook_background = default_color
    circle_border_color = 'black'
    select_color = 'white'