#!/usr/bin/python
import os
import sys
import argparse
import subprocess
import shlex

def parseArgs():
    parser = argparse.ArgumentParser(
        description='EOU Ide Disk Creator')
    parser.add_argument(
        '-c',
        '--cpu',
        dest='cpu',
        help='CPU Type: 6809 or 6309')
    parser.add_argument(
        '-i',
        '--vhd',
        dest='EOUVHD',
        help='Source EOU VHD File')

    args = parser.parse_args()

    # error handling
    cpus = ['6809', '6309']
    err = False

    # required options
    # cpu
    if args.cpu is None:
        print('ERROR: Must specify cpu type: %s' %(cpus))
        err = True
    else:
        if args.cpu not in cpus:
            print('ERROR: %s: Invalid CPU. Pick from %s' % (args.cpu, cpus))
            err = True
        else:
            args.cpuShort = args.cpu[:2]

    # vhd path
    if args.EOUVHD is None:
        print('ERROR: Must specify source EOU VHD File')
        err = True
    else:
        p = os.path.abspath(os.path.expanduser(args.EOUVHD))

        if os.path.exists(p):
            args.EOUVHD = p
        else:
            print('ERROR: %s: no such file' % args.EOUVHD)
            err = True

    
    if err:
        print(args)
        parser.print_usage()
        sys.exit(1)
    return args

def pathSetup(args):
    args.scriptDir = os.path.dirname(os.path.abspath(__file__))
    args.buildDir = os.path.join(args.scriptDir, 'build', args.cpu)
    args.moduleDir = os.path.join(args.buildDir, 'modules')
    args.ideModuleDir = os.path.join(args.scriptDir, args.cpu)
    args.IDEHDR = os.path.join(args.scriptDir, 'header.ide')
    args.IDEDSK = os.path.join(args.buildDir, '%sIDE.dsk' % (args.cpuShort))
    args.IDEVHD = os.path.join(args.buildDir, '%sIDE.VHD' % (args.cpuShort))
    args.IDEIDE = os.path.join(args.buildDir, '%sIDE.ide' % (args.cpuShort))
    return args

