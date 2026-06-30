import os

import ns_shared


def turbojpeg_check():
    if not os.path.isfile(ns_shared.TURBOJPEG_PATH):
        raise NoTurboJPEG


class NoTurboJPEG(Exception):
    """The TurboJPEG DLL was not found at the location specified in ns_shared/config.py.
    Please download the latest gcc x64 binary from SourceForge/Github and run the installer.
    The installer should fix everything. Please.
    If the TurboJPEG DLL has been shifted, please amend the magic string in ns_shared/config.py.TURBOJPEG_PATH.
    Thank you, and I hope this does not pop up on competition day.
    """
