#!/bin/sh

binaryTestpath='../testsFolder/secondTest.sh'

ls "$binaryTestpath"
if [ $? -ne 0 ]; then
    echo "binary test $binaryTestpath NOT exist"
    exit
fi

bash "$binaryTestpath"
testRC=$?
exit $testRC