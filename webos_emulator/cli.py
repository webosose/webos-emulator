"""
  Copyright (c) 2022-2023 LG Electronics Inc.
  SPDX-License-Identifier: MIT
"""

"""Console script for webos-emulator."""
import argparse
import sys
from typing import List, Optional
import logging
import os

from webos_emulator import __version__
from webos_emulator import WebosEmulator
from webos_emulator.webos_emulator import attach_storage, create_vd, custom_vd, default_vd, delete_vd, hidden_create, modify_vd, set_default, start_vd, stop_vd, VD_JSON
from webos_emulator.check import VBOXM, validate_vd_name, is_vd_exists, is_vd_running

def main():
    """webOS Emulator Launcher"""
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    parser = argparse.ArgumentParser(description=main.__doc__)
    args = _parse_args(parser)
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    """if args.vd_image:
        vd = WebosEmulator("webos-imagex")
        vd.image = args.vd_image
        if create_vd(vd):
            start_vd(vd)
        return 0
    """
   
    if args.express:
        vd = WebosEmulator("webos-imagex", "webos-imagex")
        if args.express != "configured":
            if is_vd_running(vd.name):
                print("If you want to launch emulator, please start emualtor as below")
                print("webos-emulator -x")
            if os.path.isfile(args.express):
                vd.image = args.express
            else:
                print("webos-emulator : Please check %s exists." % args.express)
                return 1
            if VD_JSON['ram']:
                vd.ram = VD_JSON['ram']
            if create_vd(vd) == False:  # TODO: create webos-emulator class and use
                print("webos-emulator : failed")
                return 1

        vd.product = "ose"
        if is_vd_exists(vd.name):
            if is_vd_running(vd.name):
                stop_vd(vd)
            else:
                start_vd(vd)
        else:
            print("Please specify a vmdk full path to make and launch emulator like below")
            print("   webos-emulator -x  /path/to/abc.vmdk")
            print("If you have made the emulator, you can launch or kill the emulator as")
            print("   webos-emulator -x")
            return 1
        return 0
    
    if args.list:
        validate_vd_name("__list_images__", True)
        return 0
    
    name = ""
    uuid = ""
    product = "ose"
    name,uuid,product,version = validate_vd_name(args.vd, False)
    if name == "__VBOX_NOT_INSTALLED__":
        return 1

    if args.vd:
        if product == "tv" or product == "signage":
            if args.modify or args.hidden_create or args.delete or args.image or args.default:
                print("Only start and kill commands are permitted for TV/Signage Emulator.")
                return 1

    if args.create:
        if args.vd == None:
            print("Please specify a vd name with -vd <name>")
            return 1
        #if not args.vd.startswith("ose_"):
        #    print("Please specify vd name as ose_version like ose_475")
        #    return 2
        ose_name = args.vd # TODO: need to check args.vd is product_version
        vd = WebosEmulator(ose_name, args.vd)
        if args.image:
            if os.path.isfile(args.image):
                vd.image = args.image
            else:
                print("webos-emulator : Please check %s exists." % args.image)
                return 1
        if VD_JSON['ram']:
            vd.ram = VD_JSON['ram']
        create_vd(vd)  # TODO: create webos-emulator class and use
        return 0

    if args.custom:
        if args.vd == None:
            print("Please specify a vd name with -vd <name>")
            return 1
        #if not args.vd.startswith("ose_"):
        #    print("Please specify vd name as ose_version like ose_475")
        #    return 2
        ose_name = args.vd # TODO: need to check args.vd is product_version
        vd = WebosEmulator(ose_name, args.vd)
        if args.image:
            if os.path.isfile(args.image):
                vd.image = args.image
            else:
                print("webos-emulator : Please check %s exists." % args.image)
                return 1
        if VD_JSON['ram']:
            vd.ram = VD_JSON['ram']
        if custom_vd(vd, args.custom) == False:  # TODO: create webos-emulator class and use
            return 1
        return 0

    if args.modify or args.hidden_create or args.start or args.stop or args.delete or args.default:
        if args.vd == None:
            print("Please specify a vd name with -vd <name>")
            return 1
        if name == "":
            print("Please check vd list via webos-emulator -l")
            return 1

    if args.modify:
        mstr = ""
        if args.memory:
            mstr = mstr + "--memory:" + str(args.memory) +":"
        if args.vram:
            mstr = mstr + "--vram:" + str(args.vram)+":"
        if args.cpus:
            mstr = mstr + "--cpus:" + str(args.cpus)+":"
        if args.monitorcount:
            mstr = mstr + "--monitorcount:" + str(args.monitorcount)+":"
        if args.name:
            mstr = mstr + "--name:" + str(args.name)+":"
        if args.ostype:
            if args.ostype != "Linux" and args.ostype != "Linux_64":
                print("Please specify a correct ostype name: Linux or Linux_64")
                return 1
            mstr = mstr + "--ostype:" + str(args.ostype)+":"
        vd = WebosEmulator(name, args.vd)
        vmdk = ""
        if args.vmdk:
            vmdk = args.vmdk.name
        modify_vd(vd, mstr, args.name, vmdk)
    elif args.hidden_create:
        vd = WebosEmulator(name, args.vd)
        mstr = ""
        if args.memory:
            vd.ram = str(args.memory)
        if args.vram:
            vd.vram = str(args.vram)
        if args.cpus:
            vd.cpus = str(args.cpus)
        if args.monitorcount:
            vd.monitorcount = str(args.monitorcount)
        if args.scalefactor:
            vd.scalefactor = str(args.scalefactor)
        if args.name:
            vd.name = str(args.name)
        if args.ostype:
            if args.ostype != "Linux" and args.ostype != "Linux_64":
                print("Please specify a correct ostype name: Linux or Linux_64")
                return 1
            vd.name = str(args.ostype)
        vmdk = ""
        if args.vmdk:
            vd.vmdkfile = str(args.vmdk.name)
        hidden_create(vd)
    elif args.image:
        if not os.path.isfile(args.image):
            print("webos-emulator : Please check %s exists." % args.image)
            return 1
        if name == "":
            print("Please specify a existing vd name")
            return 1
        vd = WebosEmulator(name, args.vd)
        vd.image = args.image
        if VD_JSON['ram']:
            vd.ram = VD_JSON['ram']
        # create_vd(vd)  # TODO: create webos-emulator class and use
        attach_storage(VBOXM, vd.name, vd.image)
    elif args.start:
        vd = WebosEmulator(name, args.vd)
        if product == "tv":
            vd.product = "tv"
            vd.version = version
        elif product == "signage":
            vd.product = "signage"
            vd.version = version
        start_vd(vd)
    elif args.stop:
        vd = WebosEmulator(name, args.vd)
        stop_vd(vd)
    elif args.delete:
        vd = WebosEmulator(name, args.vd)
        delete_vd(vd)
    elif args.default:
        vd = WebosEmulator(name, args.vd)
        default_vd(vd)
    elif args.custom:
        vd = WebosEmulator(name, args.vd)
        custom_vd(vd, args.custom)
    else:
        parser.print_help()

    return 0

