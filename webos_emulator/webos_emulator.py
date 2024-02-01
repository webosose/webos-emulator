"""
  Copyright (c) 2022-2023 LG Electronics Inc.
  SPDX-License-Identifier: MIT
"""

"""Main module."""

# TODO: make webos-emulator class

import logging
import subprocess
import os, platform
import json
from subprocess import DEVNULL
from sys import stderr # TODO: check Python 3.3 above
from webos_emulator import WebosEmulator
from webos_emulator.exceptions import DetachError
import locale

# TODO: set logging level
STDIN = DEVNULL  # quiet, None for info level
hostos_encoding = locale.getpreferredencoding()

from webos_emulator.check import detach_image, get_stderr, get_storage_name, get_vboxmanage, is_safe_to_create, is_vd_exists, is_vd_running
from webos_emulator.check import VBOXM

here = os.path.abspath(os.path.dirname(__file__))
VD_JSON = json.loads(open(os.path.join(here, "webos-emulator.json"), encoding=hostos_encoding).read())

def detach_storage(name):
    """detach the image from the vd

    Args:
        name (str): vd name
    """
    logging.info("detach_storage : %s" % name)
    vdcmd = VBOXM
    command = [vdcmd] + ['storageattach', name, '--storagectl', name, '--type',
                         'hdd', '--medium', 'emptydrive', '--port', '0', '--device', '0']
    if subprocess.call(command, stdin=STDIN, stderr=get_stderr()) == 0:
        return True
    else:
        return False

def attach_storage(vdcmd, name, vdimage):
    """attach the image to the vd

    Args:
        vdcmd (str): virtualizer command
        name (str): vd name
    """
    try:
        storage_name = get_storage_name(name)
        if storage_name == "":
            storage_name = name
        command = [vdcmd] + ['storageattach', name, '--storagectl', storage_name, '--type',
                             'hdd', '--port', '0', '--device', '0', '--medium', vdimage]
        subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL, stderr=get_stderr())
    except subprocess.CalledProcessError as e:
        print("webos-emulator : attach_stroage error")
        logging.debug("attach_storage error : %s" % e)
        return False
    return True

def remove_vd(name):
    """remove vd

    Args:
        name (str): vd name
    """
    logging.info("remove_vd : %s" % name)
    if VBOXM == None:
        print("webos-emulator : Please install virtualbox.")
        return False
    
    if is_vd_exists(name):
        detach_storage(name)
        command = [VBOXM] + ['unregistervm', name, '--delete']
        if subprocess.call(command, stdin=STDIN, stderr=get_stderr()) == 0:
            return True
        else:
            raise DetachError(vdname=name)
    return False

