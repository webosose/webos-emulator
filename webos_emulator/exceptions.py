"""
  Copyright (c) 2022 LG Electronics Inc.
  SPDX-License-Identifier: MIT
"""
class webos_emulatorError(Exception):
    """Base webos-emulator exception that others inherit.

    """
    
class VdError(webos_emulatorError):
    """vd related exception

    """
    
class DetachError(VdError):
    """vd detach error exception

    """
    def __init__(self, vdname:str):
        """Detach Error

        Args:
            vdname (str): vd name of exception occurred
        """
        super().__init__(f"[{vdname}] could not detach image")
        self.vdname = vdname
