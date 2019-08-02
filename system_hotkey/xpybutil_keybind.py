"""
A set of functions devoted to binding key presses and registering
callbacks. This will automatically hook into the event callbacks
in event.py.

The two functions of interest here are 'bind_global_key' and 'bind_key'. Most
of the other functions facilitate the use of those two, but you may need them
if you're getting down and dirty.
"""
from collections import defaultdict
import sys

#~ import xcb.xproto as xproto
import xcffib.xproto as xproto

from xpybutil import conn, root, event
from xpybutil.keysymdef import keysyms, keysym_strings

__kbmap = None
__keysmods = None

__keybinds = defaultdict(list)
__keygrabs = defaultdict(int) # Key grab key -> number of grabs

EM = xproto.EventMask
GM = xproto.GrabMode
TRIVIAL_MODS = [
    0,
    xproto.ModMask.Lock,
    xproto.ModMask._2,
    xproto.ModMask.Lock | xproto.ModMask._2
]

def bind_global_key(event_type, key_string, cb):
    """
    An alias for ``bind_key(event_type, ROOT_WINDOW, key_string, cb)``.

    :param event_type: Either 'KeyPress' or 'KeyRelease'.
    :type event_type: str
    :param key_string: A string of the form 'Mod1-Control-a'.
                       Namely, a list of zero or more modifiers separated by
                       '-', followed by a single non-modifier key.
    :type key_string: str
    :param cb: A first class function with no parameters.
    :type cb: function
    :return: True if the binding was successful, False otherwise.
    :rtype: bool
    """
    return bind_key(event_type, root, key_string, cb)

def bind_key(event_type, wid, key_string, cb):
    """
    Binds a function ``cb`` to a particular key press ``key_string`` on a
    window ``wid``. Whether it's a key release or key press binding is
    determined by ``event_type``.

    ``bind_key`` will automatically hook into the ``event`` module's dispatcher,
    so that if you're using ``event.main()`` for your main loop, everything
    will be taken care of for you.

    :param event_type: Either 'KeyPress' or 'KeyRelease'.
    :type event_type: str
    :param wid: The window to bind the key grab to.
    :type wid: int
    :param key_string: A string of the form 'Mod1-Control-a'.
                       Namely, a list of zero or more modifiers separated by
                       '-', followed by a single non-modifier key.
    :type key_string: str
    :param cb: A first class function with no parameters.
    :type cb: function
    :return: True if the binding was successful, False otherwise.
    :rtype: bool
    """
    assert event_type in ('KeyPress', 'KeyRelease')

    mods, kc = parse_keystring(key_string)
    key = (wid, mods, kc)

    if not kc:
        print('Could not find a keycode for %s' % key_string, file=sys.stderr)
        return False

    if not __keygrabs[key] and not grab_key(wid, mods, kc):
        return False

    __keybinds[key].append(cb)
    __keygrabs[key] += 1

    if not event.is_connected(event_type, wid, __run_keybind_callbacks):
        event.connect(event_type, wid, __run_keybind_callbacks)

    return True

def parse_keystring(key_string):
    """
    A utility function to turn strings like 'Mod1-Mod4-a' into a pair
    corresponding to its modifiers and keycode.

    :param key_string: String starting with zero or more modifiers followed
                       by exactly one key press.

                       Available modifiers: Control, Mod1, Mod2, Mod3, Mod4,
                       Mod5, Shift, Lock
    :type key_string: str
    :return: Tuple of modifier mask and keycode
    :rtype: (mask, int)
    """
    modifiers = 0
    keycode = None

    for part in key_string.split('-'):
        if hasattr(xproto.KeyButMask, part):
            modifiers |= getattr(xproto.KeyButMask, part)
        else:
            if len(part) == 1:
                part = part.lower()
            keycode = lookup_string(part)

    return modifiers, keycode

