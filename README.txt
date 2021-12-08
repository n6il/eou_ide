+==============================+
| EOU for GlensideIDE/SuperIDE |
| And XRoar Emulation          |
|                              |
| Michael Furman (MikeyN6IL)   |
| 7 Dec 2021                   |
+==============================+

This is a DIY Pack for setting up EOU to work on a GlensideIDE, SuperIDE,
or in XRoar with an emulated GlensideIDE.

The makebootfileide.py script creates the following disk images:

   68IDE.VHD -- This is a VHD disk image designed for use on IDE Drives.
      You can use this disk on a real GlensideIDE or SuperIDE controller.
      The VHD image will not work on XRoar.

   68IDE.IDE -- This is a special IDE disk image for use with XRoar's
      Glenside IDE emulation.  This image will not work on real hardware.
 
   68IDE.dsk -- This is a boot disk which can load Nitros9 from the VHD or
      XRoar IDE disk images.  It is not required to use this disk.  It is
      already installed on both the VHD and IDE disk images.


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

      XRoar: Use the ide cartridge and attach the 68IDE.IDE image to hd0. Use
             YADOS or HDB-DOS LBA ROM(hdblba.rom).  See the start-ide.sh
             script for a sample command line.

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


Instructions for creating your own IDE Disk images:
===================================================

1. Download a copy of NitrOS-9 Ease Of Use for 6809
2. Make a copy of 68SDC.VHD in this directory
3. Run the script: python ./makebootfileide.py
4. The disk images are created: 68IDE.VHD, 68IDE.ide, and 68IDE.dsk
5. To use it:  See usage instructions above.

