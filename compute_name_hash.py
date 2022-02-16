#!/usr/bin/env python3

import hashlib

def padded_name_hash(path, s = 5):
    return compute_name_hash(path + ".MiHoYoBinData", s)

def compute_name_hash(path, s = 5):
    path = path.encode('ascii')
    pad = ((len(path) >> 8) + 1) << 8;
    bts = path + bytes([0] * (pad - len(path)))
    m = hashlib.md5()
    m.update(bts)
    dgst = m.digest()[:s]
    return ''.join(["{:02x}".format(i) for i in reversed(dgst)])[:8]

if __name__ == '__main__':
    test1 = "Data/_ExcelBinOutput/WorldLevelExcelConfigData"
    print ("8EBCF66D - ", padded_name_hash(test1, 4))
    test2 = "Lua/Scene/3/scene3_block3001.lua"
    print ("468B3142 - ", padded_name_hash(test2, 5))
