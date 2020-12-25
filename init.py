import sys
import os
version = '1.4.6'

# The exe files do not have a media folder, so the media folder should only be added to the path when code is run
# directly through Python
media_folder = '' if getattr(sys, 'frozen', False) else 'media\\'
media_path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), media_folder)
release_repo = 'https://github.com/oskros/MF_run_counter/releases'
