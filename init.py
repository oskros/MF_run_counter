import re
import os
import sys


default_color = '#f0f0ed'
background_color = '#40E0D0'
button_color = '#40ccd0'
activebutton_color = '#40E0D0'

# The exe files do not have a media folder, so the media folder should only be added to the path when code is run
# directly through Python
media_path = '' if getattr(sys, 'frozen', False) else 'media\\'
blockpath = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'Blocks.txt')
blocks = [x for x in re.split(r'#(\s+)', open('Blocks.txt', 'r').read()) if x != '\n'] if os.path.isfile('Blocks.txt') else ['']*100
version = '0.11'
release_repo = 'https://github.com/oskros/MF_counter_releases/releases'
exec(blocks[0])