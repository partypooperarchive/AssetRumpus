meta:
  id: asset_bundle
  file-extension: blyat
  endian: le
  encoding: UTF-8
  title: Unity AssetBundle according to format specification V17
  
seq:
  - id: archive_header
    type: header
  - id: archive_metadata
    type: metadata
    
  - id: padding
    size: archive_header.data_offset - archive_header.metadata_size - sizeof<header> + 1 # TODO: +1 is a hack!
    
types:
  header:
    seq:
      - id: metadata_size
        type: u4be
      - id: asset_bundle_size
        type: u4be
        doc: Filesize
      - id: version_number
        type: u4be
      - id: data_offset
        type: u4be
        
      - id: not_null 
        type: u4     
        doc: |
          Supposedly must be related to endianness
          Also, it's supposed to be 1 byte with a 3-byte alignment, but for simplicity I left this out

  metadata:
    seq:
      - id: unity_version 
        type: strz
        doc: String that represents Unity version
        
      - id: target_platform # 19 == StandaloneWindows64
        type: s4
        
      - id: enable_type_trees
        type: u1
    
      - id: type_count
        type: s4
      - id: type_list
        type: serialized_type(false)
        repeat: expr
        repeat-expr: type_count
        
      - id: object_count
        type: s4
      - id: object_list
        type: serialized_object
        repeat: expr
        repeat-expr: object_count
        
      - id: script_count
        type: s4
      - id: script_list
        type: serialized_script
        repeat: expr
        repeat-expr: script_count
        
      - id: externals_count
        type: s4
      - id: externals_list
        type: serialized_external
        repeat: expr
        repeat-expr: externals_count

  serialized_type:
    params:
      - id: is_ref
        type: bool
    seq:
      - id: class_id_raw 
        type: u4be
        doc: See class_id below for the actual value
      - id: is_stripped
        type: u1
      - id: script_type_index
        type: s2
      - id: script_id
        type: u1
        repeat: expr
        repeat-expr: 16
        if: (class_id == 114) or (is_ref and (script_type_index >= 0))
      - id: old_type_hash
        type: u1
        repeat: expr
        repeat-expr: 16
    instances:
      class_id:
        value: (class_id_raw ^ 0x23746FBE) - 3
        
  serialized_object:
    seq:
      - id: path_id
        type: u8
      - id: start_offset
        type: u4
      - id: size
        type: u4
      - id: type_id
        type: u4

    instances:
      body:
        pos: start_offset + _root.archive_header.data_offset
        size: size
        type:
          switch-on: _parent.type_list[type_id].class_id
          cases:
            142:  bundle_info
            1210: lua_hashes_info
            1208: lua_script_data
        
  serialized_script:
    seq:
      - id: local_index
        type: u4
      - id: local_identifier
        type: u8
        
  serialized_external:
    seq:
      - id: empty
        type: strz
      - id: guid
        type: u1
        repeat: expr
        repeat-expr: 16
      - id: type
        type: u4
      - id: path_name
        type: strz
  
  bundle_info:
    seq:
      - id: bundle_name
        type: string
        
      - id: element_count
        type: u4
        
      - id: element_descs
        type: element_desc
        repeat: expr
        repeat-expr: element_count
  
  lua_hashes_info:
    seq:
      - id: unk1
        type: u4
        
      - id: count
        type: u4
        
      - id: script_infos
        type: script_info
        repeat: expr
        repeat-expr: count
  
  script_info:
    seq:
      - id: name_hash
        type: string
      
      - id: unk1
        type: u4
        
      - id: script_idx
        type: u4
        
      - id: unk2
        type: u4
        
      - id: size
        type: u4
        
      - id: unk3
        type: u4
  
  element_desc:
    seq:
      - id: unk1
        type: u4
      - id: element_idx
        type: u4
      - id: unk2
        type: u4
        
  lua_script_data:
    seq:
      - id: len
        type: u4
      - id: data
        size: len
  
  string:
    seq:
      - id: len
        type: s4
      - id: data
        type: str
        size: ((len - 1) / 4 + 1) * 4
