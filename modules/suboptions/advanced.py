from modules.suboptions.general import General
from utils import tk_dynamic as tkd


class Advanced(General):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.add_flag(flag_name='PD2 mode', comment='Enable PD2 mode to use item_library_pd2 instead of item_library. Requires app restart to take effect.')
        self.add_flag(flag_name='Auto upload herokuapp', comment='Automatically upload newly found grailers to d2-holy-grail.herokuapp.com')
        self.add_flag(flag_name='Autocompletion unids', comment='Enable autocompletion for unid set/uniques, for tc84/87 items and for circlets, charms and jewels')
        self.add_num_entry(flag_name='Start run delay (seconds)', comment='Add an artificial delay to the "start run" command')
        self.add_num_entry(flag_name='Auto archive (hours)', comment='Automatically calls "Archive session" if more than configured number of hours have passed since last time the profile was used\n\nDisabled when equal to zero (0.0)\n\nThis is checked when app is opened and when profile is changed')
