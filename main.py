import logging


try:
    import win32event
    import win32api
    from winerror import ERROR_ALREADY_EXISTS
    import sys
    import os
    from tkinter import messagebox
    from utils import tk_utils
    from master_frame import MasterFrame

    mutex = win32event.CreateMutex(None, False, 'A957B84C-9800-4BAE-8B56-8F446AB8ED5B')
    last_error = win32api.GetLastError()
    if last_error == ERROR_ALREADY_EXISTS:
        messagebox.showerror('Already open', 'An instance of MF Run Counter is already open - Aborting!')
        logging.exception(f'An instance of MF Run Counter is already open - Aborting! {last_error}')
        sys.exit(0)

    MasterFrame()
except Exception as e:
    logging.exception(e)
    raise e
