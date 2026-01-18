import sys
import os
version = '1.6.0'

# The exe files do not have an assets folder, so the assets folder should only be added to the path when code is run
# directly through Python
assets_folder = '' if getattr(sys, 'frozen', False) else 'assets\\'
assets_path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), assets_folder)
release_repo = 'https://github.com/oskros/MF_run_counter/releases'