def modify_vd(vd: WebosEmulator, mstr, newname, vmdk):
    """modify vd settings

    Without extra options, it shows current settings

    Args:
        vd (WebosEmulator): vd object
        mstr : modifications settings list
        newname : new name of vm
        vmdk : vmdk file
    """
    if is_vd_running(vd.name):
        print("webos-emulator : vd is running. please stop vd before modify")
        return False
    storage_name = get_storage_name(vd.name)
    storage = storage_name + " (0, 0)"
    settings = ["Memory size", "Monitor count", "Number of CPUs", "VRAM size", "Name", "Guest OS", storage]

    tname = vd.name
    if newname:
        tname = newname

    if mstr == "" and vmdk == "":
        print("-m options:")
        print("  --memory <memory size in MB>")
        print("  --vram <video memory size in MB>")
        print("  --cpus <number>")
        print("  --monitorcount <number>")
        print("  --name <name>")
        print("  --ostype <Linux or Linux_64>")
        print("  --vmdk <vmdk file>")
        print()
    else:
        try:
            if mstr:
                command = [VBOXM] + ['modifyvm', vd.name] + mstr.split(":")[:-1]
                subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL, stderr=get_stderr())
            if vmdk != "":
                command = [VBOXM] + ['storageattach', tname, '--storagectl', storage_name, '--type',
                        'hdd', '--port', '0', '--device', '0', '--medium', vmdk]
                subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL, stderr=get_stderr())
        except subprocess.CalledProcessError as e:
            print("webos-emulator : modify_vd, set subprocess.Popen error")
            logging.debug("modify error : %s" % e)
            return False
    command = [VBOXM] + ['showvminfo', tname]
    try:
        sp = subprocess.Popen(command, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        vdinfo, error = sp.communicate()
    except:
        print("webos-emulator : modify_vd, get subprocess.Popen error")
        return False
    if error:
       print("webos-emulator : Popen error %s" % error)
       return False
    vdinfo = str(vdinfo, hostos_encoding).split('\n')

    print("following is the current settings of vd")
    for i in vdinfo:
        if i.split(":")[0] in settings:
            print(i)
    return True

def create_vd(vd: WebosEmulator):
    """create a vd
    
    Temporal method for create vd.
    webos-emulator class will be made sooner.

    Args:
        vd (WebosEmulator): vd object
    """
    name = vd.name
    if is_safe_to_create(name):
        logging.info("%s is safe to create." % name)
        try:
            remove_vd(name)
        except DetachError as e:
            logging.error("webos-emulator error : %s" % e)
            return False
    else:
        # TODO: error handling
        return False
    
    # TODO: error handling
    try:
        logging.info("creating vd....")
        command = [VBOXM] + ['createvm', '--ostype', 'Linux_64', '--register', '--name', name]
        subprocess.check_call(command, stdin=STDIN)
        command = [VBOXM] + ['storagectl', name, '--add', 'ide', '--name', name]
        subprocess.check_call(command, stdin=STDIN)
        command = [VBOXM] + ['modifyvm', name, '--boot1', 'disk', '--boot2', 'none', '--boot3', 'none', '--boot4', 'none']
        subprocess.check_call(command, stdin=STDIN)
        
        # setting memory, videoram and cpu
        command = [VBOXM] + ['modifyvm', name, '--memory', vd.ram, '--vram', vd.vram, '--ioapic', 'on', '--cpus', vd.cpus]
        subprocess.check_call(command, stdin=STDIN)
        
        # setting graphics stuffs
        command = [VBOXM] + ['modifyvm', name, '--graphicscontroller', 'vmsvga']
        subprocess.check_call(command, stdin=STDIN)
        command = [VBOXM] + ['modifyvm', name, '--accelerate3d', 'on']
        subprocess.check_call(command, stdin=STDIN)
        
        # set usb tablet and sound
        if platform.system() == 'Windows':
            command = [VBOXM] + ['modifyvm', name, '--mouse', 'usbtablet', '--audio', 'dsound', '--audioout', 'on', '--audioin', 'on']
        elif platform.system() == 'Darwin':
            command = [VBOXM] + ['modifyvm', name, '--mouse', 'usbtablet', '--audio', 'coreaudio', '--audioout', 'on', '--audioin', 'on']
        else:
            command = [VBOXM] + ['modifyvm', name, '--mouse', 'usbtablet', '--audio', 'pulse', '--audioout', 'on', '--audioin', 'on']
        subprocess.check_call(command, stdin=STDIN)
        
        # setting network
        command = [VBOXM] + ['modifyvm', name, '--nic1', 'nat', '--natpf1', 'ssh,tcp,,'+ vd.hostssh  +',,22']
        subprocess.check_call(command, stdin=STDIN)
        command = [VBOXM] + ['modifyvm', name, '--natpf1', 'web-inspector,tcp,,9998,,9998']
        subprocess.check_call(command, stdin=STDIN)
        command = [VBOXM] + ['modifyvm', name, '--natpf1', 'enact-browser-web-inspector,tcp,,9223,,9999']
        subprocess.check_call(command, stdin=STDIN)
        
        # serial to null
        if platform.system() == 'Windows':
            command = [VBOXM] + ['modifyvm', name, '--uart1', '0x3f8', '4', '--uartmode1', 'file', 'null']
        else:
            command = [VBOXM] + ['modifyvm', name, '--uart1', '0x3f8', '4', '--uartmode1', 'file', '/dev/null']
        subprocess.check_call(command, stdin=STDIN)
        
        # two display
        command = [VBOXM] + ['modifyvm', name, '--monitorcount', '2']
        subprocess.check_call(command, stdin=STDIN)
        
        # scale factor to 0.7
        command = [VBOXM] + ['setextradata', name, 'GUI/ScaleFactor', '0.7']
        subprocess.check_call(command, stdin=STDIN)

        # set signature
        command = [VBOXM] + ['setextradata', name, 'wemul', 'ose']
        subprocess.check_call(command, stdin=STDIN)

    except subprocess.CalledProcessError as e:
        print("webos-emulator : creation error")
        logging.debug("creation error : %s" % e)
        return False
    else: # creation success
        if vd.image: # TODO: just create a vd without an image?
            if attach_storage(VBOXM, name, vd.image) == False:
                print("webos-emulator : The vmdk file is already attached. Please use a new vmdk")
                remove_vd(name)
                return False
    return True
        
def start_vd(vd: WebosEmulator):
    """start a vd

    Args:
        vd (WebosEmulator): vd object
    """
    if is_vd_exists(vd.name):
        # TODO: use is_vd_running below
        if is_safe_to_create(vd.name): # TODO: check image is attached meaning for now, we must create a vd with -i option
            if vd.product == "tv":
                # signage : LG_WEBOS_SIGNAGE_SDK_HOME + /Emulator/v4.1.7/LG_webOS_SIGNAGE_Emulator.sh
                if 'LG_WEBOS_TV_SDK_HOME' in os.environ:
                    if platform.system() == 'Windows':
                        command = 'cd ' + os.environ['LG_WEBOS_TV_SDK_HOME'][:3] + ' && cd ' + os.environ['LG_WEBOS_TV_SDK_HOME'] + '\\Emulator\\v' + vd.version + ' && LG_webOS_TV_Emulator.bat'
                    elif platform.system() == 'Darwin':
                        command = 'open ' + os.environ['LG_WEBOS_TV_SDK_HOME'] + '/Emulator/v' + vd.version + '/LG_webOS_TV_Emulator_RCU.app &'
                    else:
                        command = os.environ['LG_WEBOS_TV_SDK_HOME'] + '/Emulator/v' + vd.version + '/LG_webOS_TV_Emulator.sh &'
                    # print("please run : chmod +x " +  os.environ['LG_WEBOS_TV_SDK_HOME'] + "/Resources/Jre/bin/*" )
                else:
                    print("webos-emulator : please check installation of TV Emulator")
                    return False
            elif vd.product == "signage":
                if 'LG_WEBOS_SIGNAGE_SDK_HOME' in os.environ:
                    command = os.environ['LG_WEBOS_SIGNAGE_SDK_HOME'] + '/Emulator/v' + vd.version + '/LG_webOS_SIGNAGE_Emulator.sh &'
                else:
                    print("webos-emulator : please check installation of SIGNAGE Emulator")
                    return False
            else:
                command = [VBOXM] + ['startvm', vd.name]
            
            if vd.product == "ose":
                if subprocess.call(command, stdin=STDIN , stdout=subprocess.DEVNULL,  stderr=get_stderr()) != 0:
                    print("webos-emulator : TV Emulator is needed")
                    return False
            else:
                if subprocess.call(command, stdin=STDIN , stdout=subprocess.DEVNULL,  shell=True, stderr=get_stderr()) != 0:
                    print("webos-emulator : start error")
                    return False
    else:
        print("webos-emulator : vd does not exist!")
        return False
    return True

def stop_vd(vd: WebosEmulator):
    """stop a vd

    Args:
        vd (WebosEmulator): vd object
    """
    if is_vd_exists(vd.name):
        if is_vd_running(vd.name):
            try:
                command = [VBOXM] + ['controlvm', vd.name, 'pause']
                subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL, stderr=get_stderr())
                command = [VBOXM] + ['controlvm', vd.name, 'poweroff']
                subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL, stderr=get_stderr())
            except subprocess.CalledProcessError as e:
                print("webos-emulator : stop error")
                logging.debug("power off error : %s" % e)
                return False
            return True
        else:
            print("webos-emulator : vd is not running.")
            return False
    return False

