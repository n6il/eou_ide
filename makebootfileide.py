#!/usr/bin/python
import os
import sys
import argparse
import subprocess
import shlex
import json

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
    parser.add_argument(
        '-d',
        '--dw',
        dest='dw',
        help='Make Dw Image in addition to IDE image')

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

    # dw
    dwTypes = ['becker', 'bitBanger', 'bbCoCo1', 'rs232', 'mmmpi']
    if args.dw and args.dw not in dwTypes:
        print('ERROR: %s: not a valid dw type. Pick from %s' % (args.dw, dwTypes))
        err = 1


    if err:
        parser.print_usage()
        sys.exit(1)
    return args

def pathSetup(args, subDir=None):
    buildSubDir = args.cpu
    if subDir is not None:
        buildSubDir = '%s_%s' % (args.cpu, subDir)
    args.scriptDir = os.path.dirname(os.path.abspath(__file__))
    args.buildDir = os.path.join(args.scriptDir, 'build', buildSubDir)
    args.moduleDir = os.path.join(args.buildDir, 'modules')
    args.localModuleDir = os.path.join(args.scriptDir, args.cpu)
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

EOUMODDIR='MODULES/%sL2/MODULES' % (args.cpu)

os9_format='os9 format -e %s'
os9_copy='os9 copy %s,%s %s'
os9_modbust='os9 modbust %s,OS9Boot'
os9_gen='os9 gen -b%s -t%s %s'

kernel_ide='kernel_ide'
bootfile_ide='OS9Boot'

miscFiles = ('README.txt', 'hdblba.rom', 'start-ide.sh')
scriptFiles = ('start-ide.sh',)

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
        mods.append(lp[2].replace('...', ''))
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
                raise Exception('KwikGen: %s: Module not found' % after)
        else:
            raise Exception('KwinGen: Unknown action: %s' % action)
    copyFile(mods, dst)
    os.chdir(pwd)

def doBuild(buildDir, localMods, copyMods, kernelMods, kwMods):
    print('-' * 50)
    print("0. setup")
    if not os.path.exists(os.path.dirname(buildDir)) or not os.path.exists(buildDir):
        os.makedirs(buildDir)
    moduleDir = os.path.join(buildDir, "modules")
    if not os.path.exists(moduleDir):
        os.makedirs(moduleDir)

    pwd = os.getcwd()

    print('-' * 50)
    print("1. Copy some modules out of the EOU Disk")
    os.chdir(moduleDir)
    #for d, mod in modsCopy:
    for d, mod in copyMods:
        path='/'.join([EOUMODDIR, d, mod])
        cmd = os9_copy % (args.EOUVHD, path, mod)
        runCmd(cmd)

    print('-' * 50)
    print("2. Copy local modules into module dir")
    os.chdir(moduleDir)
    copyPath(localMods, args.localModuleDir, moduleDir)

    print('-' * 50)
    print("3. Create kernel containing boot_ide")
    os.chdir(buildDir)
    copyFile(addPath(moduleDir, kernelMods), kernel_ide)

    print('-' * 50)
    print("4. Make new boot file which has IDE drivers inserted")
    newBootFile = os.path.join(buildDir, 'OS9Boot')
    #kwikGen(moduleDir, args.EOUVHD, newBootFile, instns)
    kwikGen(moduleDir, args.EOUVHD, newBootFile, kwMods)

    print('-' * 50)
    print("5. Make a new boot disk using the new kernel and OS9Boot")
    cmd = os9_format % (args.IDEDSK)
    if (os.path.exists(args.IDEDSK)):
        print('rm %s' % args.IDEDSK)
        os.unlink(args.IDEDSK)
    runCmd(cmd)
    cmd = os9_gen % (bootfile_ide, kernel_ide, args.IDEDSK)
    runCmd(cmd)

    print('-' * 50)
    print("6. Start making the new IDE VHD Disk.  Copy the floppy disk image to the")
    print("   drive with padding to IDE's 512-byte sectors")
    copyFile([args.IDEDSK], args.IDEVHD, pad=True)
    copyFile([args.IDEDSK], args.IDEDSK+'.pad', pad=True)

    print('-' * 50)
    print("7. Nitros9 knows how to do 512-byte sectors, copy the contents of the")
    print("   EOU disk into the IDE VHD.")
    copyFile([args.EOUVHD], args.IDEVHD, mode='ab')

    print('-' * 50)
    print("8. Make the XRoar IDE Image. XRoar needs a header, so put that on first")
    copyFile([args.IDEHDR], args.IDEIDE)
    copyFile([args.IDEVHD], args.IDEIDE, mode='ab')

    print('-' * 50)
    print("9. Copy Misc files to build dir")
    copyPath(miscFiles, args.scriptDir, buildDir)
    copyPath(scriptFiles, args.localModuleDir, buildDir)
    os.chdir(pwd)

## main

kwikGenList = [['ide']]
if args.dw:
    kwikGenList += [['ide', 'dw_%s' % (args.dw)]]

msgs = []
for kwikGens in kwikGenList:
    localMods = []
    copyMods = []
    kernelMods = []
    instns = []
    subDir = '_'.join(kwikGens)
    args = pathSetup(args, subDir=subDir)
    for kw in kwikGens:
        with open(os.path.join(args.scriptDir, 'kwikgens', kw+'.json')) as f:
                t = json.load(f)
                localMods += t.get('localMods', [])
                copyMods += t.get('copyMods', [])
                kernelMods += t.get('kernelMods', [])
                instns += t.get('instructions', [])
    msg = []
    print('')
    msg.append('='*50)
    msg.append('KwikGens: %s' % kwikGens)
    msg.append('Output Dir: %s' % args.buildDir)
    msg.append('='*50)
    print('\n'.join(msg))
    msgs += msg
    doBuild(args.buildDir, localMods, copyMods, kernelMods, instns)


print('')
print('\n'.join(msgs))
