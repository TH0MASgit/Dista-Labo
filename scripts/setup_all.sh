#!/bin/bash

# This script can setup the software environment and git repos on a new machine
# (or refresh it on an existing one). You can use it locally or remotely on a
# target machine by passing its ip address as the first (and only) argument.

if [ -z "$1" ] ; then # run remotely (expect to type your password a couple times)
    rsync -av --ignore-existing ~/.ssh/id_ed25519* $1:.ssh/ # use -avu to force update
    ssh $1 'bash -s' <(cat setup_ssh.sh setup_git.sh)
    ssh -t $1 'sudo bash ~/Documents/dista/scripts/setup_env.sh'
else # run locally
    ./setup_ssh.sh #TODO add the server's ip address here to copy its ssh keys
    ./setup_git.sh && ./setup_env.sh
fi