def delete_vd(vd: WebosEmulator):
    """delete a vd

    Args:
        vd (WebosEmulator): vd object
    """
    if is_vd_exists(vd.name):
        if not is_vd_running(vd.name):
            if detach_image(vd.name):
                command = [VBOXM] + ['unregistervm', vd.name, '--delete']
                if subprocess.call(command, stdin=STDIN, stderr=get_stderr()) != 0:
                    logging.error("webos-emulator error : delete_vd failed")
                    logging.debug("reason : unregistervm failed ")
            else:
                print("webos-emulator : delete_vd failed")
        else:
            print("webos-emulator : vd is running. please stop vd before delete")

def set_default(vd: WebosEmulator, extended):
    """set default values

    Args:
        vd (WebosEmulator): vd object
        exteneded : function extended for vs code extension integration
    """
    name = vd.name
    try:
        logging.info("set default....")
        #command = [VBOXM] + ['modifyvm', name, '--ostype', 'Linux_64']
        #subprocess.check_call(command, stdin=STDIN)

        if extended:
            command = [VBOXM] + ['storagectl', name, '--add', 'ide', '--name', name]
            subprocess.check_call(command, stdin=STDIN)
            command = [VBOXM] + ['modifyvm', name, '--boot1', 'disk', '--boot2', 'none', '--boot3', 'none', '--boot4', 'none']
            subprocess.check_call(command, stdin=STDIN)
            if vd.vmdkfile:
                command = [VBOXM] + ['storageattach', name, '--storagectl', name, '--type',
                         'hdd', '--port', '0', '--device', '0', '--medium', vd.vmdkfile]
                subprocess.check_call(command, stdin=STDIN)

        # setting memory, videoram and cpu
        command = [VBOXM] + ['modifyvm', name, '--memory', vd.ram, '--vram', vd.vram, '--ioapic', 'on', '--cpus', vd.cpus]
        subprocess.check_call(command, stdin=STDIN)

        # setting graphics stuffs
        command = [VBOXM] + ['modifyvm', name, '--graphicscontroller', 'vmsvga']
        subprocess.check_call(command, stdin=STDIN)
        command = [VBOXM] + ['modifyvm', name, '--accelerate3d', 'on']
        subprocess.check_call(command, stdin=STDIN)

        # set usb tablet and sound
        if platform.system() == 'Windows':
            command = [VBOXM] + ['modifyvm', name, '--mouse', 'usbtablet', '--audio', 'dsound', '--audioout', 'on', '--audioin', 'on']
        elif platform.system() == 'Darwin':
            command = [VBOXM] + ['modifyvm', name, '--mouse', 'usbtablet', '--audio', 'coreaudio', '--audioout', 'on', '--audioin', 'on']
        else:
            command = [VBOXM] + ['modifyvm', name, '--mouse', 'usbtablet', '--audio', 'pulse', '--audioout', 'on', '--audioin', 'on']
        subprocess.check_call(command, stdin=STDIN)

        # remove network
        #sp = subprocess.Popen([command, '-version'], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #version, error = sp.communicate()

        try:
            command = [VBOXM] + ['modifyvm', name, '--nic1', 'nat', '--natpf1', 'delete', 'ssh']
            subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL, stderr=get_stderr()) # virtualbox7 needs "stderr=get_stderr()"
        except:
            pass
        try:
            command = [VBOXM] + ['modifyvm', name, '--nic1', 'nat', '--natpf1', 'delete', 'web-inspector']
            subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL, stderr=get_stderr())
        except:
            pass
        try:
            command = [VBOXM] + ['modifyvm', name, '--nic1', 'nat', '--natpf1', 'delete', 'enact-browser-web-inspector']
            subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL, stderr=get_stderr())
        except:
            pass

        # setting network
        command = [VBOXM] + ['modifyvm', name, '--nic1', 'nat', '--natpf1', 'ssh,tcp,,'+ vd.hostssh  +',,22']
        subprocess.check_call(command, stdin=STDIN)
        command = [VBOXM] + ['modifyvm', name, '--natpf1', 'web-inspector,tcp,,9998,,9998']
        subprocess.check_call(command, stdin=STDIN)
        command = [VBOXM] + ['modifyvm', name, '--natpf1', 'enact-browser-web-inspector,tcp,,9223,,9999']
        subprocess.check_call(command, stdin=STDIN)

        # serial to null
        if platform.system() == 'Windows':
            command = [VBOXM] + ['modifyvm', name, '--uart1', '0x3f8', '4', '--uartmode1', 'file', 'null']
        else:
            command = [VBOXM] + ['modifyvm', name, '--uart1', '0x3f8', '4', '--uartmode1', 'file', '/dev/null']
        subprocess.check_call(command, stdin=STDIN)

        # monitor
        if extended:
            command = [VBOXM] + ['modifyvm', name, '--monitorcount', vd.monitorcount]
        else:
            command = [VBOXM] + ['modifyvm', name, '--monitorcount', '2']
        subprocess.check_call(command, stdin=STDIN)

        # scale factor to 0.7
        if extended:
            command = [VBOXM] + ['setextradata', name, 'GUI/ScaleFactor', vd.scalefactor]
        else:
            command = [VBOXM] + ['setextradata', name, 'GUI/ScaleFactor', '0.7']
        subprocess.check_call(command, stdin=STDIN)

        # set signature
        command = [VBOXM] + ['setextradata', name, 'wemul', 'ose']
        subprocess.check_call(command, stdin=STDIN)

    except subprocess.CalledProcessError as e:
        print("webos-emulator : setting error")
        logging.debug("setting error : %s" % e)
        return False

    return True

