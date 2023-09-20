"""
  Copyright (c) 2022-2023 LG Electronics Inc.
  SPDX-License-Identifier: MIT
"""

import logging
import subprocess
from subprocess import DEVNULL   # TODO: check Python 3.3 above
import re
import locale

# TODO: set logging level
STDIN = DEVNULL  # quiet, None for info level
hostos_encoding = locale.getpreferredencoding()

def get_stderr():
    """get stderr log level by int
    """
    if logging.root.level == logging.DEBUG:
        return None
    else:
        return DEVNULL

def get_vboxmanage(command):
    """Get the full path of vboxmanage"""
    try:
        sp = subprocess.Popen([command, '-version'], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        version, error = sp.communicate()
    except:
        return None, None
    else:
        return command, version

VBOXM, VBOXVER = get_vboxmanage("VBoxManage")
if VBOXVER:
    VBOXVER = str(VBOXVER, hostos_encoding).split('\n')[0]

def is_vd_exists(name):
    """Check the given vd is exists

    Args:
        name (string): target name of vd
    """
    vdcmd = VBOXM
    command = [vdcmd] + ['list', 'vms']

    try:
        sp = subprocess.Popen(command, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, error = sp.communicate()
    except:
        return False
    result = str(result, hostos_encoding).split('\n')
    pattern = "^\"" + name + "\""
    for i in result:
        if re.search(pattern, i):
            return True
    return False

def check_linux_guest(name):
    """Check the given vm is Linux guest

    Args:
        name (string): target name
    """
    vdcmd = VBOXM
    command = [vdcmd] + ['showvminfo', name]

    try:
        sp = subprocess.Popen(command, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, error = sp.communicate()
    except:
        return False
    result = str(result, hostos_encoding).split('\n')
    for i in result:
        if i == "":
            break
        n = i.split(":")
        if n[0]=="Guest OS":
            n1 = n[1].strip()
            if n1 == "Other Linux (64-bit)" or n1 == "Other Linux (32-bit)":
                return True
    return False

def validate_vd_name(name, listing):
    """Validate the given vd name

    Args:
        name (string): target name of vd
        listing (boolean): list option
    """
    vdcmd = VBOXM
    command = [vdcmd] + ['list', 'vms']

    try:
        sp = subprocess.Popen(command, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, error = sp.communicate()
        command = [vdcmd] + ['list', 'runningvms']
        sp = subprocess.Popen(command, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result2, error2 = sp.communicate()
    except:
        print("webos-emulator : Please install virtualbox and set the PATH variable in the system envrionment.")
        print("On Windows, please refer to https://www.webosose.org/docs/tools/sdk/emulator/virtualbox-emulator/emulator-user-guide/#setting-the-path-on-windows")
        return ("__VBOX_NOT_INSTALLED__", "", "")
    dl = []
    product = "ose"
    rname = ""
    ruuid = ""
    version = ""
    result = str(result, hostos_encoding).split('\n')
    running_vm = ""
    if result2:
        result2 = str(result2, hostos_encoding).split('\n')
        running_vm = result2[0].split("\" ")[0][1:]

    for i in result:
        if i == "":
            break
        vm = n = i.split("\" ")
        n = vm[0][1:]
        m = vm[1].strip()[1:-1]

        if check_linux_guest(n):
            dl.append((n, m))
    if listing:
        for i,j in dl:
            if i == running_vm:
                i = i + " (running)"
            print(i)
        return ("","","")
    else:
        for i,j in dl:
            if i == name or j == name:
                rname = i
                ruuid = j
                if rname.startswith("LG webOS TV Emulator"):
                    product = "tv"
                    version = rname.split("LG webOS TV Emulator ")[1]
                elif rname.startswith("LG webOS SIGNAGE Emulator"):
                    product = "signage"
                    version = rname.split("LG webOS SIGNAGE Emulator ")[1]
    return (rname, ruuid, product, version)

def is_vd_running(name):
    """Check the given vd is running

    Args:
        name (string): target name of vd
    """
    vdcmd = VBOXM
    command = [vdcmd] + ['list', 'runningvms']

    try:
        sp = subprocess.Popen(command, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, error = sp.communicate()
    except:
        print("webos-emulator : is_vd_running subprocess.Popen error")
        return False
    if error:
       print("webos-emulator : Popen error %s" % error)
       return False
    result = str(result, hostos_encoding).split('\n')
    pattern = "^\"" + name + "\""
    for i in result:
        if re.search(pattern, i):
            return True
    return False

def get_storage_name(name):
    """Check the given vd's stroage controller name

    Args:
        name (string): target name of vd
    """
    vdcmd = VBOXM
    command = [vdcmd] + ['showvminfo', name]

    try:
        sp = subprocess.Popen(command, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, error = sp.communicate()
    except:
        print("webos-emulator : get_storage_name subprocess.Popen error")
        return ""
    if error:
       print("webos-emulator : Popen error %s" % error)
       return ""
    result = str(result, hostos_encoding).split('\n')
    for i in result:
        if i.startswith("Storage Controller Name (0):"):
            found = i.split("Storage Controller Name (0):")
            return found[1].strip()
        if i.startswith("#0:"):
            found = i.split(",")[0].split()[1]
            return found.strip()[1:-1]
    return ""

def is_safe_to_create(name): # TODO: need to rename the method name
    """Check if the emulator is running
    
    :param name:
        the name of emulator
    """
    logging.info("is_safe_to_create : %s" % name)
    if VBOXM == None:
        print("webos-emulator : Please install virtualbox.")
        return False

    if is_vd_exists(name) and is_vd_running(name):
        return False
    else:
        return True

def detach_image(name):
    """Detach image from the given vd

    Args:
        name (string): target name of vd
    """
    vdcmd = VBOXM
    command = [vdcmd] + ["storageattach", name, "--storagectl", name,
                         "--type", "hdd", "--medium", "emptydrive",
                         "--port", "0", "--device", "0"]

    if subprocess.call(command, stdin=STDIN, stderr=get_stderr()) != 0:
        logging.debug("detach error")
        # TODO: check if storage is attached or not using grep '(UUID: ' in showvminfo
        # return False
    return True
