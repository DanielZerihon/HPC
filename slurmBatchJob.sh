#!/bin/sh
runWrapTestOnNode() {
    local wrapTestName="$1"
    echo
    echo "####"
    echo "HOSTNAME: $HOSTNAME"

    ls "$wrapTestName"
    if [ $? -ne 0 ]; then
        echo "$wrapTestName file NOT exist"
        exit
    fi

    bash "$wrapTestName"
    local testRC=$?

    echo "** wrap Test result: $testRC **"

    if [ $testRC -ne 0 ]; then
        echo "$wrapTestName failed with exit code $testRC."
        echo "DRAINING NODE!"
        # scontrol update nodename="$HOSTNAME" state=drain reason="$wrapTestName failed"
        return $testRC
    fi
}

recordTestResult(){
    local testName="$1"
    local testResult="$2"
    jsonPath="$nodeWorkingDir$HOSTNAME.json"

    if [ -f "$jsonPath" ]; then
        sed -i '$d' "$jsonPath"
        sed -i '$ s/$/,/' "$jsonPath"
    else
        echo "{" > "$jsonPath"
        echo "    \"nodeName\": \"$HOSTNAME\"," >> "$jsonPath"
        echo "    \"date\": \"$(date +%d.%m.%y)\"," >> "$jsonPath"
    fi

    echo "    \"$testName\": \"$testResult\"" >> "$jsonPath"
    echo "}" >> "$jsonPath"
}

sendJsonToElastic(){
    curl -k -u "$elasticUser":"$elasticPassword" https://"$elasticIP":"$elasticPort"/"$elasticNewIndexName"/_doc -XPOST -H 'Content-Type: application/json' -d @$jsonPath
    elasticCommadRESULT=$?
    if [ $elasticCommadRESULT -ne 0 ]; then
        echo "Error: Failed to index document in Elasticsearch. return code: $elasticCommadRESULT"
        exit 1
    fi
}

jsonPath=""
wrapTestFiles='wrapTestsFolder'

# Iterate over the list and run the tests
for testFile in "$wrapTestFiles"/*
do
  if [ -f "$testFile" ]; then
    runWrapTestOnNode "$testFile"
    testReturnCode=$?
    recordTestResult "$testFile" "$testReturnCode"
  fi
done

sendJsonToElastic