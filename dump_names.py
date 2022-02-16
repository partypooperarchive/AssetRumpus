#!/usr/bin/env python3

import sys
import json

from asset_index import AssetIndex

from compute_name_hash import padded_name_hash

ai = AssetIndex.from_file(sys.argv[1])

ass_block_map = {}

for bi in ai.block_infos:
    for ao in bi.asset_offsets:
        ass_block_map[ao.asset_id] = (bi.block_id, ao.offset)

name_file_hashes = {}

for i, ass in enumerate(ai.assets):
    bi = ass_block_map[ass.asset_id]
    d_name = ass.name.data
    if not d_name:
        d_name = "(stripped)"
    print ("{:06d} {} {} {:08X} {} ({:08d} {:08X})".format(i, ass.asset_id, ass.type_id, ass.hash, d_name, bi[0], bi[1]))
    name = ass.name.data.replace("LuaBytes", "Lua", 1)
    name_hash = padded_name_hash(name)
    name_file_hashes[name_hash] = {"name": name, "file_hash": ass.hash}

print (json.dumps(name_file_hashes, indent=4, sort_keys=True))