def runCmd(cmd):
    cp = shlex.split(cmd)
    print(cmd)
    p = subprocess.Popen(cp, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    if p.returncode != 0:
        raise Exception('%s: %s' % (cp[0], p.stderr.read()))
    return(p.returncode, p.stdout.read())

args = parseArgs()
args = pathSetup(args)

EOUMODDIR='MODULES/%sL2/MODULES' % (args.cpu)

os9_format='os9 format -e %s'
os9_copy='os9 copy %s,%s %s'
os9_modbust='os9 modbust %s,OS9Boot'
os9_gen='os9 gen -b%s -t%s %s'

kernel_ide='kernel_ide'
bootfile_ide='OS9Boot'

modsCopy = (('boottrack','rel_80'), ('boottrack','krn_beta5'))
ideModules = ('llide.dr', 'i0_ide.dd', 'i1_ide.dd', 'ddi0_ide.dd', 'boot_ide')
modsKernel = ('rel_80', 'boot_ide', 'krn_beta5')

# KwikGen Instructions
instns = [
    {
        'action': 'del',
        'module': 'llcocosdc'
    },
    {
        'action': 'del',
        'module': 'DD'
    },
    {
        'action': 'del',
        'module': 'H1'
    },
    {
        'action': 'ins',
        'module': 'llide.dr',
        'after': 'RBSuper'
    },
    {
        'action': 'ins',
        'module': 'i0_ide.dd',
        'after': 'llide.dr'
    },
    {
        'action': 'ins',
        'module': 'i1_ide.dd',
        'after': 'i0_ide.dd'
    },
    {
        'action': 'ins',
        'module': 'ddi0_ide.dd',
        'after': 'i1_ide.dd'
    },
]


padding=b'\x00'*256

def copyPath(fnl, spn, dpn):
    for fn in fnl:
        sfn = os.path.join(spn, fn)
        dfn = os.path.join(dpn, fn)
        print('cp %s %s' % (sfn, dfn))
        f=open(sfn, 'rb')
        g=open(dfn, 'wb')
        g.write(f.read())
        f.close()
        g.close()

def copyFile(fnl, gn, pad=False, mode='wb'):
    g=open(gn, mode)
    dd = '>'
    if mode.startswith('a'):
        dd = '>>'
    for fn in fnl:
        print('cat %s %s %s' % (fn, dd, gn))
        f=open(fn, 'rb')
        data = f.read(256)
        i=256
        while data:
            g.write(data)
            if pad:
                g.write(padding)
            data = f.read(256)
            i += 256
        f.close()
        dd = '>>'
    g.close()

def addPath(path, files):
    return [os.path.join(path, m) for m in files]

# KwikGen: 
#   Starting with an existing Nitros9 VHD, use modbust to get all of the
#   modules out of the OS9Boot file on that VHD.  Modules are placed in the
#   specified path.  Create a new OS9Boot file using the povided
#   instructions.  The result is placed at the specified dst location.
# Path: Working directory where modules should go
# srcVhd - Nitros9 VHD
# dst - path to new OS9Boot file
# instList - list of instructions
def kwikGen(path, srcVhd, dst, instList):
    pwd = os.getcwd()
    os.chdir(path)
    cmd = os9_modbust % (srcVhd)
    rc, output = runCmd(cmd)
    mods = []
    for l in output.decode('ascii').split('\n'):
        lp = l.split(' ')
        if len(lp) != 3:
            continue
        print(l)
        mods.append(lp[2].replace('...', ''))
    print(mods)
    for inst in instList:
        action = inst['action']
        if action == 'del':
            module = inst['module']
            try:
                i = mods.index(module)
                print('KwikGen: del module: %s' % module)
                del mods[i]
            except ValueError:
                raise Exception('KwikGen: %s: Module not found' % module)
        elif action == 'ins':
            module = inst['module']
            after = inst['after']
            try:
                i = mods.index(after)
                print('KwikGen: ins module: %s after %s' % (module, after))
                mods.insert(i+1, module)
            except ValueError:
                raise Exception('KwikGen: %s: Module not found' % module)
        else:
            raise Exception('KwinGen: Unknown action: %s' % action)
    copyFile(mods, dst)
    os.chdir(pwd)

# setup
if not os.path.exists(os.path.dirname(args.buildDir)) or not os.path.exists(args.buildDir):
    os.makedirs(args.buildDir)
if not os.path.exists(args.moduleDir):
    os.makedirs(args.moduleDir)

pwd = os.getcwd()
# 1. Copy some modules out of the EOU Disk
os.chdir(args.moduleDir)
for d, mod in modsCopy:
    path='/'.join([EOUMODDIR, d, mod])
    cmd = os9_copy % (args.EOUVHD, path, mod)
    runCmd(cmd)

# 2. Copy ide modules into module dir
os.chdir(args.moduleDir)
copyPath(ideModules, args.ideModuleDir, args.moduleDir)

# 3. Create kernel containing boot_ide
os.chdir(args.buildDir)
copyFile(addPath(args.moduleDir, modsKernel), kernel_ide)

# 4. Make new boot file which has IDE drivers inserted
newBootFile = os.path.join(args.buildDir, 'OS9Boot')
kwikGen(args.moduleDir, args.EOUVHD, newBootFile, instns)

# 5. Make a new boot disk using the
cmd = os9_format % (args.IDEDSK)
if (os.path.exists(args.IDEDSK)):
    print('rm %s' % args.IDEDSK)
    os.unlink(args.IDEDSK)
runCmd(cmd)
cmd = os9_gen % (bootfile_ide, kernel_ide, args.IDEDSK)
runCmd(cmd)

# 6. Start making the new IDE VHD Disk.  Copy the floppy disk image to the
# drive with padding to IDE's 512-byte sectors
copyFile([args.IDEDSK], args.IDEVHD, pad=True)

# 7. Nitros9 knows how to do 512-byte sectors, copy the contents of the
#    EOU disk into the IDE VHD.
copyFile([args.EOUVHD], args.IDEVHD, mode='ab')

# 8. Make the XRoar IDE Image. XRoar needs a header, so put that on first
copyFile([args.IDEHDR], args.IDEIDE)
copyFile([args.IDEVHD], args.IDEIDE, mode='ab')

print('Output Dir: %s' % args.buildDir)
os.chdir(pwd)
