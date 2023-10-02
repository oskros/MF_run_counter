try:
    import win32event
    import win32api
    from winerror import ERROR_ALREADY_EXISTS
    import logging
    import sys
    import os
    from utils import tk_utils
    from master_frame import MasterFrame

    mp = os.path.abspath(__file__).replace('\\', '/') + "_{MF RUN COUNTER}"
    mutex = win32event.CreateMutex(None, False, mp)
    last_error = win32api.GetLastError()
    if last_error == ERROR_ALREADY_EXISTS:
        logging.exception(f'Application is already open. Aborting. {last_error}')
        sys.exit(0)

    MasterFrame()
except Exception as e:
    logging.exception(e)
    raise e
