import re
import os
import sys


# The exe files do not have a media folder, so only main program should add this to the path
frozen = '' if getattr(sys, 'frozen', False) else 'media\\'
blockpath = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'Blocks.txt')
blocks = [x for x in re.split(r'#(\s+)', open('Blocks.txt', 'r').read()) if x != '\n'] if os.path.isfile('Blocks.txt') else ['']*100
version = '0.11'
release_repo = 'https://github.com/oskros/MF_counter_releases/releases'
exec(blocks[0])