def lookup_string(kstr):
    """
    Finds the keycode associated with a string representation of a keysym.

    :param kstr: English representation of a keysym.
    :return: Keycode, if one exists.
    :rtype: int
    """
    if kstr in keysyms:
        return get_keycode(keysyms[kstr])
    elif len(kstr) > 1 and kstr.capitalize() in keysyms:
        return get_keycode(keysyms[kstr.capitalize()])

    return None

def lookup_keysym(keysym):
    """
    Finds the english string associated with a keysym.

    :param keysym: An X keysym.
    :return: English string representation of a keysym.
    :rtype: str
    """
    return get_keysym_string(keysym)

def get_min_max_keycode():
    """
    Return a tuple of the minimum and maximum keycode allowed in the
    current X environment.

    :rtype: (int, int)
    """
    return conn.get_setup().min_keycode, conn.get_setup().max_keycode

def get_keyboard_mapping():
    """
    Return a keyboard mapping cookie that can be used to fetch the table of
    keysyms in the current X environment.

    :rtype: xcb.xproto.GetKeyboardMappingCookie
    """
    mn, mx = get_min_max_keycode()

    return conn.core.GetKeyboardMapping(mn, mx - mn + 1)

def get_keyboard_mapping_unchecked():
    """
    Return an unchecked keyboard mapping cookie that can be used to fetch the
    table of keysyms in the current X environment.

    :rtype: xcb.xproto.GetKeyboardMappingCookie
    """
    mn, mx = get_min_max_keycode()

    return conn.core.GetKeyboardMappingUnchecked(mn, mx - mn + 1)

def get_keysym(keycode, col=0, kbmap=None):
    """
    Get the keysym associated with a particular keycode in the current X
    environment. Although we get a list of keysyms from X in
    'get_keyboard_mapping', this list is really a table with
    'keysys_per_keycode' columns and ``mx - mn`` rows (where ``mx`` is the
    maximum keycode and ``mn`` is the minimum keycode).

    Thus, the index for a keysym given a keycode is:
    ``(keycode - mn) * keysyms_per_keycode + col``.

    In most cases, setting ``col`` to 0 will work.

    Witness the utter complexity:
    http://tronche.com/gui/x/xlib/input/keyboard-encoding.html

    You may also pass in your own keyboard mapping using the ``kbmap``
    parameter, but xpybutil maintains an up-to-date version of this so you
    shouldn't have to.

    :param keycode: A physical key represented by an integer.
    :type keycode: int
    :param col: The column in the keysym table to use.
                Unless you know what you're doing, just use 0.
    :type col: int
    :param kbmap: The keyboard mapping to use.
    :type kbmap: xcb.xproto.GetKeyboardMapingReply
    """
    if kbmap is None:
        kbmap = __kbmap

    mn, mx = get_min_max_keycode()
    per = kbmap.keysyms_per_keycode
    ind = (keycode - mn) * per + col

    return kbmap.keysyms[ind]

def get_keysym_string(keysym):
    """
    A simple wrapper to find the english string associated with a particular
    keysym.

    :param keysym: An X keysym.
    :rtype: str
    """
    return keysym_strings.get(keysym, [None])[0]

def get_keycode(keysym):
    """
    Given a keysym, find the keycode mapped to it in the current X environment.
    It is necessary to search the keysym table in order to do this, including
    all columns.

    :param keysym: An X keysym.
    :return: A keycode or None if one could not be found.
    :rtype: int
    """
    mn, mx = get_min_max_keycode()
    cols = __kbmap.keysyms_per_keycode
    for i in range(mn, mx + 1):
        for j in range(0, cols):
            ks = get_keysym(i, col=j)
            if ks == keysym:
                return i

    return None

def get_mod_for_key(keycode):
    """
    Finds the modifier that is mapped to the given keycode.
    This may be useful when analyzing key press events.

    :type keycode: int
    :return: A modifier identifier.
    :rtype: xcb.xproto.ModMask
    """
    return __keysmods.get(keycode, 0)

