import importlib
import typing as T
from pathlib import Path

from libs.screeninfo import enumerators
from libs.screeninfo.common import Enumerator, Monitor, ScreenInfoError

ENUMERATOR_MAP = {
    Enumerator.Windows: enumerators.windows,
    Enumerator.Cygwin: enumerators.cygwin,
    Enumerator.Xrandr: enumerators.xrandr,
    Enumerator.Xinerama: enumerators.xinerama,
    Enumerator.DRM: enumerators.drm,
    Enumerator.OSX: enumerators.osx,
}


def _get_monitors(enumerator: Enumerator, disable_scaling: bool) -> T.List[Monitor]:
    return list(ENUMERATOR_MAP[enumerator].enumerate_monitors(disable_scaling=disable_scaling))


def get_monitors(
    disable_scaling: bool = True,
    name: T.Union[Enumerator, str, None] = None
) -> T.List[Monitor]:
    """Returns a list of :class:`Monitor` objects based on active monitors."""
    enumerator = Enumerator(name) if name is not None else None

    if enumerator is not None:
        return _get_monitors(enumerator, disable_scaling=disable_scaling)

    for enumerator in Enumerator:
        try:
            return _get_monitors(enumerator, disable_scaling=disable_scaling)
        except Exception:
            pass

    raise ScreenInfoError("No enumerators available")
