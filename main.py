try:
    import win32gui
    import logging
    import sys
    from utils import tk_utils
    from main_frame import MainFrame

    if win32gui.FindWindow(None, 'MF run counter'):
        resp = tk_utils.mbox(msg='It seems like you already have an instance of MF run counter open.\n'
                                 'Opening another instance will make the app unstable (If this is a false positive, just ignore it)\n\n'
                                 'Do you wish to continue anyway?', title='WARNING')
        if not resp:
            sys.exit(0)

    MainFrame()
except Exception as e:
    logging.exception(e)
    raise e