def _parse_args(parser: argparse.ArgumentParser, args: Optional[List] = None) -> argparse.Namespace:
    vd_grp = parser.add_argument_group('Commands')
    vd_grp = vd_grp.add_mutually_exclusive_group()
    vd_grp.add_argument(
        "-l",
        "--list",
        action="store_true",
        dest="list",
        help="list all the vd names",
    )
    parser.add_argument(
        "-vd",  # change vm option to vd
        metavar='<name> or <uuid>',
        help="use a webOS emulator name as product_version like ose_475",
    )
    vd_grp.add_argument(
        "-m",
        "--modify",
        action="store_true",
        dest="modify",
        help="Modify a webOS emulator settings",
    )
    vd_grp.add_argument(
        "--hidden-vce-create",
        action="store_true",
        dest="hidden_create",
        help=argparse.SUPPRESS,
    )

    parser.add_argument("--memory", type=int, help=argparse.SUPPRESS) # https://docs.python.org/3/library/argparse.html
    parser.add_argument("--vram", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--cpus", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--monitorcount", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--name", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--ostype", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--vmdk", type=argparse.FileType('r'), help=argparse.SUPPRESS)
    parser.add_argument("--scalefactor", type=str, help=argparse.SUPPRESS)

    #parser.add_argument(
    #    "vd_image", help="create and run vd_image (ose emulator only)", nargs="?"
    #)
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__,
    )
    vd_grp.add_argument(
        "-c",
        "--create",
        action="store_true",
        dest="create",
        help="Create a webOS emulator",
    )
    parser.add_argument(
        "-i",
        "--image",
        metavar='<file>',
        help="specify virtualbox image file",
    )
    vd_grp.add_argument(
        "-s",
        "--start",
        action="store_true",
        dest="start",
        help="Start a webOS emulator",
    )
    vd_grp.add_argument(
        "-k",
        "--kill",
        action="store_true",
        dest="stop",
        help="Kill a running webOS emulator",
    )
    vd_grp.add_argument(
        "-d",
        "--delete",
        action="store_true",
        dest="delete",
        help="Delete a webOS emulator",
    )
    vd_grp.add_argument(
        "-ds",
        "--default-settings",
        action="store_true",
        dest="default",
        help="Set to default settings",
    )
    vd_grp.add_argument(
        "-cc",
        "--create-with-custom",
        action="store",
        metavar='<.ova>',
        dest="custom",
        help="Create a emulator with a custom settings using OVF 1.0 file",
    )
    vd_grp.add_argument(
        "-x",
        "--express",
        nargs='?',
        action="store",
        const="configured",
        metavar='<.vmdk>',
        dest="express",
        help='Launch a emulator if vmdk is given, without vmdk option launch or kill the emulator',
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        dest="debug",
        help="Show debug info",
    )
        
    return parser.parse_args(args)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
