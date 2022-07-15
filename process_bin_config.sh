#!/bin/bash

DLL_DIR="/home/mihoyo/hk4e_output/2.2.0-Fix/DummyDll"
DATA_DIR="/home/mihoyo/hk4e_output/2.2.0-Fix/Data/_BinOutput"
OUT_DIR="BinData_2850"
XOR_BYTE="0x98"

BINARY="BinDumper.exe"

TEMPDIR=`mktemp -d`

for f in `find ${DATA_DIR} -type f`; do
  #echo $f;
  B=`basename "$f"`
  D=`dirname $f | sed -e "s|${DATA_DIR}||"`
  T=`mktemp -u ${TEMPDIR}/${B}_XXXXXXXXXXXX`

  DATA=(`echo $f | ./get_class_mode.py`)

  CLASS=${DATA[0]}
  MODE=${DATA[1]}

  cp "$f" "$T"
  sync
  ./xor.py $T ${XOR_BYTE} || true
  mkdir -p ${OUT_DIR}/${D}
  mono "${BINARY}" ${DLL_DIR} $T ${OUT_DIR}/${D}/${B}.json $MODE $CLASS
  echo $T ${OUT_DIR}/${D}/${B}.json $MODE $CLASS
  rm $T
done

rm -r ${TEMPDIR}
