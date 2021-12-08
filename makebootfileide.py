#!/usr/bin/python
import os

IDEDSK='68IDE.dsk'
EOUVHD='68SDC.VHD'
IDEVHD='68IDE.VHD'
IDEHDR='header.ide'
IDEIDE='68IDE.ide'
EOUMODDIR='MODULES/6809L2/MODULES'

os9_format='os9 format -e %s'
os9_copy='os9 copy %s,%s %s'
os9_modbust='os9 modbust %s,OS9Boot'
os9_gen='os9 gen -b%s -t%s %s'

kernel_ide='kernel_ide'
bootfile_ide='OS9Boot'

modsCopy = (('boottrack','rel_80'), ('boottrack','krn_beta5'))
modsKernel = ('rel_80', 'boot_ide', 'krn_beta5')

mods = (
	'KrnP2',
	'KrnP3',
	'IOMan',
	'Init',
	'RBF',
	'RBSuper',
	'llide.dr',
	'ddi0_ide.dd',
	'i0_ide.dd',
	'i1_ide.dd',
	'rb1773',
	'D0',
	'D1',
	'Rammer',
	'R0',
	'MD',
	'SCF',
	'VTIO',
	'JoyDrv',
	'SndDrv',
	'CoWin',
	'CoVDG',
	'Term',
	'W',
	'W1',
	'W2',
	'W3',
	'W4',
	'W5',
	'W6',
	'W7',
	'W8',
	'W9',
	'W10',
	'W11',
	'W12',
	'W13',
	'W14',
	'W15',
	'Verm',
	'scbbp',
	'p',
	'VRN',
	'Nil',
	'VI',
	'FTDD',
	'PipeMan',
	'Piper',
	'Pipe',
	'Clock',
	'Clock2',
)

padding='\x00'*256

def copyFile(fnl, gn, pad=False, mode='wb'):
    g=open(gn, mode)
    for fn in fnl:
        f=open(fn)
        data = f.read(256)
        i=256
        while data:
            g.write(data)
            if pad:
                g.write(padding)
            data = f.read(256)
            i += 256
        f.close()
    g.close()

# 1. Copy some modules out of the EOU Disk
for d, mod in modsCopy:
    path='/'.join([EOUMODDIR, d, mod])
    cmd = os9_copy % (EOUVHD, path, mod)
    os.system(cmd)

# 2. Create kernel containing boot_ide
copyFile(modsKernel, kernel_ide)

# 3. Use modbust to get all the modules out of the existing EOU OS9Boot
cmd = os9_modbust % (EOUVHD)
os.system(cmd)

# 4. Make new boot file which has IDE drivers inserted
copyFile(mods, bootfile_ide)

# 5. Make a new boot disk using the
cmd = os9_format % (IDEDSK)
if (os.path.exists(IDEDSK)):
    os.unlink(IDEDSK)
os.system(cmd)
cmd = os9_gen % (bootfile_ide, kernel_ide, IDEDSK)
os.system(cmd)

# 6. Start making the new IDE VHD Disk.  Copy the floppy disk image to the
# drive with padding to IDE's 512-byte sectors
copyFile([IDEDSK], IDEVHD, pad=True)

# 7. Nitros9 knows how to do 512-byte sectors, copy the contents of the
#    EOU disk into the IDE VHD.
copyFile([EOUVHD], IDEVHD, mode='ab')

# 8. Make the XRoar IDE Image. XRoar needs a header, so put that on first
copyFile([IDEHDR], IDEIDE)
copyFile([IDEVHD], IDEIDE, mode='ab')

