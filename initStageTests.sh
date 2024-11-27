#!/bin/sh

if ! command -v python3 &> /dev/null; then
    echo "[ERROR]: Python 3 is not installed."
    exit 125
fi

if ! mountpoint -q /nfsshare; then
    echo '[ERROR]: /nfsshare folder is not mounted';
    exit 125
fi