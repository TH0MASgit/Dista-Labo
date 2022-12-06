#!/bin/bash

if [ "$1" == "install" ]; then
    sudo apt install sshpass --yes
else
    USERNAME="christian"
    NANO_NUMBER=$1
    SCRIPT=$2
    sshpass -p wertyuiop ssh -X -o StrictHostKeyChecking=accept-new -l ${USERNAME} "192.168.1.${NANO_NUMBER}" "${SCRIPT}"
fi
