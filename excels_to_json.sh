#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters! Please pass a path to unobfuscated DummyDlls"
fi

ASSSEMBLY_PATH="$1"
OUT_DIR="JSON_250"
XOR_BYTE="0x95"

for f in OUTPUT/Data/_ExcelBinOutput/*; do 
  X=`echo $f | xargs basename`; 
  cp -v $f test.bin; 
  ./xor.py test.bin ${XOR_BYTE}; 
  mv -v test.bin EBI_Dec/$X.bin; 
  mono DataDumper.exe ${ASSSEMBLY_PATH} EBI_Dec/$X.bin out.json;
  json-glib-format -p out.json > ${OUT_DIR}/$X.json;
  rm out.json;
done
