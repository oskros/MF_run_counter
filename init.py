import re
import os
import sys
version = '0.13.0'

# The exe files do not have a media folder, so the media folder should only be added to the path when code is run
# directly through Python
media_path = '' if getattr(sys, 'frozen', False) else 'media\\'
# blockpath = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'Automode.txt')
# blocks = [x for x in re.split(r'#(\s+)', open('Automode.txt', 'r').read()) if x != '\n'] if os.path.isfile('Automode.txt') else ['']*100
# exec(blocks[0])
# AUTOMODE = os.path.isfile('Automode.txt')
release_repo = 'https://github.com/oskros/MF_counter_releases/releases'
# AUTOMODE = False
