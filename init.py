import sys
import os
version = '1.4.0'

# The exe files do not have a media folder, so the media folder should only be added to the path when code is run
# directly through Python
media_path = '' if getattr(sys, 'frozen', False) else 'media\\'
release_repo = 'https://github.com/oskros/MF_run_counter/releases'
