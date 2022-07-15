#!/bin/bash

DLL_DIR="/home/mihoyo/hk4e_output/2.2.0-Fix/DummyDll"
DATA_DIR="/home/mihoyo/hk4e_output/2.2.0-Fix/Data/_ExcelBinOutput"
OUT_DIR="ExcelBinData_2850"
XOR_BYTE="0x98"

BINARY="DataDumper.exe"

TEMPDIR=`mktemp -d`

for f in ${IN_DIR}/*; do 
  X=`echo $f | xargs basename`; 
  cp -v $f test.bin; 
  ./xor.py test.bin ${XOR_BYTE}; 
  mv -v test.bin ${TEMPDIR}/$X.bin; 
  mono ${BINARY} ${DLL_DIR} ${TEMPDIR}/$X.bin out.json;
  json-glib-format -p out.json > ${OUT_DIR}/$X.json;
  rm out.json;
done

rm -r ${TEMPDIR}
