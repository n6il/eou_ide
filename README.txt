+==============================+
| EOU for GlensideIDE/SuperIDE |
| MAME And XRoar Emulation     |
|                              |
| Michael Furman (MikeyN6IL)   |
| 17 Mar 2022                  |
+==============================+

This is a DIY Pack for setting up EOU to work on a GlensideIDE, SuperIDE,
or in MAME or XRoar with an emulated GlensideIDE.

The makebootfileide.py script creates the following disk images in the
build/<CPU> directory.  If you are using 6309 cpu every this document says
"68xxx" you substitute "63xxx" for the 6309 version:

   68IDE.VHD -- This is a VHD disk image designed for use on IDE Drives.
      You can use this disk on a real GlensideIDE or SuperIDE controller.
      The VHD image will not work on XRoar or MAME.

   68IDE.IDE -- This is a special IDE disk image for use with XRoar's
      Glenside IDE emulation.  This image will not work on real hardware 
      or MAME.
 
   68IDE.dsk -- This is a boot disk which can boot Nitros9 from the VHD or
      XRoar IDE disk images.  This disk image should be used for MAME but
      It is not required for XRoar.  It is already installed on both the
      VHD and IDE disk images.


What's on the VHD and IDE Disk images?
======================================

68IDE.VHD is a specially crafted disk image.  It contains the following
partitions:

	First Partition: Sectors 0-629: Contains the 68IDE.dsk with padding
           for 512-byte sectors.
	Second Partition: Sector 630+: Contains the 68SDC.VHD image from
           EOU verbatim without any modifications.

68IDE.IDE is further specialized:

        Header: 1024 byte header required for XRoar. Not seen by the CoCo
	First Partition: Sectors 0-629: Contains the 68IDE.dsk with padding
           for 512-byte sectors.
	Second Partition: Sector 630+: Contains the 68SDC.VHD image from
           EOU verbatim without any modifications.


How to use the disk images:
===========================

     Downloading: Binary or source packages are available here:
        https://github.com/n6il/eou_ide/releases

      XRoar: Use the ide cartridge and attach the 68IDE.IDE image to hd0. Use
             YADOS or HDB-DOS LBA ROM(hdblba.rom).  See the start-ide.sh
             script for a sample command line.

      MAME: Use MAME v0.241 or later.  Attach the IDE card and 68SDC.VHD to
             hard3.  Attach fdcv11 to the IDE Card's Slot and 68IDE.dsk to
             flop1:

             mame coco3 -ext ide -ext:ide:slot fdcv11 -flop1 68IDE.dsk -hard3 68SDC.VHD

             If you want a second HDD add: -ext:ide:ata:1 hdd -hard4 test.vhd

      SuperIDE: Burn the 68IDE.VHD image to a CF Card.  Use YADOS or HDB-DOS
             LBA ROM(hdblba.rom).

      GlensideIDE: Image drive/Card with 68IDE.VHD.  use YADOS or HDB-DOS
             LBA ROM(hdblba.rom)


DIY Package Contents:
=====================

* README.txt -- this file
* boot_ide -- NitrOS-9 IDE Booter HwAddr: $FF50
* llide.dr -- SuperDriver IDE Driver with a small patch
* i0_ide.dd -- Descriptor for /I0 HwAddr: $FF50 Offset: $000276
* i1_ide.dd -- Descriptor for /I1 HwAddr: $FF50 Offset: $000276
* ddi0_ide.dd -- Descriptor for /DD HwAddr: $FF50 Offset: $000276
* header.ide -- XRoar IDE Header
* makebootfileide.py -- Python Script that creates the disk images


Script Usage:
=============
usage: makebootfileide.py [-h] [-c CPU] [-i EOUVHD] [-d DW] [-e EMULATOR]

EOU Ide Disk Creator

optional arguments:
  -h, --help            show this help message and exit
  -c CPU, --cpu CPU     CPU Type: ['6809', '6309']
  -i EOUVHD, --vhd EOUVHD
                        Source EOU VHD File
  -d DW, --dw DW        Make Dw Image in addition to IDE image: ['becker',
                        'bitBanger', 'bbCoCo1', 'rs232', 'mmmpi']
  -e EMULATOR, --emulator EMULATOR
                        Which Emulator to build for: ['xroar', 'mame']


Instructions for creating your own IDE Disk images:
===================================================

1. Download a copy of NitrOS-9 Ease Of Use
2. Note the path of either 68SDC.VHD or 63SDC.VHD
3. Run the script: python ./makebootfileide.py -c <CPU> -i <VHD> -e <emulator>
4. The disk images are created in a build/<CPU> directory: 68IDE.VHD, 68IDE.ide, and 68IDE.dsk
5. To use it:  See usage instructions above.
6. If you want DriveWire support, add the -dbecker option.  This will create a new build directory
	build/<CPU>_becker

Examples:

XRoar 6809 with IDE

    python ./makebootfileide -c 6809 -i ~/demo/eou/6809/68SDC.VHD -e xroar

    python ./makebootfileide --cpu 6809 --vhd ~/demo/eou/6809/68SDC.VHD --emulator xroar

    Output Dir: build/6809_ide_xroar

    Floppy Image: None
    VHD Image: 68IDE.VHD 

MAME 6809 with IDE

    python ./makebootfileide -c 6809 -i ~/demo/eou/6809/68SDC.VHD -e mame

    python ./makebootfileide --cpu 6809 --vhd ~/demo/eou/6809/68SDC.VHD --emulator mame

    Output Dir: build/6809_ide_mame

    Floppy Image: 68IDE.dsk
    VHD Image: 68SDC.VHD (Stock EOU Image)

XRoar 6809 with IDE and DriveWire

    python ./makebootfileide -c 6809 -i ~/demo/eou/6809/68SDC.VHD -e xroar -d becker

    python ./makebootfileide --cpu 6809 --vhd ~/demo/eou/6809/68SDC.VHD --emulator xroar --dw becker

    Note: Command line above makes both DW and Non-Dw versions:

    Output Dir: build/6809_ide_xroar
    Output Dir: build/6809_ide_xroar_dw_becker

MAME 6809 with IDE and DriveWire

    python ./makebootfileide -c 6809 -i ~/demo/eou/6809/68SDC.VHD -e mame -d becker

    python ./makebootfileide --cpu 6809 --vhd ~/demo/eou/6809/68SDC.VHD --emulator mame --dw becker

    Note: Command line above makes both DW and Non-Dw versions:

    Output Dir: build/6809_ide_xroar
    Output Dir: build/6809_ide_xroar_dw_becker

6309:
	Same as above set -c 6309 or --cpu 6309
	Use 63XXX instead of 68XXX for files and directories
