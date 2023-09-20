"""
  Copyright (c) 2022 LG Electronics Inc.
  SPDX-License-Identifier: MIT
"""

"""
This module implements the developer interface for webos-emulator.

:class:`WebosEmulator <WebosEmulator> class focuses on the developer interface.
    
"""
from typing import Optional

import webos_emulator
class WebosEmulator:
    """Core developer interface for webos-emulator."""
    
    def __init__(
        self,
        name: str,
        vdname: str
    ):
        """Construct a :class:`WebosEmulator <WebosEmulator>`.
        
        :param str name:
            A webOS emulator name.
        """
        self._name = name
        self._product = "ose"  # TODO
        self._version = "TBD"  # TODO
        self._cpus: Optional[str] = '2'  # number of CPUs
        self._ram: Optional[str] = '4096'  # vd RAM, MBs
        self._vram: Optional[str] = '128'  # vd video RAM, MBs
        self._hostssh: Optional[str] = '6622' # host to emulator ssh port number
        self._image: Optional[str] = None # image name if exists
        self._monitorcount: Optional[str] = '2'  # number of monitors
        self._scalefactor: Optional[str] = '0.7'  # number of scale factor
        self._vmdkfile: Optional[str] = ''  # vmdkfile
        
    @property
    def name(self):
        """Return webOS emulator name"""
        return self._name

    @property
    def product(self):
        """Return webOS emulator product name"""
        return self._product

    @property
    def version(self):
        """Return webOS emulator version name"""
        return self._version

    @property
    def cpus(self):
        """Return webOS emulator number of CPUs """
        return self._cpus
        
    @property
    def ram(self):
        """Return webOS emulator RAM size in MBs"""
        return self._ram
        
    @property
    def vram(self):
        """Return webOS emulator Video RAM size in MBs"""
        return self._vram
        
    @property
    def hostssh(self):
        """Return emulator ssh port number"""
        return self._hostssh
    
    @property
    def image(self):
        """Return image"""
        return self._image

    @property
    def monitorcount(self):
        """Return webOS emulator number of monitors """
        return self._monitorcount

    @property
    def scalefactor(self):
        """Return webOS emulator number of scale factor """
        return self._scalefactor

    @property
    def vmdkfile(self):
        """Return webOS emulator full path of vmdkfile """
        return self._vmdkfile

    @property
    def version(self):
        """Return webOS emulator version """
        return self._version
    
    @image.setter
    def image(self, value):
        """Sets the image"""
        self._image = value

    @ram.setter
    def ram(self, value):
        """Sets the ram"""
        self._ram = value

    @product.setter
    def product(self, value):
        """Sets the product"""
        self._product = value

    @monitorcount.setter
    def monitorcount(self, value):
        """Sets the monitor count"""
        self._monitorcount = value

    @scalefactor.setter
    def scalefactor(self, value):
        """Sets the scale factor"""
        self._scalefactor = value

    @vmdkfile.setter
    def vmdkfile(self, value):
        """Sets the vmdkfile"""
        self._vmdkfile = value

    @version.setter
    def version(self, value):
        """Sets the version"""
        self._version = value

    def create(self):
        """Create a webOS emulator
            
        Default emulator is webOS OSE emulator.
        This method will be removed soon.
            
        """
        pass
        