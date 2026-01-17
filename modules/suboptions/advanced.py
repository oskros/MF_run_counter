from modules.suboptions.general import General
from utils import tk_dynamic as tkd


class Advanced(General):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.add_flag(flag_name='PD2 mode', comment='Enable PD2 mode to access PD2-specific items and settings from item_library.')
        self.add_flag(flag_name='Auto upload herokuapp', comment='Automatically upload newly found grailers to d2-holy-grail.herokuapp.com')
        self.add_flag(flag_name='Unid item mode', comment='Toggle autocompletion in the drop window for unidentified set/unique items, and some selected magic and rare items.')
        self.add_flag(flag_name='Disable DPI scaling', comment='Disable Windows DPI scaling for the application. Requires a restart of the app to take effect.\n\nNote that the app is not guaranteed to behave well if DPI scaling is enabled.')
        self.add_num_entry(flag_name='Start run delay (seconds)', comment='Add an artificial delay to the "start run" command')
        self.add_num_entry(flag_name='Auto archive (hours)', comment='Automatically calls "Archive session" if more than the configured number of hours have passed since last time the profile was used\n\nDisabled when equal to zero (0.0)\n\nThis is checked when app is opened and when profile is changed')

    def toggle_button(self, attr):
        # Call parent implementation first
        super().toggle_button(attr)
        
        # Refresh grail tab summary when PD2 mode changes
        if attr == 'pd2_mode' and hasattr(self.main_frame, 'grail_tab'):
            self.main_frame.grail_tab.update_statistics()
