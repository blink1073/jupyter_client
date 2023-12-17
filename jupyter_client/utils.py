"""
utils:
- provides utility wrappers to run asynchronous functions in a blocking environment.
- vendor functions from ipython_genutils that should be retired at some point.
"""
from __future__ import annotations

import asyncio
import os
import sys
import warnings
from typing import Callable, Sequence

from jupyter_core.utils import ensure_async, run_sync  # noqa: F401  # noqa: F401

from .session import utcnow  # noqa


def _filefind(filename: str, path_dirs: str | Sequence[str] | None = None) -> str:
    """Find a file by looking through a sequence of paths.

    This iterates through a sequence of paths looking for a file and returns
    the full, absolute path of the first occurrence of the file.  If no set of
    path dirs is given, the filename is tested as is, after running through
    :func:`expandvars` and :func:`expanduser`.  Thus a simple call::

        filefind('myfile.txt')

    will find the file in the current working dir, but::

        filefind('~/myfile.txt')

    Will find the file in the users home directory.  This function does not
    automatically try any paths, such as the cwd or the user's home directory.

    Parameters
    ----------
    filename : str
        The filename to look for.
    path_dirs : str, None or sequence of str
        The sequence of paths to look for the file in.  If None, the filename
        need to be absolute or be in the cwd.  If a string, the string is
        put into a sequence and the searched.  If a sequence, walk through
        each element and join with ``filename``, calling :func:`expandvars`
        and :func:`expanduser` before testing for existence.

    Returns
    -------
    Raises :exc:`IOError` or returns absolute path to file.
    """

    # If paths are quoted, abspath gets confused, strip them...
    filename = filename.strip('"').strip("'")
    # If the input is an absolute path, just check it exists
    if os.path.isabs(filename) and os.path.isfile(filename):
        return filename

    if path_dirs is None:
        path_dirs = ("",)
    elif isinstance(path_dirs, str):
        path_dirs = (path_dirs,)

    for path in path_dirs:
        if path == ".":
            path = os.getcwd()  # noqa
        testname = _expand_path(os.path.join(path, filename))
        if os.path.isfile(testname):
            return os.path.abspath(testname)
    msg = f"File {filename!r} does not exist in any of the search paths: {path_dirs!r}"
    raise OSError(msg)


def _expand_path(s: str) -> str:
    """Expand $VARS and ~names in a string, like a shell

    :Examples:

       In [2]: os.environ['FOO']='test'

       In [3]: expand_path('variable FOO is $FOO')
       Out[3]: 'variable FOO is test'
    """
    # This is a pretty subtle hack. When expand user is given a UNC path
    # on Windows (\\server\share$\%username%), os.path.expandvars, removes
    # the $ to get (\\server\share\%username%). I think it considered $
    # alone an empty var. But, we need the $ to remains there (it indicates
    # a hidden share).
    if os.name == "nt":
        s = s.replace("$\\", "IPYTHON_TEMP")
    s = os.path.expandvars(os.path.expanduser(s))
    if os.name == "nt":
        s = s.replace("IPYTHON_TEMP", "$\\")
    return s


def get_event_loop() -> asyncio.AbstractEventLoop:
    # Get the loop for this thread.
    # In Python 3.12, a deprecation warning is raised, which
    # may later turn into a RuntimeError.  We handle both
    # cases.
    # TODO: migrate to jupyter_core
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            if sys.platform == "win32":
                loop = asyncio.WindowsSelectorEventLoopPolicy().new_event_loop()
            else:
                loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    return loop


def run_in_event_loop(fn: Callable) -> None:
    """Run the given function after invoking asyncio.run"""

    async def inner():
        fn()

    def cb():
        if sys.version_info >= (3, 12) and sys.platform == "win32":
            loop_factory = asyncio.WindowsSelectorEventLoopPolicy()
            asyncio.run(inner(), loop_factory=loop_factory)
            return
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(inner())

    return cb