def default_vd(vd: WebosEmulator):
    """set to default settings

    Args:
        vd (WebosEmulator): vd object
    """
    if is_vd_exists(vd.name):
        if not is_vd_running(vd.name):
            if set_default(vd, False):
                return True
            else:
                print("webos-emulator : default_vd failed")
        else:
            print("webos-emulator : vd is running. please stop vd before setting default")
    return False

def hidden_create(vd: WebosEmulator):
    """hidden create vd

    Args:
        vd (WebosEmulator): vd object
    """
    if is_vd_exists(vd.name):
        if not is_vd_running(vd.name):
            if set_default(vd, True):
                return True
            else:
                print("webos-emulator : hidden_create failed")
        else:
            print("webos-emulator : vd is running. please stop vd before hidden create")
    return False

def custom_vd(vd: WebosEmulator, ovafile):
    """set to default settings

    Args:
        vd (WebosEmulator): vd object
        ovafile: ova format 1.0 file
    """
    if not is_vd_exists(vd.name):
        try:
            logging.info("custom vd....")
            command = [VBOXM] + ['import', ovafile, '--vsys', '0', '--vmname', vd.name]
            subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL, stderr=get_stderr())
            command = [VBOXM] + ['modifyvm', vd.name, '--boot1', 'disk', '--boot2', 'none', '--boot3', 'none', '--boot4', 'none']
            subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL)
            old_name = get_storage_name(vd.name)
            if old_name:
                command = [VBOXM] + ['storagectl', vd.name, '--name', old_name, '--rename', vd.name]
                subprocess.check_call(command, stdin=STDIN, stdout=DEVNULL)
        except subprocess.CalledProcessError as e:
            print("webos-emulator : custom error")
            logging.debug("custom error : %s" % e)
            return False
        else: # creation success
            if vd.image: # TODO: just create a vd without an image?
                if attach_storage(VBOXM, vd.name, vd.image): # TODOL check ok
                    print("webos-emulator : custom error")
                    return False
        return True
    else:
        print("webos-emulator : vd is exist. please delete vd before setting custom file")
    return False
