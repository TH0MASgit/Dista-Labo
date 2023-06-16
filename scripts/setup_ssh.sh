#!/bin/bash

# You can use this script in one of two ways:
# == Fetch ssh key remotely ==
# 1. Invoke this script using a 'donor' machine's ip address as argument
# 2. Enter the remote (or 'donor') machine's password when prompted
# == Copy key from USB ==
# 1. Copy this script and the .ssh folder to a usb drive
# 2. Plug the usb drive in the target computer and copy this script anywhere
# 3. Make sure the copied script is executable: chmod u+x setup_git.sh
# 4. Launch the script from bash and input your password if prompted


echo "Copying ssh keys ========================================================"
distakey="$HOME/.ssh/id_ed25519"

if [ -f "$distakey" ] ; then
    echo "Using existing ssh key:"
    ssh-keygen -E md5 -lf "$distakey.pub"
elif [ -n "$1" ] ; then # fetch key remotely
    echo "Copying key from $1"
    scp $1:.ssh/id_ed25519\* ~/.ssh/
elif [ -d "/media/$USERNAME/KINGSTON/.ssh" ] ; then # copy from USB
    # (you might have to adjust these paths manually)
    echo "Copying key from KINGSTON/.ssh"
    cp -ri /media/$USERNAME/KINGSTON/.ssh ~/
else
    >&2 echo "Error: ssh key not found!"
    exit 1
fi


echo "Configuring ssh ========================================================="

# Allow for password-less login over ssh:
cat "$distakey.pub" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# No one wants to enter their ssh key's passphrase all the time:
echo -e '\n{ [ -z "$SSH_AUTH_SOCK" ] && eval `ssh-agent -s` ; } >/dev/null' >> ~/.bashrc
echo -e '\n[ -n "$SSH_AUTH_SOCK" ] && eval `ssh-agent -k`' >> ~/.bash_logout
echo -e 'AddKeysToAgent yes' >> ~/.ssh/config
chmod 600 ~/.ssh/config

# Register the new key:
chmod 400 "$distakey" "$distakey.pub"
eval "$(ssh-agent)"
ssh-add "$distakey"

