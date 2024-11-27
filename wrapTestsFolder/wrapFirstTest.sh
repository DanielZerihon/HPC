#!/bin/sh

binaryTestpath='../testsFolder/firstTest.sh'

ls "$binaryTestpath"
if [ $? -ne 0 ]; then
    echo "binary test $binaryTestpath NOT exist"
    exit
fi

bash "$binaryTestpath"
testRC=$?
exit $testRC