def get_keys_to_mods():
    """
    Fetches and creates the keycode -> modifier mask mapping. Typically, you
    shouldn't have to use this---xpybutil will keep this up to date if it
    changes.

    This function may be useful in that it should closely replicate the output
    of the ``xmodmap`` command. For example:

     ::

        keymods = get_keys_to_mods()
        for kc in sorted(keymods, key=lambda kc: keymods[kc]):
            print keymods[kc], hex(kc), get_keysym_string(get_keysym(kc))

    Which will very closely replicate ``xmodmap``. I'm not getting precise
    results quite yet, but I do believe I'm getting at least most of what
    matters. (i.e., ``xmodmap`` returns valid keysym strings for some that
    I cannot.)

    :return: A dict mapping from keycode to modifier mask.
    :rtype: dict
    """
    mm = xproto.ModMask
    modmasks = [mm.Shift, mm.Lock, mm.Control,
                mm._1, mm._2, mm._3, mm._4, mm._5] # order matters

    mods = conn.core.GetModifierMapping().reply()

    res = {}
    keyspermod = mods.keycodes_per_modifier
    for mmi in range(0, len(modmasks)):
        row = mmi * keyspermod
        for kc in mods.keycodes[row:row + keyspermod]:
            res[kc] = modmasks[mmi]

    return res

def get_modifiers(state):
    """
    Takes a ``state`` (typically found in key press or button press events)
    and returns a string list representation of the modifiers that were pressed
    when generating the event.

    :param state: Typically from ``some_event.state``.
    :return: List of modifier string representations.
    :rtype: [str]
    """
    ret = []

    if state & xproto.ModMask.Shift:
        ret.append('Shift')
    if state & xproto.ModMask.Lock:
        ret.append('Lock')
    if state & xproto.ModMask.Control:
        ret.append('Control')
    if state & xproto.ModMask._1:
        ret.append('Mod1')
    if state & xproto.ModMask._2:
        ret.append('Mod2')
    if state & xproto.ModMask._3:
        ret.append('Mod3')
    if state & xproto.ModMask._4:
        ret.append('Mod4')
    if state & xproto.ModMask._5:
        ret.append('Mod5')
    if state & xproto.KeyButMask.Button1:
        ret.append('Button1')
    if state & xproto.KeyButMask.Button2:
        ret.append('Button2')
    if state & xproto.KeyButMask.Button3:
        ret.append('Button3')
    if state & xproto.KeyButMask.Button4:
        ret.append('Button4')
    if state & xproto.KeyButMask.Button5:
        ret.append('Button5')

    return ret

def grab_keyboard(grab_win):
    """
    This will grab the keyboard. The effect is that further keyboard events
    will *only* be sent to the grabbing client. (i.e., ``grab_win``).

    N.B. There is an example usage of this in examples/window-marker.

    :param grab_win: A window identifier to report keyboard events to.
    :type grab_win: int
    :rtype: xcb.xproto.GrabStatus
    """
    return conn.core.GrabKeyboard(False, grab_win, xproto.Time.CurrentTime,
                                  GM.Async, GM.Async).reply()

def ungrab_keyboard():
    """
    This will release a grab initiated by ``grab_keyboard``.

    :rtype: void
    """
    conn.core.UngrabKeyboardChecked(xproto.Time.CurrentTime).check()

def grab_key(wid, modifiers, key):
    """
    Grabs a key for a particular window and a modifiers/key value.
    If the grab was successful, return True. Otherwise, return False.
    If your client is grabbing keys, it is useful to notify the user if a
    key wasn't grabbed. Keyboard shortcuts not responding is disorienting!

    Also, this function will grab several keys based on varying modifiers.
    Namely, this accounts for all of the "trivial" modifiers that may have
    an effect on X events, but probably shouldn't effect key grabbing. (i.e.,
    whether num lock or caps lock is on.)

    N.B. You should probably be using 'bind_key' or 'bind_global_key' instead.

    :param wid: A window identifier.
    :type wid: int
    :param modifiers: A modifier mask.
    :type modifiers: int
    :param key: A keycode.
    :type key: int
    :rtype: bool
    """
    try:
        for mod in TRIVIAL_MODS:
            conn.core.GrabKeyChecked(True, wid, modifiers | mod, key, GM.Async,
                                     GM.Async).check()

        return True
    except xproto.BadAccess:
        return False

