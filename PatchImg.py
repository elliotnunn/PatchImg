#!/usr/bin/env python3

import sys
import struct

def load_apm_from_file(f):
    f.seek(512+4)
    pmMapBlkCnt = int.from_bytes(f.read(4), byteorder='big')
    f.seek(0)
    return f.read(512 * (pmMapBlkCnt + 1)) # read the DDM + n APM blocks

def apm_to_tuples(apm):
    for i, offset in enumerate(range(512, len(apm), 512)):
        entry = apm[offset:][:512]

        ptype = entry[48:][:32].rstrip(b'\x00').decode('ascii')
        startblk = int.from_bytes(entry[8:][:4], byteorder='big')
        blkcnt = int.from_bytes(entry[12:][:4], byteorder='big')
        ptype = entry[48:][:32].rstrip(b'\x00').decode('ascii')

        startbyte = startblk * 512
        stopbyte = (startblk + blkcnt) * 512

        yield(startbyte, stopbyte, ptype)

def find_patch_partition(apm):
    for start, stop, ptype in apm_to_tuples(apm):
        if ptype == 'Apple_Patches':
            return start, stop

def list_patches(ppart, devblocksize):
    # This will have some logic to overwrite an existing patch (one hopes...)

    patches = []

    numPatchBlocks, numPatches = struct.unpack_from('>HH', ppart)
    pdes_offset = 4
    for i in range(numPatches):
        pdes_size = int.from_bytes(ppart[pdes_offset + 24:][:4], byteorder='big')
        pdes = ppart[pdes_offset:][:pdes_size]

        patch_offset = int.from_bytes(ppart[pdes_offset + 12:][:4], byteorder='big') * devblocksize
        patch_size = int.from_bytes(ppart[pdes_offset + 16:][:4], byteorder='big')
        patch = ppart[patch_offset:][:patch_size]

        patches.append((pdes, patch))

        pdes_offset += pdes_size

    return patches


img_path = sys.argv[1]

with open(img_path, 'rb') as f:
    apm = load_apm_from_file(f) # actually includes DDM

    print('Partition list:')
    for start, stop, ptype in apm_to_tuples(apm):
        print('[0x%x-0x%x] %s' % (start, stop-1, ptype))
    print()

    ppstart, ppstop = find_patch_partition(apm)
    f.seek(ppstart)
    ppart = f.read(ppstop-ppstart)

    print('Raw patch descriptors:')
    for pdes, patch in list_patches(ppart, devblocksize=2048):
        print(pdes)
