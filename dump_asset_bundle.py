#!/usr/bin/env python3

import sys
import gzip
import bz2
import json
from pathlib import Path
from os.path import dirname

from asset_bundle import AssetBundle
from compute_name_hash import padded_name_hash

if lne(sys.argv) < 3:
    print ()
    print ("Usage: ./tool input_asset_bundle names_list")
    print ("\tinput_asset_bundle should be decrypted beforehand")
    print ("\tnames_list could be grabbed from radioegor's repo")

output_dir = "OUTPUT"

index = json.load(bz2.open(sys.argv[2]))

name_hashes = {}

for _,group in index["SubAssets"].items():
    for e in group:
        name = e["Name"]
        hash4 = padded_name_hash(name, 4)
        hash5 = padded_name_hash(name, 5)
        name_hashes[hash4] = e
        name_hashes[hash5] = e

ab = AssetBundle.from_file(sys.argv[1])
md = ab.archive_metadata

type_id = -1

for i, t in enumerate(md.type_list):
    if t.class_id == 1208:
        type_id = i
        break

if type_id < 0:
    print ("File doesn't contain Lua scripts")
else:
    hash_map = None

    # Find hash map
    for o in md.object_list:
        if md.type_list[o.type_id].class_id == 1210:
            hash_map = {x.script_idx: x.name_hash.data for x in o.body.script_infos}
            break
    
    if hash_map == None:
        raise NameError("Hash map not found!")

    for o in md.object_list:
        if o.type_id == type_id:
            hs = hash_map[o.path_id]
            try:
                name = name_hashes[hs]['Name']
            except:
                name = hs + ".unresolved"
            print("{} {}".format(name, o.body.len))
            path = "{}/{}".format(output_dir, name)
            Path(dirname(path)).mkdir(parents=True, exist_ok=True)
            open(path, "wb").write(o.body.data)
