meta:
  id: asset_index
  file-extension: funnycat
  endian: le
  encoding: UTF-8

seq:
  - id: type_mapping_count
    type: u4
  - id: type_mapping
    type: type_mapping_entry
    repeat: expr
    repeat-expr: type_mapping_count
    doc: This specifies what specific type is serialized into (?)
    
  - id: asset_count
    type: u4
  - id: assets
    type: asset_info
    repeat: expr
    repeat-expr: asset_count
    doc: List of all the assets in the game, with their names, hashes and types
    
  - id: dependency_count
    type: u4
  - id: dependencies
    type: dependency_info
    repeat: expr
    repeat-expr: dependency_count
    doc: List of inter-asset dependencies
    
  - id: preload_blocks_count
    type: u4
  - id: preload_blocks
    type: u4
    repeat: expr
    repeat-expr: preload_blocks_count
    doc: Blocks to be preoaded during the game start (?)
    
  - id: preload_shader_blocks_count
    type: u4
  - id: preload_shader_blocks
    type: u4
    repeat: expr
    repeat-expr: preload_shader_blocks_count
    doc: Blocks containing shaders to be preloaded during the game startup (?)
    
  - id: block_group_count
    type: u4
  - id: block_groups
    type: block_group
    repeat: expr
    repeat-expr: block_group_count
    doc: Info about distribution of BLKs in file system directories
    
  - id: block_info_count
    type: u4
  - id: block_infos
    type: block_info
    repeat: expr
    repeat-expr: block_info_count
    doc: Info about distribution of assets in BLKs
    
  - id: block_count_again
    type: u4
  - id: unk_block_list
    type: u4
    repeat: expr
    repeat-expr: block_count_again
    doc: Just list of some (?) BLKs (maybe has to do something with BLK overriding?)
    
types:
  string:
    seq:
      - id: len
        type: u4
      - id: data
        type: str
        size: len
        
  type_mapping_entry:
    seq:
      - id: name
        type: string
      - id: mapped_to
        type: string
        
  asset_info:
    seq:
      - id: asset_id
        type: u4
      - id: hash
        type: u4
      - id: type_id
        type: u4
      - id: name
        type: string
        
  dependency_info:
    doc: Describes that asset asset_id depends on assets from the specified list
    seq:
      - id: asset_id
        type: u4
      - id: dependency_info_count
        type: u4
      - id: dependencies_list
        type: u4
        repeat: expr
        repeat-expr: dependency_info_count
        
  block_info:
    doc: Specifies which assets this specific block contains and their offsets in the BLK file
    seq:
      - id: block_id
        type: u4
      - id: asset_offset_count
        type: u4
      - id: asset_offsets
        type: asset_offset_info
        repeat: expr
        repeat-expr: asset_offset_count
        
  asset_offset_info:
    seq:
      - id: asset_id
        type: u4
      - id: offset
        type: u4
        
  block_group:
    doc: List of BLKs in a directory specified by the group_id
    seq:
      - id: group_id
        type: u4
      - id: block_count
        type: u4
      - id: block_list
        type: u4
        repeat: expr
        repeat-expr: block_count