def ungrab_key(wid, modifiers, key):
    """
    Ungrabs a key that was grabbed by ``grab_key``. Similarly, it will return
    True on success and False on failure.

    When ungrabbing a key, the parameters to this function should be
    *precisely* the same as the parameters to ``grab_key``.

    :param wid: A window identifier.
    :type wid: int
    :param modifiers: A modifier mask.
    :type modifiers: int
    :param key: A keycode.
    :type key: int
    :rtype: bool
    """
    try:
        for mod in TRIVIAL_MODS:
            conn.core.UngrabKeyChecked(key, wid, modifiers | mod).check()
        return True
    except xproto.BadAccess:
        return False

def update_keyboard_mapping(e):
    """
    Whenever the keyboard mapping is changed, this function needs to be called
    to update xpybutil's internal representing of the current keysym table.
    Indeed, xpybutil will do this for you automatically.

    Moreover, if something is changed that affects the current keygrabs,
    xpybutil will initiate a regrab with the changed keycode.

    :param e: The MappingNotify event.
    :type e: xcb.xproto.MappingNotifyEvent
    :rtype: void
    """
    global __kbmap, __keysmods

    newmap = get_keyboard_mapping().reply()

    if e is None:
        __kbmap = newmap
        __keysmods = get_keys_to_mods()
        return

    if e.request == xproto.Mapping.Keyboard:
        changes = {}
        for kc in range(*get_min_max_keycode()):
            knew = get_keysym(kc, kbmap=newmap)
            oldkc = get_keycode(knew)
            if oldkc != kc:
                changes[oldkc] = kc

        __kbmap = newmap
        __regrab(changes)
    elif e.request == xproto.Mapping.Modifier:
        __keysmods = get_keys_to_mods()

def __run_keybind_callbacks(e):
    """
    A private function that intercepts all key press/release events, and runs
    their corresponding callback functions. Nothing much to see here, except
    that we must mask out the trivial modifiers from the state in order to
    find the right callback.

    Callbacks are called in the order that they have been added. (FIFO.)

    :param e: A Key{Press,Release} event.
    :type e: xcb.xproto.Key{Press,Release}Event
    :rtype: void
    """
    kc, mods = e.detail, e.state
    for mod in TRIVIAL_MODS:
        mods &= ~mod

    key = (e.event, mods, kc)
    for cb in __keybinds.get(key, []):
        try:
            cb(e)
        except TypeError:
            cb()

def __regrab(changes):
    """
    Takes a dictionary of changes (mapping old keycode to new keycode) and
    regrabs any keys that have been changed with the updated keycode.

    :param changes: Mapping of changes from old keycode to new keycode.
    :type changes: dict
    :rtype: void
    """
    for wid, mods, kc in __keybinds:
        if kc in changes:
            ungrab_key(wid, mods, kc)
            grab_key(wid, mods, changes[kc])

            old = (wid, mods, kc)
            new = (wid, mods, changes[kc])
            __keybinds[new] = __keybinds[old]
            del __keybinds[old]

if conn is not None:
    update_keyboard_mapping(None)
    event.connect('MappingNotify', None, update_keyboard_mapping)

if __name__ == '__main__':
    import xpybutil.event as event
    print(get_keysym_string(get_keysym(71)))
    #~ print(parse_keystring('f5'))
    #~ bind_global_key('KeyPress', 'F5', lambda: print('ass'))
    #~ event.main()

